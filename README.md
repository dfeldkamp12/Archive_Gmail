# Archive Gmail

Automatically archives Gmail inbox conversations once their latest message is more
than **5 days** old. It runs every hour (at 17 minutes past) as a GitHub Actions
workflow. Archived mail is not deleted; it stays in **All Mail** and in search.

- Starred conversations are never archived. Star something to keep it in the inbox.
- A conversation with a message in the last 5 days (including your own reply) stays in the inbox.

## How it works
`archive_gmail.py` signs in to Gmail over IMAP with an app password and:

1. Finds conversations with any message newer than 5 days and leaves them alone.
2. Finds the remaining inbox messages older than 5 days (skipping starred ones).
3. Moves them from the Inbox to All Mail, which is exactly what Gmail's **Archive** button does.
4. Checks the inbox again and fails the run if anything didn't move, so a problem shows
   up as a red ✗ on the Actions page (and GitHub emails you) instead of failing silently.

It uses only the Python standard library, so there's nothing to install.

## Setup (one time)

### 1. Turn on 2-Step Verification
Signed in to the Gmail account you want to clean up, go to
<https://myaccount.google.com/signinoptions/twosv> and turn it on. Google only offers
app passwords once 2-Step Verification is on.

### 2. Create a Google app password
1. Go to <https://myaccount.google.com/apppasswords> (same account).
2. Enter a name such as `Archive Gmail` and tap **Create**.
3. Copy the 16-character password. You'll only see it once. Spaces don't matter.

### 3. Add two GitHub secrets
Use a web browser for this step. The GitHub iOS/Android app can't edit secrets.
Open <https://github.com/dfeldkamp12/archive_gmail/settings/secrets/actions> and tap
**New repository secret** for each:

| Name | Value |
|---|---|
| `GMAIL_ADDRESS` | your Gmail address |
| `GMAIL_APP_PASSWORD` | the app password from step 2 |

### 4. Test it
Go to **Actions → Archive Gmail → Run workflow**. This works in the GitHub app too.
"Dry run" is checked by default, so the run only reports how many messages it *would*
archive. Open the run and check the "Archive inbox mail older than 5 days" step, then
run it again with "Dry run" unchecked to archive for real.

After that it runs on its own every hour.

## Settings
Edit `.github/workflows/archive-gmail.yml`:

- `DAYS_OLD`: age threshold in days
- `SKIP_STARRED`: `"false"` to archive starred mail too
- `cron`: how often it runs (times are in UTC)

## Troubleshooting

| What you see | Fix |
|---|---|
| `AUTHENTICATIONFAILED Invalid credentials` in the run log | The app password is wrong, or it was created on a different Google account. Create a new one on the right account and update `GMAIL_APP_PASSWORD`. |
| "The setting you are looking for is not available for your account" on the app passwords page | 2-Step Verification is off. Turn it on (setup step 1) and try again. |
| `GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set` | One of the secrets is missing or misspelled. Names must match exactly. |
| `message(s) are still in the inbox after archiving` | Gmail didn't accept the move. Re-run the workflow. If it keeps happening, check the log for details. |

## Stop it
Go to **Actions → Archive Gmail → ⋯ → Disable workflow**. You can also revoke the app
password at <https://myaccount.google.com/apppasswords>, which immediately cuts off access.

## Notes
- GitHub pauses scheduled workflows in a **public** repo after 60 days without commits.
  If that happens, re-enable the workflow on the Actions page.
- Private repos get 2,000 free Actions minutes a month. Hourly runs use about 720.
