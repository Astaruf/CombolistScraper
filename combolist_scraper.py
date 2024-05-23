import configparser
import os
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import re

# Read configuration from config.ini file
config = configparser.ConfigParser()
config.read('config/config.ini')

api_id = config.get('Telegram', 'api_id')
api_hash = config.get('Telegram', 'api_hash')
phone_number = config.get('Telegram', 'phone_number')
channels = {name: int(id) for name, id in config['Channels'].items()}
keywords = config.get('Keywords', 'keywords').split(',')

# Create the sessions folder if it doesn't exist
session_folder = 'sessions'
if not os.path.exists(session_folder):
    os.makedirs(session_folder)

# Create the client
client = TelegramClient(os.path.join(session_folder, 'session'), api_id, api_hash)

# Function to clean folder names and add the main folder path
def clean_folder_name(channel_name, channel_id, main_folder):
    clean_name = re.sub(r'[<>:"/\\|?*]', '', channel_name)
    return os.path.join(main_folder, f"{clean_name} - {channel_id}")

# Function to check if a file already exists with the same size
def file_exists_with_same_size(directory, file_name, file_size):
    file_path = os.path.join(directory, file_name)
    return os.path.exists(file_path) and os.path.getsize(file_path) == file_size

# Function to generate a new file name if it already exists with different size
def generate_new_file_name(directory, file_name):
    base, ext = os.path.splitext(file_name)
    counter = 1
    new_file_name = f"{base}_{counter}{ext}"
    while os.path.exists(os.path.join(directory, new_file_name)):
        counter += 1
        new_file_name = f"{base}_{counter}{ext}"
    return new_file_name

# Function to check if a word contains exactly the keyword
def contains_exact_keyword(word, keyword):
    return re.search(r'\b' + re.escape(keyword) + r'\b', word, re.IGNORECASE) is not None

# Function to search and download files from all channels
async def search_and_download_files():
    main_folder = "combolists"  # Main folder for downloaded files
    for channel_name, channel_id in channels.items():
        print(f"Searching messages in channel {channel_name} ({channel_id}) with keywords {', '.join(keywords)}...")
        try:
            # Clean the channel folder name
            clean_channel_name = clean_folder_name(channel_name, channel_id, main_folder)
            
            # Create a folder for the channel if it doesn't exist
            if not os.path.exists(clean_channel_name):
                os.makedirs(clean_channel_name)

            channel = await client.get_entity(PeerChannel(channel_id))
            
            offset_id = 0
            files_found = 0
            total_files = 0

            while True:
                history = await client(GetHistoryRequest(
                    peer=channel,
                    limit=100,  # Telegram API limit
                    offset_date=None,
                    offset_id=offset_id,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                if not history.messages:
                    break

                for message in history.messages:
                    if message.media and hasattr(message.media, 'document'):
                        for attribute in message.media.document.attributes:
                            if hasattr(attribute, 'file_name'):
                                file_name = attribute.file_name
                                if any(contains_exact_keyword(file_name, keyword) for keyword in keywords):
                                    total_files += 1
                                    if not file_exists_with_same_size(clean_channel_name, file_name, message.media.document.size):
                                        files_found += 1
                                        break

                offset_id = history.messages[-1].id

            print(f"Found {files_found} new files in channel {channel_name} ({channel_id}).")

            current_file = 1
            offset_id = 0

            while True:
                history = await client(GetHistoryRequest(
                    peer=channel,
                    limit=100,  # Telegram API limit
                    offset_date=None,
                    offset_id=offset_id,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                if not history.messages:
                    break
                
                for message in history.messages:
                    if message.media and hasattr(message.media, 'document'):
                        for attribute in message.media.document.attributes:
                            if hasattr(attribute, 'file_name'):
                                file_name = attribute.file_name
                                file_size = message.media.document.size
                                file_size_mb = file_size / (1024 * 1024)
                                
                                if any(contains_exact_keyword(file_name, keyword) for keyword in keywords):
                                    if file_exists_with_same_size(clean_channel_name, file_name, file_size):
                                        print(f"File {file_name} already downloaded, skipped.")
                                    else:
                                        if os.path.exists(os.path.join(clean_channel_name, file_name)):
                                            new_file_name = generate_new_file_name(clean_channel_name, file_name)
                                            print(f"File {file_name} exists but with different size, downloading as {new_file_name}.")
                                            file_name = new_file_name

                                        print(f"Downloading {current_file}/{files_found} - {file_name} - File Size: {file_size_mb:.2f} MB...")
                                        await client.download_media(message, file=os.path.join(clean_channel_name, file_name))
                                        current_file += 1

                offset_id = history.messages[-1].id

        except Exception as e:
            print(f"[!] Error in channel {channel_name} ({channel_id}): {e}.")

    print("Download complete.")

if __name__ == "__main__":
    # Connect to the client
    client.start(phone_number)
    client.loop.run_until_complete(search_and_download_files())
