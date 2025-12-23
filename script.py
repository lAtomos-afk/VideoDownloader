import tkinter as tk
from tkinter import messagebox, filedialog, ttk, Toplevel
import yt_dlp
import os
import threading
import sys
import json
from datetime import datetime

def obtener_ruta_recurso(nombre_relativo):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nombre_relativo)
    return os.path.join(os.path.abspath("."), nombre_relativo)

class DescargadorUniversal:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x720")
        self.root.resizable(False, False)
        
        self.app_data_path = os.path.join(os.getenv('APPDATA'), "VideoDownloader")
        if not os.path.exists(self.app_data_path):
            os.makedirs(self.app_data_path)
            
        self.settings_file = os.path.join(self.app_data_path, "settings.json")
        self.history_file = os.path.join(self.app_data_path, "history.json")
        
        self.cargar_configuracion()
        
        self.ruta_destino = tk.StringVar()
        self.ruta_destino.set(os.path.join(os.path.expanduser("~"), "Music"))
        
        self.tipo_var = tk.StringVar(value="Audio")
        self.formato_var = tk.StringVar()
        self.calidad_var = tk.StringVar()

        self.rows = []
        self.active_bar = None
        self.active_status = None

        self.colores = {
            "light": {
                "bg_main": "#f5f6fa",
                "bg_header": "#2c3e50",
                "fg_header": "white",
                "fg_sub": "#bdc3c7",
                "text_main": "#2c3e50",
                "text_sec": "#7f8c8d",
                "input_bg": "white",
                "input_fg": "black",
                "border": "#dcdde1",
                "accent": "#27ae60",
                "row_bg": "white",
                "tree_bg": "white",
                "tree_fg": "black",
                "tree_sel": "#3498db"
            },
            "dark": {
                "bg_main": "#121212",
                "bg_header": "#000000",
                "fg_header": "#f5f6fa",
                "fg_sub": "#b2bec3",
                "text_main": "#f5f6fa",
                "text_sec": "#aaaaaa",
                "input_bg": "#333333",
                "input_fg": "white",
                "border": "#333333",
                "accent": "#27ae60", 
                "row_bg": "#1e1e1e",
                "tree_bg": "#1e1e1e",
                "tree_fg": "white",
                "tree_sel": "#27ae60"
            }
        }

        self.textos_dict = {
            "es": {
                "title": "Video Downloader",
                "save_in": "Guardar en:",
                "browse": "Examinar",
                "config_title": " Configuración de Descarga ",
                "mode": "Modo:",
                "audio_only": "Solo Audio",
                "video_audio": "Video + Audio",
                "format": "Formato:",
                "quality": "Calidad:",
                "instructions": "⬇ Ingresa los enlaces abajo (Presiona ENTER para agregar más)",
                "btn_download": "INICIAR DESCARGAS",
                "status_ready": "Listo para comenzar",
                "settings": "Configuración",
                "history": "Historial",
                "created_by": "Creado por SirAtomos",
                "settings_win_title": "Preferencias",
                "history_win_title": "Historial de Descargas",
                "lang_lbl": "Idioma:",
                "theme_lbl": "Tema:",
                "btn_save": "Guardar",
                "msg_success": "Proceso terminado con éxito.",
                "msg_error": "Error",
                "aviso_title": "Aviso Importante",
                "aviso_body": "¡Bienvenido a Video Downloader!\n\nSi decides compartir esta herramienta,\npor favor recuerda dar los créditos al creador: SirAtomos.",
                "chk_nomore": "No mostrar de nuevo",
                "btn_ok": "Entendido",
                "col_date": "Fecha",
                "col_name": "Nombre",
                "col_format": "Formato",
                "btn_clear": "Borrar Historial",
                "no_history": "No hay descargas recientes."
            },
            "en": {
                "title": "Video Downloader",
                "save_in": "Save to:",
                "browse": "Browse",
                "config_title": " Download Settings ",
                "mode": "Mode:",
                "audio_only": "Audio Only",
                "video_audio": "Video + Audio",
                "format": "Format:",
                "quality": "Quality:",
                "instructions": "⬇ Enter links below (Press ENTER to add more)",
                "btn_download": "START DOWNLOAD",
                "status_ready": "Ready to start",
                "settings": "Settings",
                "history": "History",
                "created_by": "Created by SirAtomos",
                "settings_win_title": "Preferences",
                "history_win_title": "Download History",
                "lang_lbl": "Language:",
                "theme_lbl": "Theme:",
                "btn_save": "Save",
                "msg_success": "Process finished successfully.",
                "msg_error": "Error",
                "aviso_title": "Important Notice",
                "aviso_body": "Welcome to Video Downloader!\n\nIf you share this tool, please remember\nto credit the creator: SirAtomos.",
                "chk_nomore": "Don't show again",
                "btn_ok": "Got it",
                "col_date": "Date",
                "col_name": "Name",
                "col_format": "Format",
                "btn_clear": "Clear History",
                "no_history": "No recent downloads."
            }
        }

        self.construir_interfaz()
        self.aplicar_tema_idioma()
        
        self.root.after(200, self.mostrar_aviso_inicial)

    def cargar_configuracion(self):
        self.config = {"theme": "light", "lang": "es", "show_startup_msg": True}
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
            
            historial.insert(0, registro) # Agregar al principio
            # Limitar a los últimos 100 registros
            historial = historial[:100]
            
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(historial, f, ensure_ascii=False, indent=4)
        except:
            pass

    def t(self, key):
        return self.textos_dict[self.config["lang"]].get(key, key)

    def construir_interfaz(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TCombobox", fieldbackground="white", background="white")
        self.style.configure("TProgressbar", thickness=20)

        self.header_frame = tk.Frame(self.root, height=80)
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        self.lbl_titulo = tk.Label(self.header_frame, font=("Segoe UI", 22, "bold"))
        self.lbl_titulo.pack(side="left", padx=20, pady=20)

        self.lbl_subtitulo = tk.Label(self.header_frame, text="v2.5", font=("Segoe UI", 10))
        self.lbl_subtitulo.pack(side="left", pady=(32, 20))

        # Contenedor botones header
        self.frame_botones_header = tk.Frame(self.header_frame, bg=self.header_frame.cget("bg"))
        self.frame_botones_header.pack(side="right", padx=20, pady=20)

        self.btn_history = tk.Button(self.frame_botones_header, command=self.abrir_historial, font=("Segoe UI", 9), relief="flat", cursor="hand2")
        self.btn_history.pack(side="left", padx=5)

        self.btn_settings = tk.Button(self.frame_botones_header, command=self.abrir_configuracion, font=("Segoe UI", 9), relief="flat", cursor="hand2")
        self.btn_settings.pack(side="left", padx=5)

        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)

        self.frame_dir = tk.Frame(self.main_container)
        self.frame_dir.pack(fill="x", pady=(0, 15))

        self.lbl_dir = tk.Label(self.frame_dir, font=("Segoe UI", 10, "bold"))
        self.lbl_dir.pack(side="left")

        self.entry_dir = tk.Entry(self.frame_dir, textvariable=self.ruta_destino, width=50, state="readonly", font=("Segoe UI", 10), bd=0, relief="flat", highlightthickness=1)
        self.entry_dir.pack(side="left", padx=10, ipady=5)

        self.btn_browse = tk.Button(self.frame_dir, command=self.seleccionar_carpeta, font=("Segoe UI", 9), fg="white", relief="flat", padx=15, pady=2, cursor="hand2")
        self.btn_browse.pack(side="left")

        self.frame_config = tk.LabelFrame(self.main_container, font=("Segoe UI", 10, "bold"), bd=1, relief="solid")
        self.frame_config.pack(fill="x", pady=(0, 20), ipady=5)

        self.config_inner = tk.Frame(self.frame_config)
        self.config_inner.pack(padx=10, pady=10)

        self.lbl_mode = tk.Label(self.config_inner, font=("Segoe UI", 10))
        self.lbl_mode.pack(side="left", padx=(0, 5))
        
        self.rb_audio = tk.Radiobutton(self.config_inner, variable=self.tipo_var, value="Audio", command=self.actualizar_opciones, font=("Segoe UI", 10))
        self.rb_audio.pack(side="left")
        
        self.rb_video = tk.Radiobutton(self.config_inner, variable=self.tipo_var, value="Video", command=self.actualizar_opciones, font=("Segoe UI", 10))
        self.rb_video.pack(side="left", padx=(0, 20))

        self.lbl_format = tk.Label(self.config_inner, font=("Segoe UI", 10))
        self.lbl_format.pack(side="left", padx=(0, 5))
        self.cb_formato = ttk.Combobox(self.config_inner, textvariable=self.formato_var, state="readonly", width=10, font=("Segoe UI", 10))
        self.cb_formato.pack(side="left", padx=(0, 20))

        self.lbl_quality = tk.Label(self.config_inner, font=("Segoe UI", 10))
        self.lbl_quality.pack(side="left", padx=(0, 5))
        self.cb_calidad = ttk.Combobox(self.config_inner, textvariable=self.calidad_var, state="readonly", width=18, font=("Segoe UI", 10))
        self.cb_calidad.pack(side="left")

        self.lbl_instructions = tk.Label(self.main_container, font=("Segoe UI", 10, "italic"))
        self.lbl_instructions.pack(anchor="w", pady=(0, 5))

        self.frame_canvas_border = tk.Frame(self.main_container, bd=1, relief="solid")
        self.frame_canvas_border.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.frame_canvas_border, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame_canvas_border, orient="vertical", command=self.canvas.yview)
        self.frame_links = tk.Frame(self.canvas)

        self.frame_links.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.frame_links, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.pack(side="right", fill="y")

        self.frame_actions = tk.Frame(self.root)
        self.frame_actions.pack(side="bottom", fill="x", padx=30, pady=(0, 10))

        self.btn_descargar = tk.Button(self.frame_actions, command=self.iniciar_descarga, font=("Segoe UI", 11, "bold"), fg="white", relief="flat", padx=30, pady=8, cursor="hand2")
        self.btn_descargar.pack(side="top", pady=10)

        self.lbl_global = tk.Label(self.frame_actions, font=("Segoe UI", 9))
        self.lbl_global.pack(side="top")

        self.footer_line = tk.Frame(self.root, height=25)
        self.footer_line.pack(side="bottom", fill="x")

        self.lbl_watermark = tk.Label(self.footer_line, font=("Segoe UI", 8, "italic"))
        self.lbl_watermark.pack(side="right", padx=15)

        self.actualizar_opciones()
        self.agregar_entry()

    def aplicar_tema_idioma(self):
        # Textos
        self.root.title(self.t("title"))
        self.lbl_titulo.config(text=self.t("title"))
        self.lbl_dir.config(text=self.t("save_in"))
        self.btn_browse.config(text=self.t("browse"))
        self.frame_config.config(text=self.t("config_title"))
        self.lbl_mode.config(text=self.t("mode"))
        self.rb_audio.config(text=self.t("audio_only"))
        self.rb_video.config(text=self.t("video_audio"))
        self.lbl_format.config(text=self.t("format"))
        self.lbl_quality.config(text=self.t("quality"))
        self.lbl_instructions.config(text=self.t("instructions"))
        self.btn_descargar.config(text=self.t("btn_download"))
        self.lbl_global.config(text=self.t("status_ready"))
        self.btn_settings.config(text=self.t("settings"))
        self.btn_history.config(text=self.t("history"))
        self.lbl_watermark.config(text=self.t("created_by"))

        # Colores
        c = self.colores[self.config["theme"]]
        
        self.root.configure(bg=c["bg_main"])
        self.header_frame.configure(bg=c["bg_header"])
        self.frame_botones_header.configure(bg=c["bg_header"])
        self.lbl_titulo.configure(bg=c["bg_header"], fg=c["fg_header"])
        self.lbl_subtitulo.configure(bg=c["bg_header"], fg=c["fg_sub"])
        
        self.btn_settings.configure(bg="#95a5a6", fg="white") 
        self.btn_history.configure(bg="#3498db", fg="white") # Botón historial azul

        self.main_container.configure(bg=c["bg_main"])
        self.frame_dir.configure(bg=c["bg_main"])
        self.lbl_dir.configure(bg=c["bg_main"], fg=c["text_main"])
        self.entry_dir.configure(bg=c["input_bg"], fg=c["input_fg"], readonlybackground=c["input_bg"], highlightbackground=c["border"])
        self.btn_browse.configure(bg="#95a5a6")

        self.frame_config.configure(bg=c["bg_main"], fg=c["text_main"])
        self.config_inner.configure(bg=c["bg_main"])
        self.lbl_mode.configure(bg=c["bg_main"], fg=c["text_main"])
        self.rb_audio.configure(bg=c["bg_main"], fg=c["text_main"], selectcolor=c["bg_main"], activebackground=c["bg_main"], activeforeground=c["text_main"])
        self.rb_video.configure(bg=c["bg_main"], fg=c["text_main"], selectcolor=c["bg_main"], activebackground=c["bg_main"], activeforeground=c["text_main"])
        self.lbl_format.configure(bg=c["bg_main"], fg=c["text_main"])
        self.lbl_quality.configure(bg=c["bg_main"], fg=c["text_main"])

        self.lbl_instructions.configure(bg=c["bg_main"], fg=c["text_sec"])
        self.frame_canvas_border.configure(bg=c["border"])
        self.canvas.configure(bg=c["row_bg"])
        self.frame_links.configure(bg=c["row_bg"])

        self.frame_actions.configure(bg=c["bg_main"])
        self.btn_descargar.configure(bg="#27ae60", activebackground="#219150")
        self.lbl_global.configure(bg=c["bg_main"], fg=c["text_sec"])

        self.footer_line.configure(bg=c["bg_header"])
        self.lbl_watermark.configure(bg=c["bg_header"], fg=c["fg_header"])

        for row in self.rows:
            row["frame"].configure(bg=c["row_bg"])
            row["entry"].configure(bg=c["input_bg"], fg=c["input_fg"], highlightbackground=c["border"])
            row["status"].configure(bg=c["row_bg"], fg=c["text_main"])
            
        # Configurar Estilo del Treeview (Historial)
        self.style.configure("Treeview", 
            background=c["tree_bg"], 
            foreground=c["tree_fg"], 
            fieldbackground=c["tree_bg"], 
            borderwidth=0
        )
        self.style.map("Treeview", background=[("selected", c["tree_sel"])], foreground=[("selected", "white")])
        self.style.configure("Treeview.Heading", font=('Segoe UI', 9, 'bold'))

    def mostrar_aviso_inicial(self):
        if not self.config.get("show_startup_msg", True):
            return

        aviso = Toplevel(self.root)
        aviso.title(self.t("aviso_title"))
        aviso.geometry("400x260")
        aviso.resizable(False, False)
        aviso.transient(self.root)
        aviso.grab_set()
        
        c = self.colores[self.config["theme"]]
        aviso.config(bg=c["bg_main"])

        tk.Label(aviso, text=self.t("aviso_body"), bg=c["bg_main"], fg=c["text_main"], font=("Segoe UI", 10), justify="center").pack(pady=20)
        
        var_nomostrar = tk.BooleanVar()
        chk = tk.Checkbutton(
            aviso, 
            text=self.t("chk_nomore"), 
            variable=var_nomostrar, 
            bg=c["bg_main"], 
            fg=c["text_main"], 
            selectcolor=c["bg_main"], 
            activebackground=c["bg_main"], 
            activeforeground=c["text_main"]
        )
        chk.pack(pady=10)

        def cerrar_aviso():
            if var_nomostrar.get():
                self.config["show_startup_msg"] = False
                self.guardar_configuracion()
            aviso.destroy()

        tk.Button(aviso, text=self.t("btn_ok"), command=cerrar_aviso, bg=c["accent"], fg="white", width=15, relief="flat").pack(pady=10)

    def abrir_historial(self):
        hist = Toplevel(self.root)
        hist.title(self.t("history_win_title"))
        hist.geometry("600x400")
        hist.transient(self.root)
        hist.grab_set()
        
        c = self.colores[self.config["theme"]]
        hist.config(bg=c["bg_main"])
        
        # Frame contenedor
        container = tk.Frame(hist, bg=c["bg_main"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titulo
        tk.Label(container, text=self.t("history"), font=("Segoe UI", 16, "bold"), bg=c["bg_main"], fg=c["text_main"]).pack(anchor="w", pady=(0, 10))
        
        # Treeview
        columns = ("date", "name", "format")
        tree = ttk.Treeview(container, columns=columns, show="headings", selectmode="browse")
        
        tree.heading("date", text=self.t("col_date"))
        tree.heading("name", text=self.t("col_name"))
        tree.heading("format", text=self.t("col_format"))
        
        tree.column("date", width=120, anchor="center")
        tree.column("name", width=300, anchor="w")
        tree.column("format", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar datos
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        tree.insert("", "end", values=(item["fecha"], item["nombre"], item["formato"]))
            except:
                pass
        
        # Botón borrar
        def borrar_historial():
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
                for i in tree.get_children():
                    tree.delete(i)
        
        btn_frame = tk.Frame(hist, bg=c["bg_main"])
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Button(btn_frame, text=self.t("btn_clear"), command=borrar_historial, bg="#e74c3c", fg="white", font=("Segoe UI", 9), relief="flat").pack(side="right")

    def abrir_configuracion(self):
        top = Toplevel(self.root)
        top.title(self.t("settings_win_title"))
        top.geometry("300x220")
        top.resizable(False, False)
        top.transient(self.root)
        top.grab_set()
        
        c = self.colores[self.config["theme"]]
        top.config(bg=c["bg_main"])

        tk.Label(top, text=self.t("lang_lbl"), bg=c["bg_main"], fg=c["text_main"], font=("Segoe UI", 10, "bold")).pack(pady=(20, 5))
        combo_lang = ttk.Combobox(top, values=["Español", "English"], state="readonly")
        combo_lang.pack()
        combo_lang.current(0 if self.config["lang"] == "es" else 1)

        tk.Label(top, text=self.t("theme_lbl"), bg=c["bg_main"], fg=c["text_main"], font=("Segoe UI", 10, "bold")).pack(pady=(20, 5))
        combo_theme = ttk.Combobox(top, values=["Light", "Dark"], state="readonly")
        combo_theme.pack()
        combo_theme.current(0 if self.config["theme"] == "light" else 1)

        def guardar():
            self.config["lang"] = "es" if combo_lang.current() == 0 else "en"
            self.config["theme"] = "light" if combo_theme.current() == 0 else "dark"
            self.guardar_configuracion()
            self.aplicar_tema_idioma()
            top.destroy()

        tk.Button(top, text=self.t("btn_save"), command=guardar, bg=c["accent"], fg="white", font=("Segoe UI", 10)).pack(pady=20)

    def actualizar_opciones(self):
        tipo = self.tipo_var.get()
        if tipo == "Audio":
            self.cb_formato['values'] = ["mp3", "flac", "wav", "ogg", "m4a"]
            self.cb_formato.current(0)
            self.cb_calidad['values'] = ["320 kbps", "256 kbps", "192 kbps", "128 kbps"]
            self.cb_calidad.current(0)
        else:
            self.cb_formato['values'] = ["mp4", "mkv"]
            self.cb_formato.current(0)
            self.cb_calidad['values'] = ["Best Available", "1080p", "720p", "480p", "360p"]
            self.cb_calidad.current(0)

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.ruta_destino.set(carpeta)

    def agregar_entry(self):
        c = self.colores[self.config["theme"]]

        row_frame = tk.Frame(self.frame_links, bg=c["row_bg"])
        row_frame.pack(fill="x", pady=5, padx=5)

        entry = tk.Entry(row_frame, width=58, font=("Segoe UI", 10), bg=c["input_bg"], fg=c["input_fg"], relief="flat", highlightthickness=1, highlightbackground=c["border"])
        entry.pack(side="left", padx=(0, 15), ipady=4)
        entry.bind("<Return>", lambda event: self.agregar_entry())
        entry.focus()

        progress = ttk.Progressbar(row_frame, orient="horizontal", length=200, mode="determinate")
        progress.pack(side="left", padx=(0, 15))

        status_label = tk.Label(row_frame, text="", width=20, anchor="w", font=("Segoe UI", 9), bg=c["row_bg"], fg=c["text_main"])
        status_label.pack(side="left")

        self.rows.append({"entry": entry, "bar": progress, "status": status_label, "frame": row_frame})
        self.root.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def reiniciar_ui(self):
        for row in self.rows:
            row["frame"].destroy()
        self.rows = []
        self.agregar_entry()
        self.lbl_global.config(text=self.t("status_ready"), fg=self.colores[self.config["theme"]]["text_sec"])

    def iniciar_descarga(self):
        if not self.ruta_destino.get():
            messagebox.showwarning("Aviso", "Selecciona una carpeta.")
            return

        valid_rows = [row for row in self.rows if row["entry"].get().strip()]
        if not valid_rows:
            messagebox.showwarning("Aviso", "Ingresa al menos un link.")
            return

        config_dl = {'tipo': self.tipo_var.get(), 'formato': self.formato_var.get(), 'calidad': self.calidad_var.get()}
        self.btn_descargar.config(state="disabled", bg="#bdc3c7")
        threading.Thread(target=self.procesar_lista, args=(valid_rows, config_dl), daemon=True).start()

    def hook_progreso(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            descargado = d.get('downloaded_bytes', 0)
            if total and self.active_bar:
                p = (descargado / total) * 100
                self.root.after(0, lambda: self.active_bar.config(value=p))
                self.root.after(0, lambda: self.active_status.config(text=f"{p:.0f}%"))

    def procesar_lista(self, rows, config):
        carpeta_final = self.ruta_destino.get()
        ffmpeg_dir = os.path.dirname(obtener_ruta_recurso("ffmpeg.exe"))

        opciones = {
            'outtmpl': os.path.join(carpeta_final, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_dir,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.hook_progreso],
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
            self.root.after(0, lambda: self.active_status.config(text="..."))
            
            url = row["entry"].get().strip()
            
            try:
                # Usamos extract_info con download=True para obtener metadatos y descargar al mismo tiempo
                with yt_dlp.YoutubeDL(opciones) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                # Guardar en historial
                titulo = info.get('title', 'Video Desconocido')
                self.registrar_historial(titulo, config['formato'])

                self.root.after(0, lambda: row["status"].config(text="✅", fg="#27ae60"))
            except:
                self.root.after(0, lambda: row["status"].config(text="❌", fg="#c0392b"))

        self.root.after(0, lambda: messagebox.showinfo(self.t("title"), self.t("msg_success")))
        
        self.root.after(0, lambda: self.lbl_global.config(text=self.t("msg_success")))
        self.root.after(0, lambda: self.btn_descargar.config(state="normal", bg="#27ae60"))
        self.root.after(0, self.reiniciar_ui)

if __name__ == "__main__":
    root = tk.Tk()
    app = DescargadorUniversal(root)
    root.mainloop()