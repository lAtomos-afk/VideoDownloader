import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os
import sys
import threading
import shutil
import json
import re
import webbrowser
from datetime import datetime

ctk.set_default_color_theme("green")

class WindowsVideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x750")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        self.root.title("Video Downloader v3.0")
        
        self.color_bg = ("#F2F2F2", "#000000")
        self.color_panel = ("#FFFFFF", "#111111")
        self.color_text = ("#000000", "#FFFFFF")
        self.color_entry_bg = ("#FFFFFF", "#000000")
        self.color_border = ("#D0D0D0", "#333333")
        
        self.color_accent = "#2ecc71"       
        self.color_accent_hover = "#27ae60" 

        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, "AppData", "Local", "VideoDownloader")
        
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.history_file = os.path.join(self.config_dir, "history.json")
        
        self.config = {"lang": "es", "show_startup_msg": True, "theme_mode": "System"}
        self.cargar_configuracion()
        
        ctk.set_appearance_mode(self.config["theme_mode"])
        self.root.configure(fg_color=self.color_bg)
        
        self.ruta_destino = tk.StringVar()
        self.ruta_destino.set(os.path.join(self.home_dir, "Downloads"))
        
        self.tipo_var = tk.StringVar(value="Audio")
        self.formato_var = tk.StringVar(value="mp3")
        self.calidad_var = tk.StringVar(value="320 kbps")

        self.rows = []
        self.active_bar = None
        self.active_status = None

        self.textos_dict = {
            "es": {
                "title": "Video Downloader",
                "subtitle": "v3.0",
                "save_in": "Guardar en:",
                "browse": "Examinar",
                "config_group": "Configuración de Descarga",
                "mode": "Modo:",
                "audio_only": "Solo Audio",
                "video_audio": "Video + Audio",
                "format": "Formato:",
                "quality": "Calidad:",
                "instructions": "⬇ Pega los enlaces abajo (Enter para agregar más)",
                "btn_download": "INICIAR DESCARGA",
                "status_ready": "Listo para descargar",
                "settings": "Ajustes",
                "history": "Historial",
                "about": "Sobre Mí",
                "created_by": "SirAtomos | Linux Edition",
                "msg_success": "¡Descargas completadas!",
                "btn_clear": "Limpiar Historial",
                "col_date": "Fecha",
                "col_name": "Nombre",
                "col_format": "Formato",
                "aviso_title": "Aviso Importante",
                "aviso_body": "¡Bienvenido a la v3.0!\n\nSi compartes esta herramienta,\nrecuerda dar créditos a: SirAtomos.",
                "chk_nomore": "No mostrar de nuevo",
                "btn_ok": "Entendido",
                "error_ffmpeg": "FFmpeg no encontrado.\n\nPara instalarlo, abre PowerShell como Admin y ejecuta:\nwinget install ffmpeg\n\nO descárgalo manualmente de gyan.dev",
                "lbl_lang": "Idioma / Language",
                "lbl_theme": "Apariencia / Appearance",
                "switch_dark": "Modo Oscuro",
                "btn_save_restart": "Guardar y Reiniciar",
                "alert_playlist_title": "Playlist Detectada",
                "alert_playlist_msg": "Este enlace es una Playlist o Radio.\nSe descargarán MÚLTIPLES videos.\n\n¿Estás seguro de continuar?",
                "about_title": "Sobre el Creador",
                "about_desc": "Desarrollado con ❤️ por SirAtomos.\n¡Sígueme en mis redes!"
            },
            "en": {
                "title": "Video Downloader",
                "subtitle": "v3.0",
                "save_in": "Save to:",
                "browse": "Browse",
                "config_group": "Download Settings",
                "mode": "Mode:",
                "audio_only": "Audio Only",
                "video_audio": "Video + Audio",
                "format": "Format:",
                "quality": "Quality:",
                "instructions": "⬇ Paste links below (Press Enter to add row)",
                "btn_download": "START DOWNLOAD",
                "status_ready": "Ready to download",
                "settings": "Settings",
                "history": "History",
                "about": "About Me",
                "created_by": "SirAtomos | Linux Edition",
                "msg_success": "Downloads completed!",
                "btn_clear": "Clear History",
                "col_date": "Date",
                "col_name": "Name",
                "col_format": "Format",
                "aviso_title": "Important Notice",
                "aviso_body": "Welcome to v3.0!\n\nIf you share this tool, please\ncredit the creator: SirAtomos.",
                "chk_nomore": "Don't show again",
                "btn_ok": "Got it",
                "error_ffmpeg": "FFmpeg not found.\n\nTo install, open PowerShell as Admin and run:\nwinget install ffmpeg\n\nOr download manually from gyan.dev",
                "lbl_lang": "Language / Idioma",
                "lbl_theme": "Appearance / Apariencia",
                "switch_dark": "Dark Mode",
                "btn_save_restart": "Save and Restart",
                "alert_playlist_title": "Playlist Detected",
                "alert_playlist_msg": "This link is a Playlist or Radio.\nIt will download MULTIPLE videos.\n\nDo you want to proceed?",
                "about_title": "About the Creator",
                "about_desc": "Developed with ❤️ by SirAtomos.\nFollow me!"
            }
        }

        self.verificar_ffmpeg()
        self.construir_interfaz()
        self.root.after(200, self.mostrar_aviso_inicial)

    def t(self, key):
        return self.textos_dict[self.config["lang"]].get(key, key)

    def verificar_ffmpeg(self):
        if shutil.which("ffmpeg") is None:
            messagebox.showwarning("Falta Dependencia", self.t("error_ffmpeg"))

    def cargar_configuracion(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    saved = json.load(f)
                    self.config.update(saved)
            except:
                pass

    def guardar_configuracion(self):
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.config, f)
        except:
            pass
            
    def registrar_historial(self, nombre, formato):
        try:
            registro = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "nombre": nombre,
                "formato": formato
            }
            historial = []
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    try:
                        historial = json.load(f)
                    except:
                        pass
            historial.insert(0, registro)
            historial = historial[:100]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(historial, f, ensure_ascii=False, indent=4)
        except:
            pass

    def construir_interfaz(self):
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0, fg_color=self.color_panel)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text=self.t("title"), font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_text)
        self.logo_label.pack(padx=20, pady=(20, 10))
        
        self.subtitle_label = ctk.CTkLabel(self.sidebar, text=self.t("subtitle"), font=ctk.CTkFont(size=12), text_color="gray")
        self.subtitle_label.pack(padx=20, pady=(0, 20))

        self.btn_history = ctk.CTkButton(self.sidebar, text=self.t("history"), command=self.abrir_historial, 
                                         fg_color=("gray85", "#333333"), hover_color=("gray75", "#444444"), text_color=self.color_text)
        self.btn_history.pack(padx=20, pady=10)

        self.btn_settings = ctk.CTkButton(self.sidebar, text=self.t("settings"), command=self.abrir_configuracion, 
                                          fg_color="transparent", border_width=1, border_color="gray", hover_color=("gray85", "#333333"), text_color=self.color_text)
        self.btn_settings.pack(padx=20, pady=10)

        self.btn_about = ctk.CTkButton(self.sidebar, text=self.t("about"), command=self.abrir_sobre_mi,
                                       fg_color="transparent", border_width=1, border_color="gray", hover_color=("gray85", "#333333"), text_color=self.color_text)
        self.btn_about.pack(padx=20, pady=10)

        self.watermark = ctk.CTkLabel(self.sidebar, text=self.t("created_by"), font=ctk.CTkFont(size=10), text_color="gray")
        self.watermark.pack(side="bottom", padx=20, pady=20)

        self.main_area = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.dir_frame = ctk.CTkFrame(self.main_area, fg_color=self.color_panel)
        self.dir_frame.pack(fill="x", pady=(0, 20))

        self.lbl_dir = ctk.CTkLabel(self.dir_frame, text=self.t("save_in"), text_color=self.color_text)
        self.lbl_dir.pack(side="left", padx=15, pady=10)

        self.entry_dir = ctk.CTkEntry(self.dir_frame, textvariable=self.ruta_destino, width=300, 
                                      fg_color=self.color_entry_bg, border_color=self.color_border, text_color=self.color_text)
        self.entry_dir.pack(side="left", padx=10, pady=10)

        self.btn_browse = ctk.CTkButton(self.dir_frame, text=self.t("browse"), width=80, command=self.seleccionar_carpeta, 
                                        fg_color=("gray85", "#333333"), hover_color=("gray75", "#444444"), text_color=self.color_text)
        self.btn_browse.pack(side="left", padx=10, pady=10)

        self.config_frame = ctk.CTkFrame(self.main_area, fg_color=self.color_panel)
        self.config_frame.pack(fill="x", pady=(0, 20))
        
        self.lbl_config_title = ctk.CTkLabel(self.config_frame, text=self.t("config_group"), font=ctk.CTkFont(weight="bold"), text_color=self.color_text)
        self.lbl_config_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.opts_container = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.opts_container.pack(fill="x", padx=15, pady=(0, 15))

        self.rb_audio = ctk.CTkRadioButton(self.opts_container, text=self.t("audio_only"), variable=self.tipo_var, value="Audio", 
                                           command=self.actualizar_opciones, fg_color=self.color_accent, hover_color=self.color_accent_hover, text_color=self.color_text)
        self.rb_audio.pack(side="left", padx=10)

        self.rb_video = ctk.CTkRadioButton(self.opts_container, text=self.t("video_audio"), variable=self.tipo_var, value="Video", 
                                           command=self.actualizar_opciones, fg_color=self.color_accent, hover_color=self.color_accent_hover, text_color=self.color_text)
        self.rb_video.pack(side="left", padx=10)

        self.combo_formato = ctk.CTkOptionMenu(self.opts_container, variable=self.formato_var, values=["mp3", "flac", "m4a"], width=100,
                                               fg_color=self.color_accent, button_color=self.color_accent_hover, button_hover_color=self.color_accent, text_color="white")
        self.combo_formato.pack(side="left", padx=20)

        self.combo_calidad = ctk.CTkOptionMenu(self.opts_container, variable=self.calidad_var, values=["320 kbps", "192 kbps"], width=150,
                                               fg_color=self.color_accent, button_color=self.color_accent_hover, button_hover_color=self.color_accent, text_color="white")
        self.combo_calidad.pack(side="left", padx=10)

        self.links_frame_title = ctk.CTkLabel(self.main_area, text=self.t("instructions"), anchor="w", text_color="gray")
        self.links_frame_title.pack(fill="x", pady=(0, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_area, label_text="URLs", fg_color=self.color_panel, label_fg_color="gray", label_text_color=("black", "white"))
        self.scroll_frame.pack(fill="both", expand=True, pady=(0, 20))

        self.status_label = ctk.CTkLabel(self.main_area, text=self.t("status_ready"), text_color="gray")
        self.status_label.pack(side="bottom", pady=5)

        self.btn_descargar = ctk.CTkButton(self.main_area, text=self.t("btn_download"), height=50, font=ctk.CTkFont(size=15, weight="bold"), 
                                           command=self.iniciar_descarga, fg_color=self.color_accent, hover_color=self.color_accent_hover, text_color="white")
        self.btn_descargar.pack(side="bottom", fill="x", pady=10)

        self.actualizar_opciones()
        self.agregar_entry()

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.ruta_destino.set(carpeta)

    def actualizar_opciones(self):
        tipo = self.tipo_var.get()
        if tipo == "Audio":
            self.combo_formato.configure(values=["mp3", "flac", "wav", "ogg", "m4a"])
            self.combo_formato.set("mp3")
            self.combo_calidad.configure(values=["320 kbps", "256 kbps", "192 kbps", "128 kbps"])
            self.combo_calidad.set("320 kbps")
        else:
            self.combo_formato.configure(values=["mp4", "mkv"])
            self.combo_formato.set("mp4")
            self.combo_calidad.configure(values=["Best Available", "1080p", "720p", "480p"])
            self.combo_calidad.set("Best Available")

    def validar_y_agregar(self, entry_widget):
        url = entry_widget.get().strip()
        if "list=" in url:
            respuesta = messagebox.askyesno(self.t("alert_playlist_title"), self.t("alert_playlist_msg"))
            if not respuesta:
                entry_widget.delete(0, tk.END)
                return "break"
        
        self.agregar_entry()

    def agregar_entry(self):
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)

        entry = ctk.CTkEntry(row_frame, width=350, placeholder_text="https://youtube.com/...", 
                             fg_color=self.color_entry_bg, border_color=self.color_border, text_color=self.color_text)
        entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        entry.bind("<Return>", lambda event, e=entry: self.validar_y_agregar(e))
        entry.focus()

        progress = ctk.CTkProgressBar(row_frame, width=150, progress_color=self.color_accent)
        progress.set(0)
        progress.pack(side="left", padx=10)

        lbl_status = ctk.CTkLabel(row_frame, text="", width=120, anchor="w", text_color=self.color_text)
        lbl_status.pack(side="left")

        self.rows.append({"entry": entry, "bar": progress, "status": lbl_status, "frame": row_frame})

    def reiniciar_ui(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.rows = []
        self.agregar_entry()
        self.status_label.configure(text=self.t("status_ready"))

    def iniciar_descarga(self):
        valid_rows = [row for row in self.rows if row["entry"].get().strip()]
        if not valid_rows:
            return

        self.btn_descargar.configure(state="disabled", fg_color="gray")
        config_dl = {'tipo': self.tipo_var.get(), 'formato': self.formato_var.get(), 'calidad': self.calidad_var.get()}
        threading.Thread(target=self.procesar_lista, args=(valid_rows, config_dl), daemon=True).start()

    def limpiar_ansi(self, texto):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', texto)

    def hook_progreso(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            descargado = d.get('downloaded_bytes', 0)
            
            p_str = self.limpiar_ansi(d.get('_percent_str', '')).strip()
            s_str = self.limpiar_ansi(d.get('_speed_str', '')).strip()
            
            if total and self.active_bar:
                p = (descargado / total)
                self.root.after(0, lambda: self.active_bar.set(p))
            
            if self.active_status:
                texto_progreso = f"{p_str} • {s_str}"
                self.root.after(0, lambda: self.active_status.configure(text=texto_progreso))

    def procesar_lista(self, rows, config):
        carpeta_final = self.ruta_destino.get()
        opciones = {
            'outtmpl': os.path.join(carpeta_final, '%(title)s.%(ext)s'),
            'ffmpeg_location': shutil.which("ffmpeg"),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.hook_progreso],
            'nocheckcertificate': True,
            'ignoreerrors': True
        }

        if config['tipo'] == "Audio":
            opciones.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': config['formato'], 'preferredquality': '192'}]})
        else:
            c = config['calidad'].replace("p", "")
            fmt = f'bestvideo[height<={c}]+bestaudio/best' if c.isdigit() else 'bestvideo+bestaudio/best'
            opciones.update({'format': fmt, 'merge_output_format': config['formato']})

        for row in rows:
            self.active_bar = row["bar"]
            self.active_status = row["status"]
            self.root.after(0, lambda: row["status"].configure(text="Iniciando..."))
            url = row["entry"].get().strip()
            
            try:
                with yt_dlp.YoutubeDL(opciones) as ydl:
                    info = ydl.extract_info(url, download=True)
                titulo = info.get('title', 'Video')
                self.registrar_historial(titulo, config['formato'])
                self.root.after(0, lambda: row["status"].configure(text="✔ Completo", text_color=self.color_accent))
                self.root.after(0, lambda: row["bar"].set(1))
            except:
                self.root.after(0, lambda: row["status"].configure(text="✘ Error", text_color="red"))

        self.root.after(0, lambda: self.status_label.configure(text=self.t("msg_success")))
        self.root.after(0, lambda: self.btn_descargar.configure(state="normal", fg_color=self.color_accent))
        self.root.after(3000, self.reiniciar_ui)

    def abrir_historial(self):
        win = ctk.CTkToplevel(self.root)
        win.geometry("600x400")
        win.title(self.t("history"))
        win.transient(self.root)
        win.configure(fg_color=self.color_bg)
        
        lbl = ctk.CTkLabel(win, text=self.t("history"), font=ctk.CTkFont(size=20, weight="bold"), text_color=self.color_text)
        lbl.pack(pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.map("Treeview", background=[("selected", self.color_accent_hover)])
        style.configure("Treeview.Heading", background="#333333", foreground="white", relief="flat")

        cols = ("date", "name", "format")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.heading("date", text=self.t("col_date"))
        tree.heading("name", text=self.t("col_name"))
        tree.heading("format", text=self.t("col_format"))
        
        tree.column("date", width=120)
        tree.column("name", width=350)
        tree.column("format", width=80)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        tree.insert("", "end", values=(item["fecha"], item["nombre"], item["formato"]))
            except:
                pass
        
        def limpiar():
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
                for i in tree.get_children():
                    tree.delete(i)
        
        btn = ctk.CTkButton(win, text=self.t("btn_clear"), command=limpiar, fg_color="#c0392b", hover_color="#e74c3c", text_color="white")
        btn.pack(pady=10)

    def abrir_configuracion(self):
        win = ctk.CTkToplevel(self.root)
        win.geometry("300x300") 
        win.title(self.t("settings"))
        win.transient(self.root)
        win.configure(fg_color=self.color_bg)
        
        ctk.CTkLabel(win, text=self.t("lbl_lang"), font=ctk.CTkFont(weight="bold"), text_color=self.color_text).pack(pady=(20, 5))
        combo_lang = ctk.CTkOptionMenu(win, values=["Español", "English"], fg_color=self.color_accent, button_color=self.color_accent_hover, text_color="white")
        combo_lang.pack(pady=5)
        combo_lang.set("Español" if self.config["lang"] == "es" else "English")

        ctk.CTkLabel(win, text=self.t("lbl_theme"), font=ctk.CTkFont(weight="bold"), text_color=self.color_text).pack(pady=(20, 5))
        
        def cambiar_tema_visual():
            modo = "Dark" if switch_theme.get() == 1 else "Light"
            ctk.set_appearance_mode(modo)
            self.config["theme_mode"] = modo

        switch_theme = ctk.CTkSwitch(win, text=self.t("switch_dark"), command=cambiar_tema_visual, progress_color=self.color_accent, text_color=self.color_text)
        switch_theme.pack(pady=5)
        
        if self.config.get("theme_mode") == "Dark":
            switch_theme.select()
        else:
            switch_theme.deselect()

        def save():
            self.config["lang"] = "es" if combo_lang.get() == "Español" else "en"
            self.guardar_configuracion()
            win.destroy()
            self.root.destroy() 
            
        btn = ctk.CTkButton(win, text=self.t("btn_save_restart"), command=save, fg_color=("gray85", "#333333"), hover_color=("gray75", "#444444"), text_color=self.color_text)
        btn.pack(side="bottom", pady=25)

    def abrir_sobre_mi(self):
        win = ctk.CTkToplevel(self.root)
        win.geometry("300x350")
        win.title(self.t("about"))
        win.transient(self.root)
        win.configure(fg_color=self.color_bg)

        ctk.CTkLabel(win, text=self.t("about_title"), font=ctk.CTkFont(size=18, weight="bold"), text_color=self.color_text).pack(pady=(20, 10))
        
        ctk.CTkLabel(win, text=self.t("about_desc"), text_color="gray").pack(pady=(0, 20))

        link_github = "https://github.com/lAtomos-afk"
        link_discord = "https://discord.com/invite/gQhAt4uqKG"
        link_youtube = "https://www.youtube.com/@SirAtomos"

        def abrir(url):
            webbrowser.open(url)

        btn_gh = ctk.CTkButton(win, text="GitHub", command=lambda: abrir(link_github),
                               fg_color="#333", hover_color="#24292e", width=200)
        btn_gh.pack(pady=5)

        btn_ds = ctk.CTkButton(win, text="Discord", command=lambda: abrir(link_discord),
                               fg_color="#5865F2", hover_color="#4752C4", width=200)
        btn_ds.pack(pady=5)

        btn_yt = ctk.CTkButton(win, text="YouTube", command=lambda: abrir(link_youtube),
                               fg_color="#FF0000", hover_color="#CC0000", width=200)
        btn_yt.pack(pady=5)

        ctk.CTkButton(win, text="Cerrar", command=win.destroy, fg_color="transparent", border_width=1, border_color="gray", text_color=self.color_text, width=100).pack(side="bottom", pady=20)

    def mostrar_aviso_inicial(self):
        if not self.config.get("show_startup_msg", True):
            return

        win = ctk.CTkToplevel(self.root)
        win.geometry("400x300")
        win.title(self.t("aviso_title"))
        win.transient(self.root)
        win.configure(fg_color=self.color_bg)
        
        ctk.CTkLabel(win, text=self.t("aviso_body"), font=ctk.CTkFont(size=14), text_color=self.color_text).pack(pady=30)
        
        var_chk = ctk.BooleanVar()
        chk = ctk.CTkCheckBox(win, text=self.t("chk_nomore"), variable=var_chk, fg_color=self.color_accent, text_color=self.color_text)
        chk.pack(pady=10)
        
        def close():
            if var_chk.get():
                self.config["show_startup_msg"] = False
                self.guardar_configuracion()
            win.destroy()
            
        ctk.CTkButton(win, text=self.t("btn_ok"), command=close, fg_color=self.color_accent, hover_color=self.color_accent_hover, text_color="white").pack(pady=10)

if __name__ == "__main__":
    app = ctk.CTk()
    WindowsVideoDownloader(app)
    app.mainloop()