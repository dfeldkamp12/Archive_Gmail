# Gmail Auto-Archive

Automatically archives Gmail inbox conversations once their latest message is
more than **5 days** old. Archived mail is not deleted. It stays in **All Mail**
and in search results.

Runs as a Google Apps Script on Google's servers, hourly, for free.

## Setup (about 3 minutes)

1. Go to <https://script.google.com> and click **New project**. Name it "Gmail Auto-Archive".
2. Replace the contents of `Code.gs` with this repo's `Code.gs`.
3. (Optional) Click ⚙️ **Project Settings**, check *Show "appsscript.json"*, and paste in `appsscript.json`.
4. In the function dropdown pick **`preview`** and click **Run**. Approve the permissions
   (Google will warn "unverified app". This is your own script, so click *Advanced → Go to project*).
   The log lists what would be archived.
5. Pick **`installTrigger`** and click **Run**. The script now runs every hour.

The first run on a large inbox may take a few hourly runs to catch up (each run is capped at about 5 minutes).

## Settings (top of `Code.gs`)

| Setting | Default | Meaning |
|---|---|---|
| `DAYS_OLD` | `5` | Age threshold in days |
| `SKIP_STARRED` | `true` | Never archive starred conversations |
| `SKIP_IMPORTANT` | `false` | Never archive "important" conversations |
| `SKIP_UNREAD` | `false` | Never archive unread conversations |

## Stop it

Run **`removeTriggers`**, or delete the trigger under ⏰ **Triggers** in the left sidebar.
