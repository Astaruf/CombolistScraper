import os
import codecs

# Verifica se la cartella wordlists esiste, altrimenti la crea
if not os.path.exists("wordlists"):
    os.makedirs("wordlists")

# Rinomina i file new se esistono
if os.path.isfile("wordlists/new_users.txt"):
    if os.path.isfile("wordlists/old_users.txt"):
        os.remove("wordlists/old_users.txt")  # Elimina il file di destinazione se esiste già
    os.rename("wordlists/new_users.txt", "wordlists/old_users.txt")

if os.path.isfile("wordlists/new_passwords.txt"):
    if os.path.isfile("wordlists/old_passwords.txt"):
        os.remove("wordlists/old_passwords.txt")  # Elimina il file di destinazione se esiste già
    os.rename("wordlists/new_passwords.txt", "wordlists/old_passwords.txt")

# Verifica se i file old esistono e stampa un riepilogo
if os.path.isfile("wordlists/old_users.txt") and os.path.isfile("wordlists/old_passwords.txt"):
    with open("wordlists/old_users.txt", "r", encoding="utf-8") as old_users_file:
        total_old_users = sum(1 for line in old_users_file)
        size_old_users = os.path.getsize("wordlists/old_users.txt")

    with open("wordlists/old_passwords.txt", "r", encoding="utf-8") as old_passwords_file:
        total_old_passwords = sum(1 for line in old_passwords_file)
        size_old_passwords = os.path.getsize("wordlists/old_passwords.txt")

    print(f"Hai già un totale di {total_old_users} username ({size_old_users} bytes) e {total_old_passwords} password ({size_old_passwords} bytes).")

# Crea il file new_users.txt con gli username unici
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

# Crea il file new_passwords.txt con le password uniche
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

# Stampare il riepilogo della grandezza dei file new
with open("wordlists/new_users.txt", "r", encoding="utf-8") as new_users_file:
    total_users = sum(1 for line in new_users_file)
    size_users = os.path.getsize("wordlists/new_users.txt")

with open("wordlists/new_passwords.txt", "r", encoding="utf-8") as new_passwords_file:
    total_passwords = sum(1 for line in new_passwords_file)
    size_passwords = os.path.getsize("wordlists/new_passwords.txt")

print(f"Ora hai un totale di {total_users} username ({size_users} bytes) e {total_passwords} password ({size_passwords} bytes).")
