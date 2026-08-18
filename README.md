# IMAP Email Downloader

A small Python script that connects to an IMAP mail server, walks through **every** folder in the account, and saves each message to disk as an `.eml` file. It mirrors your server-side folder structure into a local directory tree, so you end up with a browsable, portable backup of your mailbox.

## What it does

1. Connects to your mail host over IMAP (SSL).
2. Lists all folders in the account (INBOX, Sent, Drafts, custom labels, etc.).
3. For each folder, creates a matching local subdirectory under `downloaded_emails/`.
4. Downloads every message in that folder in raw `RFC822` form and writes it as `msg_<id>.eml`.

Each `.eml` file is a complete, standard email (headers + body + attachments) that can be opened in most email clients (Thunderbird, Apple Mail, Outlook) or parsed with Python's `email` module.

## Requirements

- Python 3.6+
- No third-party packages — the script uses only the standard library (`imaplib`, `os`, `re`).

## Configuration

Open the script and edit the configuration block near the top:

| Variable | Description | Example |
| --- | --- | --- |
| `EMAIL` | Your full email address / login | `you@example.com` |
| `PASSWORD` | Your mailbox password or app-specific password | `••••••••` |
| `IMAP_SERVER` | Your provider's IMAP hostname | `imap.mailhoster.com` |
| `FOLDER_NAME` | Reserved for single-folder use (not used by the all-folders download) | `INBOX` |
| `SAVE_DIRECTORY` / `BASE_SAVE_DIRECTORY` | Root directory for saved emails | `downloaded_emails` |

> **Security note:** Credentials are stored in plain text in the script. Do not commit the script with real credentials. Prefer an [app-specific password](https://support.google.com/accounts/answer/185833) where your provider supports one, and consider reading credentials from environment variables instead (see [Suggested improvements](#suggested-improvements)).

### Common IMAP servers

| Provider | IMAP server | Port |
| --- | --- | --- |
| Gmail | `imap.gmail.com` | 993 |
| Outlook / Office 365 | `outlook.office365.com` | 993 |
| iCloud | `imap.mail.me.com` | 993 |
| Yahoo | `imap.mail.yahoo.com` | 993 |

Most providers use SSL on port 993, which is what `IMAP4_SSL` uses by default.

## Usage

```bash
python download_emails.py
```

While running, the script prints progress per folder:

```
--- Processing Folder: INBOX ---
Successfully downloaded 214 emails from INBOX.

--- Processing Folder: Sent ---
Successfully downloaded 88 emails from Sent.

All folders processed successfully.
```

## Output structure

```
downloaded_emails/
├── INBOX/
│   ├── msg_1.eml
│   ├── msg_2.eml
│   └── ...
├── Sent/
│   ├── msg_1.eml
│   └── ...
└── Archive_2024/          # server "Archive/2024" → slashes replaced with "_"
    └── ...
```

Folder names containing `/` or `\` have those characters replaced with `_` so they map cleanly to a single local directory on Windows, macOS, and Linux.

## How it works

- `mail.list()` returns each folder as a raw string like `(\HasNoChildren) "/" "INBOX"`. A regex extracts the folder name from the final quoted segment.
- `mail.select()` opens each folder, and `mail.search(None, "ALL")` returns the IDs of every message in it.
- `mail.fetch(e_id, "(RFC822)")` retrieves the full raw message, which is written straight to disk.

## Limitations & notes

- **Message IDs are per-folder.** The `msg_<id>.eml` numbering restarts in each folder, so filenames are only unique within a folder, not globally.
- **Re-running overwrites.** Running the script again re-downloads everything and overwrites existing files; it does not do incremental syncs.
- **No throttling.** Very large mailboxes are downloaded in one pass, which can be slow and may hit provider rate limits.
- **Empty folders are skipped** with a printed message.

## Disclaimer

Use this only on mailboxes you own or are authorized to access. Downloaded emails may contain sensitive personal data — store the output directory securely.
