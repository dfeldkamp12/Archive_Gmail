# Archive Gmail

Automatically archives Gmail inbox conversations once their latest message is more
than **5 days** old. It runs every hour as a GitHub Actions workflow. Archived mail is
not deleted; it stays in **All Mail** and in search.

- Starred conversations are never archived.
- A conversation with a reply in the last 5 days (including your own) stays in the inbox.

## Setup (one time)

### 1. Create a Google app password
App passwords require **2-Step Verification** on your Google account.

1. Go to <https://myaccount.google.com/apppasswords>.
2. Enter a name such as `Archive Gmail` and tap **Create**.
3. Copy the 16-character password. You'll only see it once.

### 2. Add two GitHub secrets
In this repo, go to **Settings → Secrets and variables → Actions → New repository secret**:

| Name | Value |
|---|---|
| `GMAIL_ADDRESS` | your Gmail address |
| `GMAIL_APP_PASSWORD` | the app password from step 1 |

### 3. Test it
Go to **Actions → Archive Gmail → Run workflow**. "Dry run" is checked by default, so
the run only reports how many messages it *would* archive. Check the log, then run it
again with "Dry run" unchecked to archive for real.

After that it runs on its own every hour.

## Settings
Edit `.github/workflows/archive-gmail.yml`:

- `DAYS_OLD`: age threshold in days
- `SKIP_STARRED`: `"false"` to archive starred mail too
- `cron`: how often it runs

## Stop it
Go to **Actions → Archive Gmail → ⋯ → Disable workflow**. You can also revoke the app
password at <https://myaccount.google.com/apppasswords>.

## Notes
- GitHub pauses scheduled workflows in a **public** repo after 60 days without commits.
  If that happens, re-enable the workflow on the Actions page.
- Private repos get 2,000 free Actions minutes a month. Hourly runs use about 720.
