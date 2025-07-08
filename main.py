

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import configparser
import os
import asyncio
import threading
from scraper import run_scraper, get_channels
from generator import run_generator

class ChannelSelector(tk.Toplevel):
    def __init__(self, parent, channels, callback):
        super().__init__(parent)
        self.title("Select Channels")
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()

        self.channels = channels
        self.callback = callback

        list_frame = ttk.Frame(self, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        for name in sorted(self.channels.keys()):
            self.listbox.insert(tk.END, name)

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X)
        
        add_button = ttk.Button(button_frame, text="Add Selected", command=self.on_add)
        add_button.pack()

    def on_add(self):
        selected_indices = self.listbox.curselection()
        selected_channels = {self.listbox.get(i): self.channels[self.listbox.get(i)] for i in selected_indices}
        self.callback(selected_channels)
        self.destroy()

class CombolistScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Combolist Scraper")
        self.root.geometry("800x600")

        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Main Frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Configuration Frame ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        self.api_id_var = tk.StringVar()
        self.api_hash_var = tk.StringVar()
        self.phone_number_var = tk.StringVar()
        self.channels_var = tk.StringVar()
        self.keywords_var = tk.StringVar()

        ttk.Label(config_frame, text="API ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.api_id_var, width=40).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(config_frame, text="API Hash:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.api_hash_var, width=40).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(config_frame, text="Phone Number:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.phone_number_var, width=40).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(config_frame, text="Channels (name:id, ...):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.channels_var, width=40).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(config_frame, text="Keywords (comma-separated):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.keywords_var, width=40).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)
        
        config_frame.columnconfigure(1, weight=1)

        # --- Control Frame ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.save_button = ttk.Button(control_frame, text="Save Config", command=self.save_config)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.fetch_channels_button = ttk.Button(control_frame, text="Fetch Channels", command=self.fetch_channels_thread)
        self.fetch_channels_button.pack(side=tk.LEFT, padx=5)

        self.start_scraper_button = ttk.Button(control_frame, text="Start Scraper", command=self.start_scraper_thread)
        self.start_scraper_button.pack(side=tk.LEFT, padx=5)

        self.generate_wordlist_button = ttk.Button(control_frame, text="Generate Wordlist", command=self.generate_wordlist)
        self.generate_wordlist_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_session_button = ttk.Button(control_frame, text="Clear Session", command=self.clear_session)
        self.clear_session_button.pack(side=tk.RIGHT, padx=5)

        # --- Log Frame ---
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled', bg='#2b2b2b', fg='white')
        self.log_area.pack(fill=tk.BOTH, expand=True)

        self.load_config()

    def log(self, message):
        def _log():
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.config(state='disabled')
            self.log_area.see(tk.END)
        self.root.after(0, _log)

    def clear_session(self):
        session_file = os.path.join('sessions', 'session.sqlite')
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                self.log("Session file (session.sqlite) deleted. You will need to log in again.")
                messagebox.showinfo("Success", "Session cleared. Please try your action again.")
            except Exception as e:
                self.log(f"Error deleting session file: {e}")
                messagebox.showerror("Error", f"Could not delete session file: {e}")
        else:
            self.log("No session.sqlite file to delete.")
            messagebox.showinfo("Info", "No active session file found.")

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists('config/config.ini'):
            config.read('config/config.ini')
            self.api_id_var.set(config.get('Telegram', 'api_id', fallback=''))
            self.api_hash_var.set(config.get('Telegram', 'api_hash', fallback=''))
            self.phone_number_var.set(config.get('Telegram', 'phone_number', fallback=''))
            
            channels = dict(config['Channels'].items()) if 'Channels' in config else {}
            self.channels_var.set(",".join([f"{name}:{id}" for name, id in channels.items()]))
            
            keywords = config.get('Keywords', 'keywords', fallback='')
            self.keywords_var.set(keywords)
            self.log("Configuration loaded from config.ini")
        else:
            self.log("config.ini not found. Please fill in the configuration details and save.")

    def save_config(self):
        config = configparser.ConfigParser()
        config['Telegram'] = {
            'api_id': self.api_id_var.get(),
            'api_hash': self.api_hash_var.get(),
            'phone_number': self.phone_number_var.get()
        }
        
        try:
            channels_str = self.channels_var.get()
            if channels_str:
                channels_dict = dict(item.split(":") for item in channels_str.replace(" ", "").split(","))
                config['Channels'] = channels_dict
            else:
                config['Channels'] = {}
        except ValueError:
            messagebox.showerror("Error", "Invalid format for Channels. Use name1:id1,name2:id2,...")
            return

        config['Keywords'] = {
            'keywords': self.keywords_var.get()
        }

        if not os.path.exists('config'):
            os.makedirs('config')

        with open('config/config.ini', 'w') as configfile:
            config.write(configfile)
        
        self.log("Configuration saved to config.ini")
        messagebox.showinfo("Success", "Configuration saved successfully!")

    def _get_auth_details(self):
        api_id = self.api_id_var.get()
        api_hash = self.api_hash_var.get()
        phone = self.phone_number_var.get()

        if not all([api_id, api_hash, phone]):
            messagebox.showerror("Error", "API ID, API Hash, and Phone Number are required to fetch channels.")
            return None
        return api_id, api_hash, phone

    def _get_config_and_validate(self):
        auth_details = self._get_auth_details()
        if not auth_details:
            return None
        
        try:
            channels_str = self.channels_var.get()
            channels = dict(item.split(":") for item in channels_str.replace(" ", "").split(",")) if channels_str else {}
        except ValueError:
            messagebox.showerror("Error", "Invalid format for Channels. Use name1:id1,name2:id2,...")
            return None
        
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]

        if not channels or not keywords:
            messagebox.showerror("Error", "Channels and Keywords must be provided.")
            return None
            
        return *auth_details, channels, keywords

    def set_ui_state(self, state):
        for button in [self.start_scraper_button, self.generate_wordlist_button, self.save_button, self.fetch_channels_button, self.clear_session_button]:
            button.config(state=state)

    def fetch_channels_thread(self):
        auth_details = self._get_auth_details()
        if not auth_details:
            return

        self.set_ui_state('disabled')
        
        def task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                channels = loop.run_until_complete(get_channels(*auth_details, self.log))
                self.root.after(0, self.open_channel_selector, channels)
            except Exception as e:
                self.log(f"Error fetching channels: {e}")
                messagebox.showerror("Error", f"Failed to fetch channels: {e}")
            finally:
                loop.close()
                self.root.after(0, self.set_ui_state, 'normal')

        threading.Thread(target=task, daemon=True).start()

    def open_channel_selector(self, channels):
        if not channels:
            messagebox.showinfo("Info", "No channels found or you may need to log in via console.")
            return
        ChannelSelector(self.root, channels, self.on_channels_selected)

    def on_channels_selected(self, selected_channels):
        current_channels_str = self.channels_var.get().strip()
        new_channels_dict = {}

        # If the field is empty, just add the new channels
        if not current_channels_str:
            new_channels_dict = selected_channels
            self.log(f"Added {len(selected_channels)} channels to the list.")
        else:
            # If the field is not empty, ask the user for confirmation
            choice = messagebox.askquestion(
                "Confirm Action",
                "The channels field is not empty.\n\nDo you want to OVERWRITE the existing channels?\n(Choose 'No' to APPEND the new selection.)",
                icon='warning'
            )

            if choice == 'yes':  # Overwrite
                new_channels_dict = selected_channels
                self.log(f"Overwrote existing channels with {len(selected_channels)} new one(s).")
            else:  # Append
                try:
                    current_channels = dict(item.split(":") for item in current_channels_str.replace(" ", "").split(","))
                    current_channels.update(selected_channels)
                    new_channels_dict = current_channels
                    self.log(f"Appended {len(selected_channels)} channels to the list.")
                except ValueError:
                    messagebox.showerror("Error", "The current channel string is malformed. Could not append.")
                    return
        
        self.channels_var.set(",".join([f"{name}:{id}" for name, id in new_channels_dict.items()]))

    def start_scraper_thread(self):
        config = self._get_config_and_validate()
        if not config:
            return

        self.set_ui_state('disabled')
        
        def scraper_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(run_scraper(*config, self.log))
            except Exception as e:
                self.log(f"An error occurred during scraping: {e}")
            finally:
                loop.close()
                self.root.after(0, self.set_ui_state, 'normal')

        threading.Thread(target=scraper_task, daemon=True).start()

    def generate_wordlist(self):
        self.set_ui_state('disabled')
        self.log("Generating wordlist...")
        try:
            run_generator(self.log)
        except Exception as e:
            self.log(f"Error during wordlist generation: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.set_ui_state('normal')

if __name__ == "__main__":
    # This policy is required for Windows to avoid a RuntimeError with asyncio in threads.
    # It should only be set on Windows.
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    root = tk.Tk()
    app = CombolistScraperApp(root)
    root.mainloop()

