"""Archive Gmail inbox conversations whose latest message is older than DAYS_OLD days.

Archiving removes the Inbox label only; nothing is deleted. Uses Gmail IMAP with an
app password and the Python standard library only.

Environment variables:
  GMAIL_ADDRESS       your Gmail address (required)
  GMAIL_APP_PASSWORD  a Google app password (required)
  DAYS_OLD            age threshold in days (default 5)
  SKIP_STARRED        "true" keeps starred mail in the inbox (default true)
  DRY_RUN             "true" only reports what would be archived (default false)
"""
import imaplib
import os
import re
import sys

CHUNK = 500  # UIDs per IMAP command


def env_bool(name, default):
    value = os.environ.get(name) or str(default)
    return value.strip().lower() in ("1", "true", "yes")


def find_all_mail(imap):
    """Return the quoted All Mail folder name (it is localized, so find it by its \\All flag)."""
    _, folders = imap.list()
    for line in folders:
        m = re.match(rb'\((?P<flags>[^)]*)\) (?:"[^"]*"|NIL) (?P<name>.+)$', line)
        if m and b"\\All" in m.group("flags"):
            name = m.group("name").decode()
            return name if name.startswith('"') else f'"{name}"'
    raise RuntimeError("Could not find the All Mail folder")


def search(imap, gmail_query):
    """Search the selected folder with Gmail search syntax; returns a list of UIDs."""
    _, data = imap.uid("SEARCH", "X-GM-RAW", f'"{gmail_query}"')
    return data[0].split() if data and data[0] else []


def thread_ids(imap, uids):
    """Map each UID to its Gmail conversation (thread) id."""
    result = {}
    for i in range(0, len(uids), CHUNK):
        _, data = imap.uid("FETCH", b",".join(uids[i:i + CHUNK]), "(X-GM-THRID)")
        for item in data:
            line = item[0] if isinstance(item, tuple) else item
            if not line:
                continue
            uid = re.search(rb"UID (\d+)", line)
            thr = re.search(rb"X-GM-THRID (\d+)", line)
            if uid and thr:
                result[uid.group(1)] = thr.group(1)
    return result


def main():
    address = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not address or not password:
        sys.exit("GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set (add them as GitHub secrets).")
    days = int(os.environ.get("DAYS_OLD") or 5)
    skip_starred = env_bool("SKIP_STARRED", True)
    dry_run = env_bool("DRY_RUN", False)

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(address, password.replace(" ", ""))

    # 1. Conversations with any message newer than the cutoff (including your own
    #    sent replies) stay in the inbox.
    all_mail = find_all_mail(imap)
    imap.select(all_mail, readonly=True)
    recent_threads = set(thread_ids(imap, search(imap, f"newer_than:{days}d")).values())

    # 2. Old inbox messages, minus those in recently active conversations.
    imap.select("INBOX")
    query = f"older_than:{days}d" + (" -is:starred" if skip_starred else "")
    old = thread_ids(imap, search(imap, query))
    to_archive = [uid for uid, thr in old.items() if thr not in recent_threads]
    kept = {thr for thr in old.values() if thr in recent_threads}

    print(f"{len(to_archive)} message(s) to archive; "
          f"{len(kept)} conversation(s) kept because of recent replies.")

    if dry_run:
        print("DRY_RUN is on - nothing was changed.")
    else:
        # Moving a message from INBOX to All Mail is exactly what Gmail's Archive does.
        for i in range(0, len(to_archive), CHUNK):
            typ, resp = imap.uid("MOVE", b",".join(to_archive[i:i + CHUNK]), all_mail)
            if typ != "OK":
                sys.exit(f"Gmail refused to archive: {resp}")
        left = [u for u in search(imap, query) if u in set(to_archive)]
        if left:
            sys.exit(f"{len(left)} message(s) are still in the inbox after archiving.")
        print(f"Archived {len(to_archive)} message(s).")

    imap.logout()


if __name__ == "__main__":
    main()
