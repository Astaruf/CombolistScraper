

import os
import codecs

class WordlistGenerator:
    def __init__(self, log_callback):
        self.log = log_callback
        self.combolists_dir = "combolists"
        self.wordlists_dir = "wordlists"

    def generate(self):
        self.log("Starting wordlist generation...")
        if not os.path.exists(self.combolists_dir):
            self.log(f"Error: Directory '{self.combolists_dir}' not found.")
            return

        if not os.path.exists(self.wordlists_dir):
            os.makedirs(self.wordlists_dir)
            self.log(f"Created directory: {self.wordlists_dir}")

        self._rename_old_files()
        self._log_old_summary()

        users = set()
        passwords = set()

        self.log("Reading combolist files...")
        for root, _, files in os.walk(self.combolists_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self.log(f"Processing file: {file_path}")
                with codecs.open(file_path, "r", encoding="utf-8", errors="ignore") as combo_file:
                    for line in combo_file:
                        parts = line.strip().split(':')
                        if len(parts) >= 2:
                            users.add(parts[0])
                            passwords.add(":".join(parts[1:]))

        new_users_path = os.path.join(self.wordlists_dir, "new_users.txt")
        new_passwords_path = os.path.join(self.wordlists_dir, "new_passwords.txt")

        self._write_set_to_file(users, new_users_path)
        self._write_set_to_file(passwords, new_passwords_path)

        self.log("\n--- Generation Summary ---")
        self.log(f"Total unique usernames found: {len(users)}")
        self.log(f"Total unique passwords found: {len(passwords)}")
        self.log(f"New usernames saved to: {new_users_path}")
        self.log(f"New passwords saved to: {new_passwords_path}")
        self.log("Wordlist generation complete.")

    def _write_set_to_file(self, data_set, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            for item in sorted(list(data_set)):
                f.write(item + "\n")

    def _rename_old_files(self):
        for f_type in ["users", "passwords"]:
            new_file = os.path.join(self.wordlists_dir, f"new_{f_type}.txt")
            old_file = os.path.join(self.wordlists_dir, f"old_{f_type}.txt")
            if os.path.isfile(new_file):
                if os.path.isfile(old_file):
                    os.remove(old_file)
                os.rename(new_file, old_file)
                self.log(f"Renamed {new_file} to {old_file}")

    def _log_old_summary(self):
        old_users_path = os.path.join(self.wordlists_dir, "old_users.txt")
        old_passwords_path = os.path.join(self.wordlists_dir, "old_passwords.txt")

        if os.path.isfile(old_users_path) and os.path.isfile(old_passwords_path):
            with open(old_users_path, "r", encoding="utf-8") as f:
                total_old_users = sum(1 for _ in f)
            with open(old_passwords_path, "r", encoding="utf-8") as f:
                total_old_passwords = sum(1 for _ in f)
            self.log("\n--- Previous Wordlists ---")
            self.log(f"Found {total_old_users} usernames in old_users.txt")
            self.log(f"Found {total_old_passwords} passwords in old_passwords.txt")
            self.log("--------------------------\n")

def run_generator(log_callback):
    generator = WordlistGenerator(log_callback)
    generator.generate()

if __name__ == '__main__':
    print("This module is not meant to be run directly. Import it in your main application.")

