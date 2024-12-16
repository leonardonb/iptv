import tkinter as tk
from tkinter import filedialog, messagebox
from pyvirtualdisplay import Display
import requests
import vlc
import json
import os


os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')

try:
    instance = vlc.Instance()
    print("VLC instance created successfully.")
except Exception as e:
    print(f"Error: {e}")
    
instance = vlc.Instance(['--plugin-path=/usr/lib/x86_64-linux-gnu/vlc/plugins'])

class M3UPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M3U Player")
        self.root.geometry("800x600")

        # Player VLC
        self.player = instance.media_player_new()

        # Lista de canais e favoritos
        self.channels = []
        self.all_channels = []  # Lista completa dos canais carregados
        self.favorites = self.load_favorites()

        # Interface
        self.create_widgets()

    def create_widgets(self):
        # Input de arquivo local
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10)

        tk.Label(file_frame, text="Arquivo Local:").pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Selecionar", command=self.load_file).pack(side=tk.LEFT, padx=5)

        # Input de URL
        url_frame = tk.Frame(self.root)
        url_frame.pack(pady=10)

        self.url_entry = tk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(url_frame, text="Carregar URL", command=self.load_url).pack(side=tk.LEFT, padx=5)

        # Lista de canais
        self.channel_listbox = tk.Listbox(self.root, height=15, width=50)
        self.channel_listbox.pack(pady=10)
        self.channel_listbox.bind("<Double-1>", self.play_selected_channel)

        # Botões de controle
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        tk.Button(control_frame, text="Favoritar", command=self.favorite_channel).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Desfavoritar", command=self.unfavorite_channel).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Mostrar Favoritos", command=self.display_favorites).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Mostrar Todos os Canais", command=self.show_all_channels).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Parar", command=self.stop_player).pack(side=tk.LEFT, padx=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("M3U Files", "*.m3u")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.channels = self.parse_m3u(content)
            self.all_channels = self.channels.copy()
            self.display_channels(self.channels)

    def load_url(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Erro", "Digite uma URL válida.")
            return

        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.text
            self.channels = self.parse_m3u(content)
            self.all_channels = self.channels.copy()
            self.display_channels(self.channels)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar URL: {e}")

    def show_all_channels(self):
        """Restaura a lista completa de canais."""
        self.channels = self.all_channels.copy()
        self.display_channels(self.channels)

    def favorite_channel(self):
        selected_index = self.channel_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Erro", "Selecione um canal para favoritar.")
            return

        channel = self.channels[selected_index[0]]
        if channel not in self.favorites:
            self.favorites.append(channel)
            self.save_favorites()
            messagebox.showinfo("Favoritos", f"Canal '{channel['name']}' adicionado aos favoritos.")

    def unfavorite_channel(self):
        selected_index = self.channel_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Erro", "Selecione um canal para desfavoritar.")
            return

        channel = self.channels[selected_index[0]]
        if channel in self.favorites:
            self.favorites.remove(channel)
            self.save_favorites()
            messagebox.showinfo("Favoritos", f"Canal '{channel['name']}' removido dos favoritos.")
            self.display_channels(self.favorites)

    def display_favorites(self):
        self.channels = self.favorites
        self.display_channels(self.favorites)

    def parse_m3u(self, content):
        lines = content.split("\n")
        channels = []
        current_channel = {}

        for line in lines:
            if line.startswith("#EXTINF:"):
                current_channel["name"] = line.split(",")[1]
            elif line.startswith("http"):
                current_channel["url"] = line.strip()
                channels.append(current_channel)
                current_channel = {}

        return channels

    def display_channels(self, channels):
        self.channel_listbox.delete(0, tk.END)
        for channel in channels:
            self.channel_listbox.insert(tk.END, channel["name"])

    def play_selected_channel(self, event):
        selected_index = self.channel_listbox.curselection()
        if not selected_index:
            return

        channel = self.channels[selected_index[0]]
        self.play_channel(channel["url"])

    def play_channel(self, url):
        self.player.set_media(vlc.Media(url))
        self.player.play()

    def stop_player(self):
        self.player.stop()

    def load_favorites(self):
        if os.path.exists("favorites.json"):
            with open("favorites.json", "r") as f:
                return json.load(f)
        return []

    def save_favorites(self):
        with open("favorites.json", "w") as f:
            json.dump(self.favorites, f)


if __name__ == "__main__":
    root = tk.Tk()
    app = M3UPlayerApp(root)
    root.mainloop()