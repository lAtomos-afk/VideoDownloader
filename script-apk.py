import flet as ft
import yt_dlp
import os
import sys
import requests
from datetime import datetime

def main(page: ft.Page):
    CURRENT_VERSION = "3.5"
    REPO_URL = "https://github.com/lAtomos-afk/VideoDownloader"
    API_RELEASE_URL = "https://api.github.com/repos/lAtomos-afk/VideoDownloader/releases/latest"

    page.title = "Video Downloader v3.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.window_width = 450
    page.window_height = 800
    page.padding = 0

    GREEN = "#2ecc71"
    GREEN_OPACITY = "#1A2ecc71"
    WHITE_OPACITY = "#1Affffff"
    DEFAULT_PATH = "/storage/emulated/0/Download"

    def parse_version(v_str):
        try:
            return [int(x) for x in v_str.lower().replace("v", "").split(".")]
        except:
            return [0]

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        page.bgcolor = ft.Colors.WHITE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.BLACK
        theme_icon.icon = ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
        page.update()

    def check_for_updates(e=None):
        update_btn.text = "Checking..."
        update_btn.disabled = True
        page.update()
        try:
            response = requests.get(API_RELEASE_URL, timeout=5)
            if response.status_code == 200:
                latest_data = response.json()
                latest_tag = latest_data.get("tag_name", CURRENT_VERSION)
                v_local = parse_version(CURRENT_VERSION)
                v_remote = parse_version(latest_tag)
                if v_remote > v_local:
                    version_info.value = f"New version available: {latest_tag}"
                    version_info.color = ft.Colors.AMBER
                    update_btn.text = "Download New APK"
                    update_btn.on_click = lambda _: page.launch_url(f"{REPO_URL}/releases/latest/download/VideoDownloader.apk")
                else:
                    version_info.value = "You are on the latest version"
                    version_info.color = GREEN
                    update_btn.text = "Up to date"
            else:
                version_info.value = "Error checking updates"
        except:
            version_info.value = "Network error"
        update_btn.disabled = False
        page.update()

    def add_to_history(title, format_type, quality):
        date_str = datetime.now().strftime("%d/%m %H:%M")
        entry = f"{date_str} | [{format_type} - {quality}] | {title}"
        current_history = page.client_storage.get("history") or []
        current_history.insert(0, entry)
        page.client_storage.set("history", current_history)
        load_history()

    def load_history():
        history_list.controls.clear()
        history_data = page.client_storage.get("history") or []
        if not history_data:
            history_list.controls.append(ft.Text("No history yet.", color=ft.Colors.GREY))
        else:
            for item in history_data:
                history_list.controls.append(
                    ft.Container(
                        content=ft.Text(item, size=11, color=ft.Colors.WHITE if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK),
                        padding=10, bgcolor=GREEN_OPACITY, border_radius=5
                    )
                )
        page.update()

    def clear_history(e):
        page.client_storage.remove("history")
        load_history()

    def format_changed(e):
        if format_dropdown.value == "Audio":
            quality_dropdown.options = [ft.dropdown.Option("Best")]
            quality_dropdown.value = "Best"
            quality_dropdown.disabled = True
        else:
            quality_dropdown.options = [
                ft.dropdown.Option("Best"),
                ft.dropdown.Option("1080p"),
                ft.dropdown.Option("720p"),
                ft.dropdown.Option("480p"),
                ft.dropdown.Option("360p")
            ]
            quality_dropdown.value = "Best"
            quality_dropdown.disabled = False
        page.update()

    def hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                progress_bar.value = float(p) / 100
                speed = d.get('_speed_str', 'N/A')
                status_text.value = f"Downloading: {d.get('_percent_str')} | Speed: {speed}"
                page.update()
            except: pass

    def start_batch_download(e):
        links = url_input.value.strip().split('\n')
        links = [l.strip() for l in links if l.strip()]
        if not links:
            url_input.error_text = "Paste links first"
            page.update()
            return
        url_input.error_text = None
        download_btn.disabled = True
        for i, url in enumerate(links):
            download_btn.text = f"DOWNLOADING {i+1}/{len(links)}..."
            progress_bar.value = 0
            status_text.value = "Starting..."
            status_text.color = GREEN
            page.update()
            
            selected_format = format_dropdown.value
            selected_quality = quality_dropdown.value
            
            ydl_opts = {
                'outtmpl': f'{DEFAULT_PATH}/%(title)s.%(ext)s',
                'progress_hooks': [hook],
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'quiet': True,
                'no_warnings': True,
                'restrictfilenames': True,
                'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            }
            
            if selected_format == "Audio":
                ydl_opts.update({'format': 'bestaudio[ext=m4a]/bestaudio'})
            else:
                if selected_quality == "Best":
                    ydl_opts.update({'format': 'best'})
                else:
                    target_height = selected_quality.replace("p", "")
                    ydl_opts.update({'format': f'best[height<={target_height}]'})
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', 'Unknown Title')
                    
                    if selected_format == "Audio":
                        try:
                            downloaded_path = info.get('requested_downloads', [{}])[0].get('filepath')
                            if downloaded_path and downloaded_path.endswith('.m4a'):
                                new_path = downloaded_path.rsplit('.', 1)[0] + '.mp3'
                                os.rename(downloaded_path, new_path)
                                status_text.value = f"Saved as MP3: {title[:15]}..."
                            else:
                                status_text.value = f"Saved: {title[:20]}..."
                        except:
                            status_text.value = f"Saved: {title[:20]}..."
                    else:
                        status_text.value = f"Saved: {title[:20]}..."
                        
                    add_to_history(title, selected_format, selected_quality)
                    
            except Exception as ex:
                status_text.value = f"Err: {str(ex)[:15]}..."
                status_text.color = ft.Colors.RED
            page.update()
        download_btn.disabled = False
        download_btn.text = "START DOWNLOAD"
        page.update()

    theme_icon = ft.IconButton(ft.Icons.LIGHT_MODE, on_click=toggle_theme)
    app_bar = ft.Row([ft.Text("Video Downloader", size=20, weight=ft.FontWeight.BOLD, color=GREEN), theme_icon], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    url_input = ft.TextField(label="Paste Links", multiline=True, min_lines=3, bgcolor=WHITE_OPACITY, border_color=GREEN, cursor_color=GREEN)
    format_dropdown = ft.Dropdown(label="Format", width=150, options=[ft.dropdown.Option("Audio"), ft.dropdown.Option("Video")], value="Audio", border_color=GREEN, on_change=format_changed)
    quality_dropdown = ft.Dropdown(label="Quality", width=150, options=[ft.dropdown.Option("Best")], value="Best", border_color=GREEN, disabled=True)
    status_text = ft.Text("Ready.", color=GREEN, size=12, font_family="monospace")
    progress_bar = ft.ProgressBar(width=400, color=GREEN, bgcolor="#333333", value=0)
    download_btn = ft.ElevatedButton(text="START DOWNLOAD", color=ft.Colors.WHITE, bgcolor=GREEN, width=400, height=50, on_click=start_batch_download)
    history_list = ft.Column(scroll="auto", height=350)
    version_info = ft.Text(f"Current version: {CURRENT_VERSION}", size=12, color=ft.Colors.GREY)
    update_btn = ft.OutlinedButton("Check for Updates", icon=ft.Icons.SEARCH, on_click=check_for_updates, style=ft.ButtonStyle(color=GREEN))
    settings_content = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(height=40),
            ft.Icon(ft.Icons.SYSTEM_UPDATE_ALT, color=GREEN, size=50),
            ft.Container(height=20),
            ft.Text("Software Update", size=18, weight=ft.FontWeight.BOLD),
            version_info,
            ft.Container(height=30),
            update_btn,
            ft.Container(height=40),
            ft.Text("Developer: SirAtomos", size=10, color=ft.Colors.GREY_700)
        ]
    )
    tabs = ft.Tabs(
        selected_index=0, indicator_color=GREEN, label_color=GREEN,
        tabs=[
            ft.Tab(text="Downloader", icon=ft.Icons.DOWNLOAD, content=ft.Column([ft.Container(height=10), url_input, ft.Row([format_dropdown, quality_dropdown], alignment=ft.MainAxisAlignment.CENTER), status_text, progress_bar, download_btn], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
            ft.Tab(text="History", icon=ft.Icons.HISTORY, content=ft.Column([ft.TextButton("Clear History", on_click=clear_history, style=ft.ButtonStyle(color=ft.Colors.RED)), history_list])),
            ft.Tab(text="Settings", icon=ft.Icons.SETTINGS, content=settings_content),
        ], expand=True
    )
    watermark = ft.Container(content=ft.Text("SirAtomos", color=GREEN, size=12, weight=ft.FontWeight.BOLD, opacity=0.8), padding=ft.padding.only(right=15, bottom=10), alignment=ft.alignment.bottom_right)
    page.add(ft.Column([ft.Container(content=ft.Column([app_bar, tabs]), padding=20, expand=True), watermark], expand=True))
    load_history()

ft.app(target=main)