import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import yt_dlp
import os
import sys
import threading
import shutil
import json
import re
import webbrowser
import requests
import queue
import subprocess
from datetime import datetime

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("green")

class UniversalVideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1050x750")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        self.root.title("Video Downloader")
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.icon_path = os.path.join(base_path, 'icon.ico')
        
        if os.path.exists(self.icon_path):
            try: self.root.iconbitmap(self.icon_path)
            except: pass

        self.CURRENT_VERSION = "3.9" 
        self.REPO_URL = "https://github.com/lAtomos-afk/VideoDownloader"
        self.API_RELEASE_URL = "https://api.github.com/repos/lAtomos-afk/VideoDownloader/releases/latest"

        if sys.platform == "win32":
            self.os_name = "Windows"
            self.config_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "VideoDownloader")
        elif sys.platform.startswith("linux"):
            self.os_name = "Linux"
            self.config_dir = os.path.join(os.path.expanduser("~"), ".config", "VideoDownloader")
        elif sys.platform == "darwin":
            self.os_name = "MacOS"
            self.config_dir = os.path.join(os.path.expanduser("~"), ".config", "VideoDownloader")
        else:
            self.os_name = "Desktop"
            self.config_dir = os.path.join(os.path.expanduser("~"), ".config", "VideoDownloader")

        self.edition_text = f"SirAtomos | {self.os_name} Edition"

        self.home_dir = os.path.expanduser("~")
        self.themes_dir = os.path.join(self.config_dir, "themes")
        
        if not os.path.exists(self.config_dir): os.makedirs(self.config_dir)
        if not os.path.exists(self.themes_dir): os.makedirs(self.themes_dir)

        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.history_file = os.path.join(self.config_dir, "history.json")
        
        self.default_config = {
            "lang": "es", 
            "show_startup_msg": True, 
            "current_theme": "Default Dark",
            "last_mode": "Audio",
            "last_format": "mp3",
            "last_quality": "320 kbps"
        }
        self.config = self.default_config.copy()
        self.cargar_configuracion()

        self.system_themes = {
            "Default Dark": {
                "bg": "#121212", "panel": "#1E1E1E", "text": "#FFFFFF",
                "entry_bg": "#2D2D2D", "border": "#333333",
                "accent": "#2ecc71", "accent_hover": "#27ae60",
                "button_text": "#FFFFFF" 
            },
            "Default Light": {
                "bg": "#F2F2F2", "panel": "#FFFFFF", "text": "#000000",
                "entry_bg": "#FFFFFF", "border": "#D0D0D0",
                "accent": "#2ecc71", "accent_hover": "#27ae60",
                "button_text": "#FFFFFF"
            }
        }
        
        self.themes = self.system_themes.copy()
        self.cargar_temas_usuario()
        
        self.ruta_destino = tk.StringVar(value=os.path.join(self.home_dir, "Downloads"))
        
        self.tipo_var = tk.StringVar(value=self.config.get("last_mode", "Audio"))
        self.formato_var = tk.StringVar(value=self.config.get("last_format", "mp3"))
        self.calidad_var = tk.StringVar(value=self.config.get("last_quality", "320 kbps"))
        
        self.rows = []
        
        self.download_queue = queue.Queue()
        self.is_downloading = False
        self.active_row = None

        self.textos_dict = {
            "es": {
                "title": "Video Downloader", "subtitle": f"v{self.CURRENT_VERSION}", "save_in": "Guardar en:", "browse": "Examinar",
                "config_group": "Configuración de Descarga", "mode": "Modo:", "audio_only": "Solo Audio", "video_audio": "Video + Audio",
                "format": "Formato:", "quality": "Calidad:", "instructions": "⬇ Pega los enlaces abajo (Enter para agregar más)",
                "btn_download": "INICIAR COLA", "status_ready": "Listo", "settings": "Ajustes",
                "history": "Historial", "about": "Sobre Mí", 
                "created_by": self.edition_text,
                "msg_success": "Cola finalizada", "btn_clear": "Limpiar Historial", "btn_open_loc": "Abrir Ubicación",
                "col_date": "Fecha", "col_name": "Nombre", "col_format": "Formato", "aviso_title": "Aviso Importante",
                "aviso_body": f"¡Bienvenido a la v{self.CURRENT_VERSION}!\n\nDetectado: {self.os_name}\nSe ha optimizado el sistema para tu SO.",
                "chk_nomore": "No mostrar de nuevo", "btn_ok": "Entendido", "error_ffmpeg": "FFmpeg no encontrado.",
                "lbl_lang": "Idioma / Language", "lbl_theme_select": "Seleccionar Tema / Select Theme",
                "btn_theme_editor": "Crear/Editar Tema (Vista Previa)", "btn_open_folder": "Abrir Carpeta de Temas",
                "btn_close": "Cerrar", "alert_playlist_title": "Playlist Detectada",
                "alert_playlist_msg": "Enlace de Playlist detectado.\n¿Continuar?", "about_title": "Sobre el Creador",
                "about_desc": "Desarrollado con Amor por SirAtomos.", "btn_carrd": "Mis Redes / Contacto",
                "lbl_update": "Actualizaciones", "btn_check_update": "Buscar Actualización", "msg_uptodate": "Estás actualizado",
                "msg_newversion": "¡Nueva versión!", "msg_neterror": "Error de conexión",
                "editor_title": "Creador de Temas (Vista Previa)", 
                "editor_name": "Nombre de tu Tema:",
                "editor_col_bg": "Fondo Principal de la App", 
                "editor_col_panel": "Fondo de Menús y Bloques",
                "editor_col_text": "Color de las Letras", 
                "editor_col_entry": "Casillas de Texto (Donde escribes)",
                "editor_col_border": "Color de Bordes y Líneas", 
                "editor_col_accent": "Color de Botones y Barras",
                "editor_col_btn_text": "Color de Letra dentro de Botones", 
                "btn_save_theme": "Guardar Tema", "msg_theme_saved": "¡Tema guardado y aplicado!",
                "btn_cancel_theme": "Cancelar (Deshacer)", "btn_clean_ui": "Limpiar Completados", "status_queue": "En cola",
                "status_downloading": "Descargando...", "status_cancelled": "Cancelado"
            },
            "en": {
                "title": "Video Downloader", "subtitle": f"v{self.CURRENT_VERSION}", "save_in": "Save to:", "browse": "Browse",
                "config_group": "Download Settings", "mode": "Mode:", "audio_only": "Audio Only", "video_audio": "Video + Audio",
                "format": "Format:", "quality": "Quality:", "instructions": "⬇ Paste links below (Press Enter to add row)",
                "btn_download": "START QUEUE", "status_ready": "Ready", "settings": "Settings",
                "history": "History", "about": "About Me", 
                "created_by": self.edition_text,
                "msg_success": "Queue finished", "btn_clear": "Clear History", "btn_open_loc": "Open Location",
                "col_date": "Date", "col_name": "Name", "col_format": "Format", "aviso_title": "Important Notice",
                "aviso_body": f"Welcome to v{self.CURRENT_VERSION}!\n\nDetected: {self.os_name}\nSystem optimized for your OS.",
                "chk_nomore": "Don't show again", "btn_ok": "Got it", "error_ffmpeg": "FFmpeg not found.",
                "lbl_lang": "Language", "lbl_theme_select": "Select Theme",
                "btn_theme_editor": "Create/Edit Theme (Live Preview)", "btn_open_folder": "Open Themes Folder",
                "btn_close": "Close", "alert_playlist_title": "Playlist Detected",
                "alert_playlist_msg": "Playlist link detected.\nProceed?", "about_title": "About Creator",
                "about_desc": "Developed by SirAtomos.", "btn_carrd": "Contact Me",
                "lbl_update": "Updates", "btn_check_update": "Check Updates", "msg_uptodate": "Up to date",
                "msg_newversion": "New version!", "msg_neterror": "Connection Error",
                "editor_title": "Theme Editor (Live Preview)", "editor_name": "Theme Name:",
                "editor_col_bg": "Background", "editor_col_panel": "Panels", "editor_col_text": "Text",
                "editor_col_entry": "Inputs", "editor_col_border": "Borders", "editor_col_accent": "Accent (Button BG)",
                "editor_col_btn_text": "Button Text Color",
                "btn_save_theme": "Save Theme", "msg_theme_saved": "Theme saved and applied!",
                "btn_cancel_theme": "Cancel (Revert)", "btn_clean_ui": "Clear Completed", "status_queue": "Queued",
                "status_downloading": "Downloading...", "status_cancelled": "Cancelled"
            }
        }

        self.verificar_ffmpeg()
        self.construir_interfaz()
        self.aplicar_tema_actual()
        self.root.after(200, self.mostrar_aviso_inicial)

    def aplicar_icono_ventana(self, window):
        if os.path.exists(self.icon_path):
            try:
                window.after(200, lambda: window.iconbitmap(self.icon_path))
            except: pass

    def t(self, key):
        lang = self.config.get("lang", "es")
        return self.textos_dict.get(lang, self.textos_dict["es"]).get(key, key)

    def obtener_ruta_ffmpeg(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        ext = ".exe" if sys.platform == "win32" else ""
        ffmpeg_exe = os.path.join(base_path, f'ffmpeg{ext}')
        
        return ffmpeg_exe if os.path.exists(ffmpeg_exe) else None

    def verificar_ffmpeg(self):
        ruta = self.obtener_ruta_ffmpeg()
        if ruta is None and shutil.which("ffmpeg") is None: pass

    def abrir_carpeta_sistema(self, ruta):
        if sys.platform == "win32":
            os.startfile(ruta)
        elif sys.platform == "darwin":
            subprocess.call(["open", ruta])
        else:
            subprocess.call(["xdg-open", ruta])
            
    def abrir_archivo_seleccionado(self, ruta_archivo):
        if not os.path.exists(ruta_archivo):
            if os.path.exists(os.path.dirname(ruta_archivo)):
                self.abrir_carpeta_sistema(os.path.dirname(ruta_archivo))
            return
            
        if sys.platform == "win32":
            subprocess.run(['explorer', '/select,', os.path.normpath(ruta_archivo)])
        elif sys.platform == "darwin":
            subprocess.run(['open', '-R', ruta_archivo])
        else:
            self.abrir_carpeta_sistema(os.path.dirname(ruta_archivo))

    def cargar_configuracion(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f: self.config.update(json.load(f))
            except: pass

    def guardar_configuracion(self):
        try:
            with open(self.settings_file, "w") as f: json.dump(self.config, f)
        except: pass
        
    def guardar_cambios_ui(self, valor=None):
        self.config["last_mode"] = self.tipo_var.get()
        self.config["last_format"] = self.formato_var.get()
        self.config["last_quality"] = self.calidad_var.get()
        self.guardar_configuracion()
        
        if valor: 
            if self.tipo_var.get() == "Audio":
                self.verificar_calidad_audio(valor)

    def cargar_temas_usuario(self):
        if os.path.exists(self.themes_dir):
            for file in os.listdir(self.themes_dir):
                if file.endswith(".json"):
                    try:
                        with open(os.path.join(self.themes_dir, file), "r") as f:
                            data = json.load(f)
                            if "bg" in data: self.themes[file.replace(".json", "")] = data
                    except: pass

    def aplicar_tema_actual(self):
        theme_name = self.config.get("current_theme", "Default Dark")
        if theme_name not in self.themes: theme_name = "Default Dark"
        self.aplicar_colores(self.themes[theme_name])

    def aplicar_colores(self, t):
        try:
            bg = t.get("bg", "#121212")
            panel = t.get("panel", "#1E1E1E")
            text = t.get("text", "#FFFFFF")
            entry_bg = t.get("entry_bg", "#2D2D2D")
            border = t.get("border", "#333333")
            accent = t.get("accent", "#2ecc71")
            accent_hover = t.get("accent_hover", accent)
            btn_text = t.get("button_text", "#FFFFFF") 

            self.root.configure(fg_color=bg)
            self.sidebar.configure(fg_color=panel)
            self.main_area.configure(fg_color="transparent")
            self.dir_frame.configure(fg_color=panel, border_color=border)
            self.config_frame.configure(fg_color=panel, border_color=border)
            self.scroll_frame.configure(fg_color=panel, label_fg_color="gray", label_text_color=text)

            self.logo_label.configure(text_color=text)
            self.subtitle_label.configure(text_color=text)
            self.watermark.configure(text_color=text)
            self.lbl_dir.configure(text_color=text)
            self.lbl_config_title.configure(text_color=text)
            self.links_frame_title.configure(text_color="gray")
            self.status_label.configure(text_color="gray")

            for btn in [self.btn_history, self.btn_settings, self.btn_about]:
                btn.configure(fg_color=bg, hover_color=border, text_color=text)
                if btn != self.btn_history: btn.configure(border_color=border)

            self.entry_dir.configure(fg_color=entry_bg, border_color=border, text_color=text)
            self.btn_browse.configure(fg_color=accent, hover_color=accent_hover, text_color=btn_text)
            self.btn_descargar.configure(fg_color=accent, hover_color=accent_hover, text_color=btn_text)
            self.btn_clean.configure(fg_color="transparent", border_width=1, border_color=accent, text_color=text)

            for rb in [self.rb_audio, self.rb_video]:
                rb.configure(fg_color=accent, hover_color=accent_hover, text_color=text)
            
            for combo in [self.combo_formato, self.combo_calidad]:
                combo.configure(
                    fg_color=accent, 
                    button_color=accent_hover, 
                    button_hover_color=accent, 
                    text_color=btn_text,
                    dropdown_fg_color=entry_bg, 
                    dropdown_text_color=text,   
                    dropdown_hover_color=panel  
                )

            for row in self.rows:
                row["entry"].configure(fg_color=entry_bg, border_color=border, text_color=text)
                row["bar"].configure(progress_color=accent)
                row["status"].configure(text_color=text)

            self.root.update()
        except Exception as e:
            print(f"Error aplicando tema: {e}")

    def actualizar_textos(self):
        self.logo_label.configure(text=self.t("title"))
        self.subtitle_label.configure(text=self.t("subtitle"))
        self.btn_history.configure(text=self.t("history"))
        self.btn_settings.configure(text=self.t("settings"))
        self.btn_about.configure(text=self.t("about"))
        self.watermark.configure(text=self.t("created_by"))
        self.lbl_dir.configure(text=self.t("save_in"))
        self.btn_browse.configure(text=self.t("browse"))
        self.lbl_config_title.configure(text=self.t("config_group"))
        self.rb_audio.configure(text=self.t("audio_only"))
        self.rb_video.configure(text=self.t("video_audio"))
        self.links_frame_title.configure(text=self.t("instructions"))
        self.status_label.configure(text=self.t("status_ready"))
        self.btn_descargar.configure(text=self.t("btn_download"))
        self.btn_clean.configure(text=self.t("btn_clean_ui"))
        self.root.title(f"{self.t('title')}")

    def construir_interfaz(self):
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text=self.t("title"), font=ctk.CTkFont(size=20, weight="bold"), fg_color="transparent")
        self.logo_label.pack(padx=20, pady=(20, 10))
        
        self.subtitle_label = ctk.CTkLabel(self.sidebar, text=self.t("subtitle"), font=ctk.CTkFont(size=12))
        self.subtitle_label.pack(padx=20, pady=(0, 20))

        self.btn_history = ctk.CTkButton(self.sidebar, text=self.t("history"), command=self.abrir_historial)
        self.btn_history.pack(padx=20, pady=10)
        self.btn_settings = ctk.CTkButton(self.sidebar, text=self.t("settings"), command=self.abrir_configuracion, border_width=1)
        self.btn_settings.pack(padx=20, pady=10)
        self.btn_about = ctk.CTkButton(self.sidebar, text=self.t("about"), command=self.abrir_sobre_mi, border_width=1)
        self.btn_about.pack(padx=20, pady=10)
        self.watermark = ctk.CTkLabel(self.sidebar, text=self.t("created_by"), font=ctk.CTkFont(size=10))
        self.watermark.pack(side="bottom", padx=20, pady=20)
        self.main_area = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.dir_frame = ctk.CTkFrame(self.main_area, border_width=1)
        self.dir_frame.pack(fill="x", pady=(0, 20))
        self.lbl_dir = ctk.CTkLabel(self.dir_frame, text=self.t("save_in"))
        self.lbl_dir.pack(side="left", padx=15, pady=10)
        self.entry_dir = ctk.CTkEntry(self.dir_frame, textvariable=self.ruta_destino, width=300)
        self.entry_dir.pack(side="left", padx=10, pady=10)
        self.btn_browse = ctk.CTkButton(self.dir_frame, text=self.t("browse"), width=80, command=self.seleccionar_carpeta)
        self.btn_browse.pack(side="left", padx=10, pady=10)
        self.config_frame = ctk.CTkFrame(self.main_area, border_width=1)
        self.config_frame.pack(fill="x", pady=(0, 20))
        self.lbl_config_title = ctk.CTkLabel(self.config_frame, text=self.t("config_group"), font=ctk.CTkFont(weight="bold"))
        self.lbl_config_title.pack(anchor="w", padx=15, pady=(10, 5))
        self.opts_container = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.opts_container.pack(fill="x", padx=15, pady=(0, 15))        
        self.rb_audio = ctk.CTkRadioButton(self.opts_container, text=self.t("audio_only"), variable=self.tipo_var, value="Audio", command=self.actualizar_opciones)
        self.rb_audio.pack(side="left", padx=10)
        self.rb_video = ctk.CTkRadioButton(self.opts_container, text=self.t("video_audio"), variable=self.tipo_var, value="Video", command=self.actualizar_opciones)
        self.rb_video.pack(side="left", padx=10)
        self.combo_formato = ctk.CTkOptionMenu(self.opts_container, variable=self.formato_var, values=["mp3"], width=100, command=self.guardar_cambios_ui)
        self.combo_formato.pack(side="left", padx=20)
        self.combo_calidad = ctk.CTkOptionMenu(self.opts_container, variable=self.calidad_var, values=["320 kbps"], width=150, command=self.guardar_cambios_ui)
        self.combo_calidad.pack(side="left", padx=10)
        self.links_frame_title = ctk.CTkLabel(self.main_area, text=self.t("instructions"), anchor="w")
        self.links_frame_title.pack(fill="x", pady=(0, 5))
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_area, label_text="URLs")
        self.scroll_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(self.main_area, text=self.t("status_ready"))
        self.status_label.pack(side="bottom", pady=5)
        
        self.action_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.action_frame.pack(side="bottom", fill="x", pady=10)
        
        self.btn_descargar = ctk.CTkButton(self.action_frame, text=self.t("btn_download"), height=50, font=ctk.CTkFont(size=15, weight="bold"), command=self.iniciar_descarga)
        self.btn_descargar.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_clean = ctk.CTkButton(self.action_frame, text=self.t("btn_clean_ui"), height=50, width=150, command=self.limpiar_completados)
        self.btn_clean.pack(side="right", padx=(5, 0))

        self.actualizar_opciones()
        self.agregar_entry()

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta: self.ruta_destino.set(carpeta)

    def actualizar_opciones(self):
        tipo = self.tipo_var.get()
        if tipo == "Audio":
            self.combo_formato.configure(values=["mp3", "flac", "wav", "ogg", "m4a"])
            self.combo_formato.set(self.config.get("last_format", "mp3"))
            self.verificar_calidad_audio(self.combo_formato.get()) 
        else:
            self.combo_formato.configure(values=["mp4", "mkv"])
            self.combo_formato.set(self.config.get("last_format", "mp4"))
            self.combo_calidad.configure(values=["Best Available", "1080p", "720p", "480p"], state="normal")
            self.calidad_var.set(self.config.get("last_quality", "Best Available"))
            
        self.guardar_cambios_ui()

    def verificar_calidad_audio(self, choice):
        if choice in ["flac", "wav"]:
            self.combo_calidad.configure(values=["Max Quality"], state="disabled")
            self.calidad_var.set("Max Quality")
        else:
            self.combo_calidad.configure(values=["320 kbps", "256 kbps", "192 kbps", "128 kbps"], state="normal")
            if self.calidad_var.get() == "Max Quality":
                self.calidad_var.set("320 kbps")

    def validar_y_agregar(self, entry_widget):
        url = entry_widget.get().strip()
        if "list=" in url:
            if not messagebox.askyesno(self.t("alert_playlist_title"), self.t("alert_playlist_msg")):
                entry_widget.delete(0, tk.END)
                return "break"
        self.agregar_entry()

    def cancelar_fila(self, row):
        if row.get("finished"): return
        if row == self.active_row:
            row["cancel_requested"] = True
            row["status"].configure(text="Cancelling...", text_color="orange")
        else:
            row["cancel_requested"] = True
            row["status"].configure(text=self.t("status_cancelled"), text_color="orange")
            row["btn_action"].configure(state="disabled")

    def agregar_entry(self):
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)
        
        curr_theme_name = self.config.get("current_theme", "Default Dark")
        t = self.themes.get(curr_theme_name, self.system_themes["Default Dark"])
        
        entry = ctk.CTkEntry(row_frame, width=300, placeholder_text="https://youtube.com/...", 
                             fg_color=t.get("entry_bg", "#2D2D2D"), border_color=t.get("border", "#333333"), text_color=t.get("text", "white"))
        entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        entry.bind("<Return>", lambda event, e=entry: self.validar_y_agregar(e))
        entry.focus()

        progress = ctk.CTkProgressBar(row_frame, width=120, progress_color=t.get("accent", "#2ecc71"))
        progress.set(0)
        progress.pack(side="left", padx=(0, 10))

        lbl_status = ctk.CTkLabel(row_frame, text="", width=100, anchor="w", text_color=t.get("text", "white"))
        lbl_status.pack(side="left", padx=(0, 5))

        btn_action = ctk.CTkButton(row_frame, text="✖", width=30, height=28, fg_color="#e74c3c", hover_color="#c0392b")
        btn_action.pack(side="left", padx=(0, 5))

        row_data = {
            "entry": entry, 
            "bar": progress, 
            "status": lbl_status, 
            "btn_action": btn_action,
            "frame": row_frame, 
            "processed": False,
            "cancel_requested": False,
            "finished": False
        }
        
        btn_action.configure(command=lambda r=row_data: self.cancelar_fila(r))
        self.rows.append(row_data)

    def limpiar_completados(self):
        nuevas_filas = []
        for i, row in enumerate(self.rows):
            status_text = row["status"].cget("text")
            es_ultima = (i == len(self.rows) - 1)
            esta_activa = "..." in status_text or status_text == self.t("status_queue")
            
            if esta_activa or (not row["processed"] and es_ultima):
                nuevas_filas.append(row)
            else:
                row["frame"].destroy()
        
        self.rows = nuevas_filas
        if not self.rows or self.rows[-1]["entry"].get().strip():
            self.agregar_entry()
    
    def iniciar_descarga(self):
        config_dl = {'tipo': self.tipo_var.get(), 'formato': self.formato_var.get(), 'calidad': self.calidad_var.get()}
        added_count = 0
        for row in self.rows:
            url = row["entry"].get().strip()
            if url and not row["processed"] and not row["cancel_requested"]:
                row["processed"] = True
                row["status"].configure(text=self.t("status_queue"))
                self.download_queue.put((row, config_dl))
                added_count += 1
        
        if added_count > 0 and not self.is_downloading:
            threading.Thread(target=self.processor_loop, daemon=True).start()
            
        if self.rows and self.rows[-1]["entry"].get().strip():
            self.agregar_entry()

    def processor_loop(self):
        self.is_downloading = True
        self.status_label.configure(text=self.t("status_downloading"))
        
        while not self.download_queue.empty():
            row, config = self.download_queue.get()
            if row.get("cancel_requested"):
                self.root.after(0, lambda r=row: r["status"].configure(text=self.t("status_cancelled"), text_color="orange"))
                self.root.after(0, lambda r=row: r["btn_action"].configure(state="disabled"))
                continue
                
            self.active_row = row
            self.procesar_fila_individual(row, config)
            self.active_row = None
            
        self.is_downloading = False
        self.status_label.configure(text=self.t("msg_success"))

    def limpiar_ansi(self, texto): return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', texto)

    def hook_progreso(self, d):
        if self.active_row and self.active_row.get("cancel_requested"):
            raise Exception("CancelledByUser")
            
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            descargado = d.get('downloaded_bytes', 0)
            
            if self.active_row:
                if total:
                     self.root.after(0, lambda: self.active_row["bar"].set(descargado / total))
                
                if d.get('_percent_str'):
                    p_str = self.limpiar_ansi(d.get('_percent_str', '')).strip()
                    self.root.after(0, lambda: self.active_row["status"].configure(text=f"{p_str}"))

    def procesar_fila_individual(self, row, config):
        carpeta_final = self.ruta_destino.get()
        ffmpeg_path = self.obtener_ruta_ffmpeg() or shutil.which("ffmpeg")
        
        opciones = {
            'outtmpl': os.path.join(carpeta_final, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_path,
            'quiet': True, 'no_warnings': True, 'ignoreerrors': True, 'progress_hooks': [self.hook_progreso]
        }
        if config['tipo'] == "Audio":
            opciones.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': config['formato']}]})
        else:
            c = config['calidad'].replace("p", "")
            fmt = f'bestvideo[height<={c}]+bestaudio/best' if c.isdigit() else 'bestvideo+bestaudio/best'
            opciones.update({'format': fmt, 'merge_output_format': config['formato']})

        curr_theme = self.themes.get(self.config["current_theme"], self.system_themes["Default Dark"])
        accent = curr_theme.get("accent", "#2ecc71")
        accent_hover = curr_theme.get("accent_hover", accent)

        self.root.after(0, lambda: row["status"].configure(text="Iniciando..."))
        final_filepath = None
        
        try:
            with yt_dlp.YoutubeDL(opciones) as ydl: 
                info = ydl.extract_info(row["entry"].get().strip(), download=True)
                final_filepath = ydl.prepare_filename(info)
                if config['tipo'] == "Audio":
                    base, _ = os.path.splitext(final_filepath)
                    final_filepath = f"{base}.{config['formato']}"

            self.root.after(0, lambda: row["status"].configure(text="✔", text_color=accent))
            self.root.after(0, lambda: row["bar"].set(1))
            row["finished"] = True
            
            def config_open_btn(r, path):
                r["btn_action"].configure(text="📂", fg_color=accent, hover_color=accent_hover, command=lambda: self.abrir_archivo_seleccionado(path))
            
            self.root.after(0, lambda: config_open_btn(row, final_filepath))
            
            titulo = row["entry"].get().strip() 
            hist_item = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "nombre": titulo,
                "formato": config['formato'],
                "ruta": final_filepath
            }
            self.guardar_en_historial(hist_item)
            
        except Exception as e:
            if "CancelledByUser" in str(e):
                self.root.after(0, lambda: row["status"].configure(text=self.t("status_cancelled"), text_color="orange"))
                self.root.after(0, lambda: row["btn_action"].configure(state="disabled"))
            else:
                self.root.after(0, lambda: row["status"].configure(text="✘", text_color="red"))
    
    def guardar_en_historial(self, item):
        try:
            historial = []
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    historial = json.load(f)
            historial.insert(0, item)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(historial, f, ensure_ascii=False, indent=4)
        except: pass

    def abrir_editor_temas(self):
        win = ctk.CTkToplevel(self.root)
        win.geometry("450x650")
        win.title(self.t("editor_title"))
        
        win.update()
        
        if sys.platform.startswith("linux"):
             win.attributes("-topmost", True)
        else:
             win.transient(self.root)
        
        self.aplicar_icono_ventana(win) 
        
        if sys.platform.startswith("linux"):
            win.withdraw()
            win.deiconify()
        
        original_theme_name = self.config["current_theme"]
        original_theme_data = self.themes.get(original_theme_name, self.system_themes["Default Dark"]).copy()
        editing_theme = original_theme_data.copy()
        
        def actualizar_estilo_editor():
            bg = editing_theme.get("bg", "#121212")
            win.configure(fg_color=bg)

        actualizar_estilo_editor()

        ctk.CTkLabel(win, text=self.t("editor_name"), text_color="gray").pack(pady=(15,5))
        entry_name = ctk.CTkEntry(win)
        entry_name.pack(pady=5)
        entry_name.insert(0, f"Custom {len(self.themes)}")

        frame_colors = ctk.CTkScrollableFrame(win, fg_color="transparent")
        frame_colors.pack(fill="both", expand=True, padx=20, pady=10)

        def add_picker(label_key, dict_key):
            row = ctk.CTkFrame(frame_colors, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=self.t(label_key), width=180, anchor="w", text_color="gray").pack(side="left")
            
            btn = ctk.CTkButton(row, text="", width=30, height=30, corner_radius=15, 
                                fg_color=editing_theme.get(dict_key), border_width=1, border_color="gray")
            
            def pick():
                c = colorchooser.askcolor(color=editing_theme.get(dict_key), title=self.t(label_key))[1]
                if c:
                    editing_theme[dict_key] = c
                    if dict_key == "accent": editing_theme["accent_hover"] = c 
                    btn.configure(fg_color=c)
                    self.aplicar_colores(editing_theme)
                    actualizar_estilo_editor()
            
            btn.configure(command=pick)
            btn.pack(side="right", padx=10)

        add_picker("editor_col_bg", "bg")
        add_picker("editor_col_panel", "panel")
        add_picker("editor_col_text", "text")
        add_picker("editor_col_entry", "entry_bg")
        add_picker("editor_col_border", "border")
        add_picker("editor_col_accent", "accent")
        add_picker("editor_col_btn_text", "button_text") 

        def guardar():
            name = entry_name.get().strip()
            if not name: return
            filepath = os.path.join(self.themes_dir, f"{name}.json")
            try:
                with open(filepath, "w") as f: json.dump(editing_theme, f, indent=4)
                self.themes[name] = editing_theme
                self.config["current_theme"] = name
                self.guardar_configuracion()
                messagebox.showinfo("Video Downloader", self.t("msg_theme_saved"))
                win.destroy() 
                self.abrir_configuracion() 
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def cancelar():
            self.aplicar_colores(original_theme_data)
            win.destroy()
            self.abrir_configuracion()

        win.protocol("WM_DELETE_WINDOW", cancelar)

        ctk.CTkButton(win, text=self.t("btn_save_theme"), command=guardar, fg_color="#2ecc71").pack(pady=10)
        ctk.CTkButton(win, text=self.t("btn_cancel_theme"), command=cancelar, fg_color="#e74c3c").pack(pady=(0, 20))
        
        if not sys.platform.startswith("linux"):
            win.grab_set()

    def abrir_configuracion(self):
        win = ctk.CTkToplevel(self.root)
        win.geometry("350x550")
        win.title(self.t("settings"))
        
        win.update()
        
        if sys.platform.startswith("linux"):
             win.attributes("-topmost", True)
        else:
             win.transient(self.root)
        
        self.aplicar_icono_ventana(win) 
        
        if sys.platform.startswith("linux"):
            win.withdraw()
            win.deiconify()
        
        curr_theme = self.themes.get(self.config["current_theme"], self.system_themes["Default Dark"])
        
        def update_settings_ui():
            t = self.themes.get(self.config["current_theme"], self.system_themes["Default Dark"])
            bg = t.get("bg", "#121212")
            text_col = t.get("text", "white")
            accent = t.get("accent", "#2ecc71")
            btn_text = t.get("button_text", "white")
            panel_col = t.get("panel", "#333")
            
            win.configure(fg_color=bg)
            lbl_lang.configure(text=self.t("lbl_lang"), text_color=text_col)
            lbl_theme.configure(text=self.t("lbl_theme_select"), text_color=text_col)
            lbl_upd.configure(text=self.t("lbl_update"), text_color=text_col)
            btn_edit.configure(text=self.t("btn_theme_editor"), fg_color=panel_col, text_color=text_col)
            btn_folder.configure(text=self.t("btn_open_folder"), fg_color=panel_col, text_color=text_col)
            btn_chk.configure(text=self.t("btn_check_update"), text_color=text_col)
            btn_close.configure(text=self.t("btn_close"), fg_color=accent, text_color=btn_text)
            
            for combo in [combo_lang, combo_theme]:
                combo.configure(
                    fg_color=accent, 
                    text_color=btn_text,
                    dropdown_fg_color=t.get("entry_bg", "#2D2D2D"),
                    dropdown_text_color=text_col,
                    dropdown_hover_color=panel_col
                )

        lbl_lang = ctk.CTkLabel(win, text="", font=ctk.CTkFont(weight="bold"))
        lbl_lang.pack(pady=(20, 5))
        
        def on_lang_change(choice):
            self.config["lang"] = "es" if choice == "Español" else "en"
            self.guardar_configuracion()
            self.actualizar_textos()
            update_settings_ui()

        combo_lang = ctk.CTkOptionMenu(win, values=["Español", "English"], command=on_lang_change)
        combo_lang.pack(pady=5)
        combo_lang.set("Español" if self.config["lang"] == "es" else "English")

        lbl_theme = ctk.CTkLabel(win, text="", font=ctk.CTkFont(weight="bold"))
        lbl_theme.pack(pady=(20, 5))
        
        theme_names = list(self.system_themes.keys()) + [f for f in os.listdir(self.themes_dir) if f.endswith(".json")]
        theme_names = [n.replace(".json", "") for n in theme_names]
        
        def on_theme_change(choice):
            self.config["current_theme"] = choice
            self.guardar_configuracion()
            self.aplicar_tema_actual()
            update_settings_ui()

        combo_theme = ctk.CTkOptionMenu(win, values=theme_names, command=on_theme_change)
        combo_theme.pack(pady=5)
        combo_theme.set(self.config.get("current_theme", "Default Dark"))

        btn_edit = ctk.CTkButton(win, text="", command=lambda: [win.destroy(), self.abrir_editor_temas()], border_width=1)
        btn_edit.pack(pady=10)
        
        btn_folder = ctk.CTkButton(win, text="", command=lambda: self.abrir_carpeta_sistema(self.themes_dir), border_width=1)
        btn_folder.pack(pady=5)

        ctk.CTkFrame(win, height=2, fg_color="gray50").pack(fill="x", padx=20, pady=20)
        
        lbl_upd = ctk.CTkLabel(win, text="", font=ctk.CTkFont(weight="bold"))
        lbl_upd.pack(pady=(0, 5))
        lbl_status = ctk.CTkLabel(win, text="", text_color="gray")
        lbl_status.pack(pady=5)
        btn_chk = ctk.CTkButton(win, text="", fg_color="transparent", border_width=1)
        btn_chk.pack(pady=5)
        btn_chk.configure(command=lambda: threading.Thread(target=self.verificar_actualizaciones, args=(btn_chk, lbl_status), daemon=True).start())
        btn_close = ctk.CTkButton(win, text="", command=win.destroy)
        btn_close.pack(side="bottom", pady=25)

        update_settings_ui()
        
        if not sys.platform.startswith("linux"):
            win.grab_set()

    def abrir_historial(self):
        win = ctk.CTkToplevel(self.root)
        win.geometry("600x450")
        win.title(self.t("history"))
        
        win.update()
        if sys.platform.startswith("linux"):
             win.attributes("-topmost", True)
        else:
             win.transient(self.root)
        
        self.aplicar_icono_ventana(win) 
        
        if sys.platform.startswith("linux"):
            win.withdraw()
            win.deiconify()
        
        t = self.themes.get(self.config.get("current_theme"), self.system_themes["Default Dark"])
        win.configure(fg_color=t.get("bg", "#121212"))
        
        ctk.CTkLabel(win, text=self.t("history"), font=ctk.CTkFont(size=20, weight="bold"), text_color=t.get("text", "white")).pack(pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=t.get("entry_bg", "#333"), foreground=t.get("text", "white"), fieldbackground=t.get("entry_bg", "#333"), borderwidth=0)
        style.map("Treeview", background=[("selected", t.get("accent", "#2ecc71"))])
        style.configure("Treeview.Heading", background=t.get("panel", "#222"), foreground=t.get("text", "white"), relief="flat")

        cols = ("date", "name", "format")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.heading("date", text=self.t("col_date"))
        tree.heading("name", text=self.t("col_name"))
        tree.heading("format", text=self.t("col_format"))
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        historial_data = []

        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    historial_data = json.load(f)
                    for item in historial_data: 
                        tree.insert("", "end", values=(item["fecha"], item["nombre"], item["formato"]))
            except: pass
        
        def abrir_ubicacion():
            seleccion = tree.selection()
            if seleccion:
                index = tree.index(seleccion[0])
                if index < len(historial_data):
                    ruta = historial_data[index].get("ruta")
                    if ruta and os.path.exists(ruta):
                        self.abrir_archivo_seleccionado(ruta)
                    else:
                        messagebox.showwarning("Error", "La ruta no existe.")

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text=self.t("btn_open_loc"), command=abrir_ubicacion, fg_color=t.get("accent"), hover_color=t.get("accent_hover"), text_color="white").pack(side="left", padx=5)
        
        def limpiar():
            if os.path.exists(self.history_file): os.remove(self.history_file)
            for i in tree.get_children(): tree.delete(i)
        
        ctk.CTkButton(btn_frame, text=self.t("btn_clear"), command=limpiar, fg_color="#c0392b", hover_color="#e74c3c", text_color="white").pack(side="left", padx=5)
        
        if not sys.platform.startswith("linux"):
            win.grab_set()

    def abrir_sobre_mi(self):
        win = ctk.CTkToplevel(self.root)
        win.geometry("300x300")
        win.title(self.t("about"))
        
        win.update()
        if sys.platform.startswith("linux"):
             win.attributes("-topmost", True)
        else:
             win.transient(self.root)
        
        self.aplicar_icono_ventana(win) 
        
        if sys.platform.startswith("linux"):
            win.withdraw()
            win.deiconify()
        
        t = self.themes.get(self.config.get("current_theme"), self.system_themes["Default Dark"])
        win.configure(fg_color=t.get("bg"))
        
        ctk.CTkLabel(win, text=self.t("about_title"), font=ctk.CTkFont(size=18, weight="bold"), text_color=t.get("text")).pack(pady=(20, 10))
        ctk.CTkLabel(win, text=self.t("about_desc"), text_color=t.get("text")).pack(pady=(0, 20))
        ctk.CTkButton(win, text=self.t("btn_carrd"), command=lambda: webbrowser.open("https://siratomos.carrd.co/"),
                               fg_color=t.get("accent"), hover_color=t.get("accent_hover"), text_color=t.get("button_text", "white"), width=200).pack(pady=10)
        
        if not sys.platform.startswith("linux"):
            win.grab_set()

    def mostrar_aviso_inicial(self):
        if not self.config.get("show_startup_msg", True): return
        
        win = ctk.CTkToplevel(self.root)
        win.geometry("400x300")
        win.title(self.t("aviso_title"))
        
        win.update()
        if sys.platform.startswith("linux"):
             win.attributes("-topmost", True)
        else:
             win.transient(self.root)
        
        self.aplicar_icono_ventana(win) 
        
        if sys.platform.startswith("linux"):
            win.withdraw()
            win.deiconify()
        
        t = self.themes.get(self.config.get("current_theme"), self.system_themes["Default Dark"])
        win.configure(fg_color=t.get("bg"))
        
        ctk.CTkLabel(win, text=self.t("aviso_body"), font=ctk.CTkFont(size=14), text_color=t.get("text")).pack(pady=30)
        var_chk = ctk.BooleanVar()
        ctk.CTkCheckBox(win, text=self.t("chk_nomore"), variable=var_chk, fg_color=t.get("accent"), text_color=t.get("text")).pack(pady=10)
        def close():
            if var_chk.get(): self.config["show_startup_msg"] = False; self.guardar_configuracion()
            win.destroy()
        ctk.CTkButton(win, text=self.t("btn_ok"), command=close, fg_color=t.get("accent"), text_color=t.get("button_text", "white")).pack(pady=10)
        
        if not sys.platform.startswith("linux"):
            win.grab_set()

    def parse_version(self, v_str):
        try: return [int(x) for x in v_str.lower().replace("v", "").split(".")]
        except: return [0]

    def verificar_actualizaciones(self, btn_widget, lbl_status):
        btn_widget.configure(state="disabled", text="Checking...")
        try:
            r = requests.get(self.API_RELEASE_URL, timeout=5)
            if r.status_code == 200:
                data = r.json()
                latest = data.get("tag_name", self.CURRENT_VERSION)
                if self.parse_version(latest) > self.parse_version(self.CURRENT_VERSION):
                    lbl_status.configure(text=f"{self.t('msg_newversion')} ({latest})", text_color="green")
                    btn_widget.configure(state="normal", text="Download", command=lambda: webbrowser.open(f"{self.REPO_URL}/releases/latest"))
                else:
                    lbl_status.configure(text=self.t("msg_uptodate"), text_color="gray")
                    btn_widget.configure(state="normal", text=self.t("btn_check_update"))
            else:
                lbl_status.configure(text="GitHub Error", text_color="red")
                btn_widget.configure(state="normal", text=self.t("btn_check_update"))
        except:
            lbl_status.configure(text=self.t("msg_neterror"), text_color="red")
            btn_widget.configure(state="normal", text=self.t("btn_check_update"))

if __name__ == "__main__":
    app = ctk.CTk()
    UniversalVideoDownloader(app)
    app.mainloop()