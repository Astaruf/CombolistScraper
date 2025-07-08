
import asyncio
import os
import re
from telethon import TelegramClient
from telethon.tl.types import PeerChannel
from telethon.tl.functions.messages import GetHistoryRequest

from telethon.sessions import SQLiteSession
from telethon.errors import SessionPasswordNeededError

class TelegramScraper:
    def __init__(self, api_id, api_hash, phone_number, log_callback):
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.log = log_callback
        
        session_folder = 'sessions'
        if not os.path.exists(session_folder):
            os.makedirs(session_folder)
        
        session_path = os.path.join(session_folder, 'session.sqlite')
        self.client = TelegramClient(SQLiteSession(session_path), self.api_id, self.api_hash)

    async def _ensure_connected(self):
        if not self.client.is_connected():
            await self.client.connect()

        if not await self.client.is_user_authorized():
            self.log("First run or session expired. Please check the console to log in.")
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input("Enter Telegram code: "))
            except SessionPasswordNeededError:
                self.log("Two-step verification is enabled. Please enter your password in the console.")
                await self.client.sign_in(password=input("Enter 2FA password: "))
            except Exception as e:
                self.log(f"Error during sign in: {e}")
                raise

    async def list_channels(self):
        self.log("Fetching channel list...")
        await self._ensure_connected()
        
        channels = {}
        async for dialog in self.client.iter_dialogs():
            if dialog.is_channel:
                channels[dialog.name] = dialog.id
        
        self.log(f"Found {len(channels)} channels.")
        await self.client.disconnect()
        return channels

    async def scrape(self, channels, keywords):
        self.log("Connecting to Telegram...")
        await self._ensure_connected()
        self.log("Connection successful.")

        main_folder = "combolists"
        if not os.path.exists(main_folder):
            os.makedirs(main_folder)

        for channel_name, channel_id in channels.items():
            self.log(f"Searching in channel {channel_name} ({channel_id}) for keywords: {', '.join(keywords)}...")
            try:
                clean_channel_name = self._clean_folder_name(channel_name, channel_id, main_folder)
                if not os.path.exists(clean_channel_name):
                    os.makedirs(clean_channel_name)

                channel = await self.client.get_entity(PeerChannel(int(channel_id)))
                
                async for message in self.client.iter_messages(channel):
                    if message.media and hasattr(message.media, 'document'):
                        file_name = self._get_file_name(message)
                        if file_name and any(self._contains_exact_keyword(file_name, keyword) for keyword in keywords):
                            file_size = message.media.document.size
                            if self._file_exists_with_same_size(clean_channel_name, file_name, file_size):
                                self.log(f"File {file_name} already downloaded, skipped.")
                            else:
                                final_file_name = file_name
                                if os.path.exists(os.path.join(clean_channel_name, file_name)):
                                    final_file_name = self._generate_new_file_name(clean_channel_name, file_name)
                                    self.log(f"File {file_name} exists with different size, downloading as {final_file_name}.")
                                
                                file_size_mb = file_size / (1024 * 1024)
                                self.log(f"Downloading {final_file_name} - Size: {file_size_mb:.2f} MB...")
                                await self.client.download_media(message, file=os.path.join(clean_channel_name, final_file_name))

            except Exception as e:
                self.log(f"[!] Error in channel {channel_name} ({channel_id}): {e}")
        
        self.log("Download complete.")
        await self.client.disconnect()

    def _get_file_name(self, message):
        if hasattr(message.media, 'document'):
            for attribute in message.media.document.attributes:
                if hasattr(attribute, 'file_name'):
                    return attribute.file_name
        return None

    def _clean_folder_name(self, channel_name, channel_id, main_folder):
        clean_name = re.sub(r'[<>:"/\\|?*]', '', channel_name)
        return os.path.join(main_folder, f"{clean_name} - {channel_id}")

    def _file_exists_with_same_size(self, directory, file_name, file_size):
        file_path = os.path.join(directory, file_name)
        return os.path.exists(file_path) and os.path.getsize(file_path) == file_size

    def _generate_new_file_name(self, directory, file_name):
        base, ext = os.path.splitext(file_name)
        counter = 1
        new_file_name = f"{base}_{counter}{ext}"
        while os.path.exists(os.path.join(directory, new_file_name)):
            counter += 1
            new_file_name = f"{base}_{counter}{ext}"
        return new_file_name

    def _contains_exact_keyword(self, word, keyword):
        return re.search(r'\b' + re.escape(keyword) + r'\b', word, re.IGNORECASE) is not None

async def run_scraper(api_id, api_hash, phone_number, channels, keywords, log_callback):
    scraper = TelegramScraper(api_id, api_hash, phone_number, log_callback)
    await scraper.scrape(channels, keywords)

async def get_channels(api_id, api_hash, phone_number, log_callback):
    scraper = TelegramScraper(api_id, api_hash, phone_number, log_callback)
    return await scraper.list_channels()

if __name__ == '__main__':
    print("This module is not meant to be run directly. Import it in your main application.")
