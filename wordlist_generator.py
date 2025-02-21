import os
import codecs

# Check if the 'wordlists' folder exists, otherwise create it
if not os.path.exists("wordlists"):
    os.makedirs("wordlists")

# Rename the 'new' files if they exist
if os.path.isfile("wordlists/new_users.txt"):
    if os.path.isfile("wordlists/old_users.txt"):
        os.remove("wordlists/old_users.txt")  # Delete the destination file if it already exists
    os.rename("wordlists/new_users.txt", "wordlists/old_users.txt")

if os.path.isfile("wordlists/new_passwords.txt"):
    if os.path.isfile("wordlists/old_passwords.txt"):
        os.remove("wordlists/old_passwords.txt")  # Delete the destination file if it already exists
    os.rename("wordlists/new_passwords.txt", "wordlists/old_passwords.txt")

# Check if the 'old' files exist and print a summary
if os.path.isfile("wordlists/old_users.txt") and os.path.isfile("wordlists/old_passwords.txt"):
    with open("wordlists/old_users.txt", "r", encoding="utf-8") as old_users_file:
        total_old_users = sum(1 for line in old_users_file)
        size_old_users = os.path.getsize("wordlists/old_users.txt")

    with open("wordlists/old_passwords.txt", "r", encoding="utf-8") as old_passwords_file:
        total_old_passwords = sum(1 for line in old_passwords_file)
        size_old_passwords = os.path.getsize("wordlists/old_passwords.txt")

    print(f"You already have a total of {total_old_users} usernames ({size_old_users} bytes) and {total_old_passwords} passwords ({size_old_passwords} bytes).")

# Create the 'new_users.txt' file with unique usernames
with open("wordlists/new_users.txt", "w", encoding="utf-8") as new_users_file:
    for root, dirs, files in os.walk("combolists"):
        for file_name in files:
            with codecs.open(os.path.join(root, file_name), "r", encoding="utf-8", errors="ignore") as combo_file:
                for line in combo_file:
                    try:
                        username = line.split(":")[0]
                        new_users_file.write(username + "\n")
                    except IndexError:
                        pass

# Create the 'new_passwords.txt' file with unique passwords
with open("wordlists/new_passwords.txt", "w", encoding="utf-8") as new_passwords_file:
    for root, dirs, files in os.walk("combolists"):
        for file_name in files:
            with codecs.open(os.path.join(root, file_name), "r", encoding="utf-8", errors="ignore") as combo_file:
                for line in combo_file:
                    try:
                        password = line.split(":")[1].strip()
                        new_passwords_file.write(password + "\n")
                    except IndexError:
                        pass

# Print a summary of the size of the 'new' files
with open("wordlists/new_users.txt", "r", encoding="utf-8") as new_users_file:
    total_users = sum(1 for line in new_users_file)
    size_users = os.path.getsize("wordlists/new_users.txt")

with open("wordlists/new_passwords.txt", "r", encoding="utf-8") as new_passwords_file:
    total_passwords = sum(1 for line in new_passwords_file)
    size_passwords = os.path.getsize("wordlists/new_passwords.txt")

print(f"Now you have a total of {total_users} usernames ({size_users} bytes) and {total_passwords} passwords ({size_passwords} bytes).")
