# Combolist Scraper

## Overview
Combolist Scraper is a Python program designed to scrape combolist files from specified Telegram channels based on user-defined keywords. It utilizes the Telethon library to interact with the Telegram API, ensuring efficient and secure data retrieval. The program organizes downloaded files into clean folders and prevents duplicate downloads, providing a seamless user experience.

## Features
- Scrapes combolist files from Telegram channels
- Supports custom keywords for targeted searches
- Organizes downloads into clean folders
- Prevents duplicate downloads by checking file sizes
- Easy setup with a config.ini file

## Requirements
- Python 3.x
- Telethon library

## Installation
1. Clone the repository.
2. Install the required dependencies: `pip install -r requirements.txt`.
3. Configure the `config.ini` file with your Telegram API credentials and channel details.

### Configuration - config.ini
- **Telegram API Credentials**: Obtain API ID, API hash, and phone number from Telegram (https://my.telegram.org/auth).
- **Channels**: Specify the channels ID to scrape combolists from.
- **Keywords**: Define keywords for targeted searches.

## Usage
1. Run the program: `python combolist_scraper.py` to create a Telegram session and wait for the combolists download process to complete.
2. Find downloaded combolists in the respective channel folders within the `combolists` directory.
3. Optional: Use `wordlist_generator.py` to merge unique results and create new wordlists of usernames and passwords.

# DISCLAIMER
Downloading data leaks without the consent of the data owner is illegal!

## Contributing
Contributions are welcome! Feel free to open issues or pull requests for any improvements or bug fixes.

## License
This project is licensed under the [MIT License](LICENSE).
