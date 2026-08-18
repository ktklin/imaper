"""Module for downloading all email folders and messages via IMAP."""

import imaplib
import os
import re
#from typing import List, Tuple

# Configuration
EMAIL = os.environ.get("EMAIL", "")
PASSWORD =  os.environ.get ("PASSWORD","")
IMAP_SERVER = "imap.goneo.de"
BASE_SAVE_DIRECTORY = "downloaded_emails"


def get_safe_folder_path(folder_name: str) -> str:
    """Create and return a safe local directory path for a folder name."""
    safe_name = folder_name.replace("/", "_").replace("\\", "_")
    folder_path = os.path.join(BASE_SAVE_DIRECTORY, safe_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def parse_folder_name(folder_info: bytes) -> str:
    """Extract and return the folder name from raw IMAP folder info."""
    folder_raw = folder_info.decode()
    match = re.search(r'"([^"]+)"$', folder_raw)
    return match.group(1) if match else ""


def save_email_message(folder_path: str, e_id: bytes, msg_data: list) -> None:
    """Save raw email fetch data to an .eml file."""
    for part in msg_data:
        if isinstance(part, tuple):
            file_name = f"msg_{e_id.decode()}.eml"
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "wb") as file_handle:
                file_handle.write(part[1])


def process_folder(mail: imaplib.IMAP4_SSL, folder_name: str) -> None:
    """Select a folder and download all email messages inside it."""
    print(f"\n--- Processing Folder: {folder_name} ---")
    mail.select(f'"{folder_name}"')
    _, data = mail.search(None, "ALL")

    if not data or not data[0]:
        print(f"Folder '{folder_name}' is empty. Skipping.")
        return

    email_ids = data[0].split()
    folder_path = get_safe_folder_path(folder_name)

    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        save_email_message(folder_path, e_id, msg_data)

    print(f"Successfully downloaded {len(email_ids)} emails from {folder_name}.")


def download_all_folders() -> None:
    """Connect to the IMAP server and iterate through all available folders."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)

        status, folder_list = mail.list()
        if status != "OK" or not folder_list:
            print("Could not retrieve folder list.")
            return

        for folder_info in folder_list:
            if isinstance(folder_info, bytes):
                folder_name = parse_folder_name(folder_info)
                if folder_name:
                    process_folder(mail, folder_name)

        mail.logout()
        print("\nAll folders processed successfully.")

    except (imaplib.IMAP4.error, OSError) as err:
        print(f"An error occurred during IMAP operation or file I/O: {err}")


if __name__ == "__main__":
    download_all_folders()
