/**
 * Gmail Auto-Archive
 * Archives inbox conversations whose most recent message is older than DAYS_OLD.
 * Archiving only removes the "Inbox" label - nothing is deleted.
 */

// ---- Settings ---------------------------------------------------------------
const DAYS_OLD = 5;           // archive conversations older than this many days
const SKIP_STARRED = true;    // leave starred conversations in the inbox
const SKIP_IMPORTANT = false; // leave conversations marked "important" in the inbox
const SKIP_UNREAD = false;    // leave unread conversations in the inbox
const BATCH_SIZE = 100;       // Gmail allows at most 100 threads per call
const MAX_RUNTIME_MS = 5 * 60 * 1000; // stop before the 6-min Apps Script limit
// -----------------------------------------------------------------------------

/** Main job - run by the time-based trigger. */
function archiveOldInbox() {
  const start = Date.now();
  const cutoff = new Date(start - DAYS_OLD * 24 * 60 * 60 * 1000);

  let query = `in:inbox older_than:${DAYS_OLD}d`;
  if (SKIP_STARRED) query += ' -is:starred';
  if (SKIP_IMPORTANT) query += ' -is:important';
  if (SKIP_UNREAD) query += ' -is:unread';

  let archived = 0;
  let skipped = 0;
  let offset = 0; // skips threads we decided to keep, so we don't re-fetch them forever

  while (Date.now() - start < MAX_RUNTIME_MS) {
    const threads = GmailApp.search(query, offset, BATCH_SIZE);
    if (threads.length === 0) break;

    // Gmail search matches a thread if ANY message is old enough. Only archive
    // threads whose LATEST message is past the cutoff, so a fresh reply on an
    // old conversation stays in the inbox.
    const toArchive = threads.filter(t => t.getLastMessageDate() < cutoff);
    const kept = threads.length - toArchive.length;

    if (toArchive.length > 0) GmailApp.moveThreadsToArchive(toArchive);
    archived += toArchive.length;
    skipped += kept;
    offset += kept; // archived threads leave the result set; kept ones don't

    if (threads.length < BATCH_SIZE) break;
  }

  console.log(`Archived ${archived} conversation(s); kept ${skipped} with recent replies.`);
}

/** Run ONCE to schedule archiveOldInbox every hour. */
function installTrigger() {
  removeTriggers();
  ScriptApp.newTrigger('archiveOldInbox').timeBased().everyHours(1).create();
  console.log('Installed hourly trigger for archiveOldInbox.');
}

/** Run to stop the automation. */
function removeTriggers() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'archiveOldInbox')
    .forEach(t => ScriptApp.deleteTrigger(t));
}

/** Dry run: logs what WOULD be archived without changing anything. */
function preview() {
  const cutoff = new Date(Date.now() - DAYS_OLD * 24 * 60 * 60 * 1000);
  let query = `in:inbox older_than:${DAYS_OLD}d`;
  if (SKIP_STARRED) query += ' -is:starred';
  if (SKIP_IMPORTANT) query += ' -is:important';
  if (SKIP_UNREAD) query += ' -is:unread';
  const threads = GmailApp.search(query, 0, 50).filter(t => t.getLastMessageDate() < cutoff);
  threads.forEach(t => console.log(`${t.getLastMessageDate().toISOString().slice(0, 10)}  ${t.getFirstMessageSubject()}`));
  console.log(`${threads.length} conversation(s) shown (first 50 max).`);
}
