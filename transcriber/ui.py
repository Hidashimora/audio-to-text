from __future__ import annotations

import os
import shutil
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from uuid import uuid4

import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox

from .api import AssemblyAIClient
from .config import AppConfig, AppSettings, save_settings
from .utils import wrap_text_by_words


THEME_MAP = {"dark": "dark", "light": "light", "system": "system"}

TEXTS = {
    "ru": {
        "title": "Audio -> Text",
        "program_desc": "\u0411\u044b\u0441\u0442\u0440\u0430\u044f \u0438 \u0442\u043e\u0447\u043d\u0430\u044f \u0440\u0430\u0441\u0448\u0438\u0444\u0440\u043e\u0432\u043a\u0430 \u0430\u0443\u0434\u0438\u043e \u0438 \u0432\u0438\u0434\u0435\u043e \u0432 \u0442\u0435\u043a\u0441\u0442",
        "pick_file": "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0430\u0443\u0434\u0438\u043e \u0438\u043b\u0438 \u0432\u0438\u0434\u0435\u043e \u0444\u0430\u0439\u043b",
        "file_not_selected": "\u0424\u0430\u0439\u043b \u043d\u0435 \u0432\u044b\u0431\u0440\u0430\u043d",
        "select_file": "\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u0444\u0430\u0439\u043b",
        "convert": "\u041f\u0440\u0435\u043e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u0442\u044c",
        "open_txt": "\u041e\u0442\u043a\u0440\u044b\u0442\u044c TXT",
        "open_results_folder": "\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0430\u043f\u043a\u0443 results",
        "status_title": "\u0421\u0442\u0430\u0442\u0443\u0441",
        "status_waiting": "\u041e\u0436\u0438\u0434\u0430\u043d\u0438\u0435",
        "key_info_idle": "\u041a\u043b\u044e\u0447: -",
        "key_info_format": "\u041a\u043b\u044e\u0447 {current}/{total}",
        "features_title": "\u0412\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u0438",
        "features_text": "- \u0410\u0432\u0442\u043e\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u0435 \u044f\u0437\u044b\u043a\u0430\\n\\n- \u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430 \u043d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u0438\u0445 \u043a\u043b\u044e\u0447\u0435\u0439",
        "settings_title": "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438",
        "lang_title": "\u042f\u0437\u044b\u043a",
        "theme_title": "\u0422\u0435\u043c\u0430",
        "api_key_title": "\u041a\u043b\u044e\u0447 API",
        "multi_keys": "\u041d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u043a\u043b\u044e\u0447\u0435\u0439",
        "extra_keys": "\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0435 \u043a\u043b\u044e\u0447\u0438",
        "add_key": "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043a\u043b\u044e\u0447",
        "remove_key": "\u0423\u0434\u0430\u043b\u0438\u0442\u044c",
        "save": "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",
        "cancel": "\u041e\u0442\u043c\u0435\u043d\u0430",
        "status_file_selected": "\u0424\u0430\u0439\u043b \u0432\u044b\u0431\u0440\u0430\u043d",
        "status_preparing": "\u041f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u043a\u0430...",
        "status_uploading": "\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0444\u0430\u0439\u043b\u0430...",
        "status_job_creating": "\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0437\u0430\u0434\u0430\u0447\u0438...",
        "status_waiting_start": "\u041e\u0436\u0438\u0434\u0430\u043d\u0438\u0435 \u0437\u0430\u043f\u0443\u0441\u043a\u0430 \u0440\u0430\u0441\u043f\u043e\u0437\u043d\u0430\u0432\u0430\u043d\u0438\u044f...",
        "status_done_lang": "\u0413\u043e\u0442\u043e\u0432\u043e | \u044f\u0437\u044b\u043a: {lang}",
        "status_error": "\u041e\u0448\u0438\u0431\u043a\u0430",
        "warn_no_file_title": "\u041e\u0448\u0438\u0431\u043a\u0430",
        "warn_no_file_body": "\u0421\u043d\u0430\u0447\u0430\u043b\u0430 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0444\u0430\u0439\u043b",
        "warn_no_key_title": "\u041d\u0435\u0442 API \u043a\u043b\u044e\u0447\u0430",
        "warn_no_key_body": "\u0414\u043e\u0431\u0430\u0432\u044c\u0442\u0435 API \u043a\u043b\u044e\u0447 \u0432 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430\u0445.",
        "warn_no_output_title": "\u041d\u0435\u0442 \u0444\u0430\u0439\u043b\u0430",
        "warn_no_output_body": "TXT \u0444\u0430\u0439\u043b \u0435\u0449\u0435 \u043d\u0435 \u0441\u043e\u0437\u0434\u0430\u043d",
        "settings_saved": "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u044b",
    },
    "en": {
        "title": "Audio -> Text",
        "program_desc": "Fast and accurate audio/video transcription to text",
        "pick_file": "Choose an audio or video file",
        "file_not_selected": "No file selected",
        "select_file": "Select file",
        "convert": "Transcribe",
        "open_txt": "Open TXT",
        "open_results_folder": "Open results folder",
        "status_title": "Status",
        "status_waiting": "Waiting",
        "key_info_idle": "Key: -",
        "key_info_format": "Key {current}/{total}",
        "features_title": "Features",
        "features_text": "- Auto language detection\\n\\n- Multiple key support",
        "settings_title": "Settings",
        "lang_title": "Language",
        "theme_title": "Theme",
        "api_key_title": "API key",
        "multi_keys": "Multiple keys",
        "extra_keys": "Additional keys",
        "add_key": "Add key",
        "remove_key": "Remove",
        "save": "Save",
        "cancel": "Cancel",
        "status_file_selected": "File selected",
        "status_preparing": "Preparing...",
        "status_uploading": "Uploading file...",
        "status_job_creating": "Creating job...",
        "status_waiting_start": "Waiting for transcription to start...",
        "status_done_lang": "Done | language: {lang}",
        "status_error": "Error",
        "warn_no_file_title": "Error",
        "warn_no_file_body": "Select a file first",
        "warn_no_key_title": "No API key",
        "warn_no_key_body": "Add an API key in settings.",
        "warn_no_output_title": "No file",
        "warn_no_output_body": "TXT file has not been created yet",
        "settings_saved": "Settings saved",
    },
}

class TranscriberApp:
    def __init__(self, config: AppConfig, settings: AppSettings) -> None:
        self.config = config
        self.settings = settings

        self.selected_file: Path | None = None
        self.uploaded_temp_file: Path | None = None
        self.output_file: Path | None = None
        self.client: AssemblyAIClient | None = None

        self.github_icon_image: ctk.CTkImage | None = None
        self.settings_icon_image: ctk.CTkImage | None = None
        self.file_btn_icon_image: ctk.CTkImage | None = None
        self.convert_btn_icon_image: ctk.CTkImage | None = None
        self.open_btn_icon_image: ctk.CTkImage | None = None
        self.folder_btn_icon_image: ctk.CTkImage | None = None
        self.key_rows: list[tuple[ctk.CTkFrame, ctk.CTkEntry]] = []

        self.settings_overlay: ctk.CTkFrame | None = None
        self.settings_container: ctk.CTkScrollableFrame | None = None
        self.settings_close_x_btn: ctk.CTkButton | None = None
        self._active_palette: dict[str, str] | None = None
        self._key_info_current: int | None = None
        self._key_info_total: int | None = None

        ctk.set_appearance_mode(THEME_MAP.get(self.settings.theme, "dark"))
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Audio -> Text")
        self.root.geometry("980x680")
        self.root.resizable(False, False)
        self.root.minsize(980, 680)
        self.root.maxsize(980, 680)
        self.root.configure(fg_color="#0f1115")
        self._set_window_icon()

        self._build_ui()
        self._apply_texts()
        self._rebuild_client()

    def run(self) -> None:
        self.root.mainloop()

    def _text(self, key: str) -> str:
        lang = self.settings.language if self.settings.language in TEXTS else "ru"
        value = TEXTS[lang][key]
        if isinstance(value, str):
            return value.replace("\\n", "\n")
        return value

    @staticmethod
    def _ui_font(size: int, weight: str = "normal") -> ctk.CTkFont:
        return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)

    def _resource_path(self, relative_path: str) -> Path:
        if hasattr(sys, "_MEIPASS"):
            return Path(getattr(sys, "_MEIPASS")) / relative_path
        return Path(__file__).resolve().parents[1] / relative_path

    def _set_window_icon(self) -> None:
        icon_path = self._resource_path("assets/icons/audio.ico")
        if not icon_path.exists():
            return
        try:
            self.root.iconbitmap(default=str(icon_path))
        except Exception:
            pass

    def _load_ctk_image(self, relative_path: str, size: tuple[int, int]) -> ctk.CTkImage | None:
        image_path = self._resource_path(relative_path)
        if not image_path.exists():
            return None
        try:
            image = Image.open(image_path).convert("RGBA")
            return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        except Exception:
            return None

    def _build_ui(self) -> None:
        self.main = ctk.CTkFrame(self.root, fg_color="#0f1115")
        self.main.pack(fill="both", expand=True, padx=18, pady=18)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        self.topbar = ctk.CTkFrame(self.main, height=74, corner_radius=22, fg_color="#12151b")
        self.topbar.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 14))
        self.topbar.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.topbar,
            text="",
            font=self._ui_font(28, "bold"),
            text_color="#f5f7fb",
        )
        self.title_label.pack(side="left", padx=24, pady=18)

        self.settings_icon_image = self._load_ctk_image("assets/icons/settings_icon.png", (18, 18))
        self.settings_button = ctk.CTkButton(
            self.topbar,
            text="",
            image=self.settings_icon_image,
            width=44,
            height=44,
            corner_radius=14,
            fg_color="#1a2230",
            hover_color="#243044",
            command=self._open_settings,
        )
        self.settings_button.pack(side="right", padx=20, pady=15)

        self.content = ctk.CTkFrame(self.main, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=0)
        self.content.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self.content, corner_radius=26, fg_color="#131720")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(6, 9), pady=6)

        self.right_panel = ctk.CTkFrame(self.content, width=270, corner_radius=26, fg_color="#131720")
        self.right_panel.grid(row=0, column=1, sticky="ns", padx=(9, 6), pady=6)
        self.right_panel.pack_propagate(False)

        self.upload_card = ctk.CTkFrame(
            self.left_panel,
            corner_radius=24,
            fg_color="#171b25",
            border_width=1,
            border_color="#2b2b2b",
        )
        self.upload_card.pack(fill="both", expand=True, padx=18, pady=18)

        self.icon_label = ctk.CTkLabel(
            self.upload_card,
            text="",
            font=self._ui_font(54, "bold"),
            text_color="#76a8ff",
        )
        self.icon_label.pack(pady=(10, 4))

        self.headline = ctk.CTkLabel(
            self.upload_card,
            text="",
            font=self._ui_font(24, "bold"),
            text_color="#f4f7fb",
        )
        self.headline.pack(pady=(0, 4))

        self.subheadline = ctk.CTkLabel(
            self.upload_card,
            text="",
            font=self._ui_font(14),
            text_color="#98a2b3",
            justify="center",
            wraplength=620,
        )
        self.subheadline.pack(pady=(0, 8))

        self.file_name_label = ctk.CTkLabel(
            self.upload_card,
            text="",
            font=self._ui_font(15, "bold"),
            text_color="#d8deea",
            wraplength=600,
        )
        self.file_name_label.pack(pady=(0, 8))

        self.buttons_row = ctk.CTkFrame(self.upload_card, fg_color="transparent")
        self.buttons_row.pack(pady=(6, 8))

        self.select_button = ctk.CTkButton(
            self.buttons_row,
            text="",
            command=self.select_file,
            width=200,
            height=48,
            corner_radius=16,
            fg_color="#3478f6",
            hover_color="#4b89fb",
            text_color="white",
            font=self._ui_font(15, "bold"),
        )
        self.file_btn_icon_image = self._load_ctk_image("assets/icons/btn_file.png", (18, 18))
        self.select_button.configure(image=self.file_btn_icon_image, compound="left")
        self.select_button.pack(side="left", padx=8)

        self.convert_button = ctk.CTkButton(
            self.buttons_row,
            text="",
            command=self.start_transcription,
            width=200,
            height=48,
            corner_radius=16,
            fg_color="#15a86b",
            hover_color="#22c17d",
            text_color="white",
            font=self._ui_font(15, "bold"),
        )
        self.convert_btn_icon_image = self._load_ctk_image("assets/icons/btn_convert.png", (18, 18))
        self.convert_button.configure(image=self.convert_btn_icon_image, compound="left")
        self.convert_button.pack(side="left", padx=8)

        self.open_button = ctk.CTkButton(
            self.upload_card,
            text="",
            command=self.open_txt,
            state="disabled",
            width=260,
            height=48,
            corner_radius=16,
            fg_color="#7c5cff",
            hover_color="#9377ff",
            text_color="white",
            font=self._ui_font(15, "bold"),
        )
        self.open_btn_icon_image = self._load_ctk_image("assets/icons/btn_open.png", (18, 18))
        self.open_button.configure(image=self.open_btn_icon_image, compound="left")
        self.open_button.pack(pady=(6, 4))

        self.open_folder_button = ctk.CTkButton(
            self.upload_card,
            text="",
            command=self.open_results_folder,
            width=260,
            height=42,
            corner_radius=14,
            fg_color="#3c4f73",
            hover_color="#4b618d",
            text_color="white",
            font=self._ui_font(14, "bold"),
            anchor="center",
        )
        self.folder_btn_icon_image = self._load_ctk_image("assets/icons/btn_folder.png", (18, 18))
        self.open_folder_button.configure(image=self.folder_btn_icon_image, compound="left")
        self.open_folder_button.pack(pady=(0, 8))

        self.info_title = ctk.CTkLabel(
            self.right_panel,
            text="",
            font=self._ui_font(22, "bold"),
            text_color="#f4f7fb",
        )
        self.info_title.pack(anchor="w", padx=20, pady=(22, 8))

        self.status_badge = ctk.CTkFrame(self.right_panel, corner_radius=18, fg_color="#1c1c1f")
        self.status_badge.pack(fill="x", padx=16, pady=(0, 14))

        self.status_label = ctk.CTkLabel(
            self.status_badge,
            text="",
            font=self._ui_font(15, "bold"),
            text_color="#d6d6d6",
        )
        self.status_label.pack(padx=14, pady=14)

        self.key_info_label = ctk.CTkLabel(
            self.right_panel,
            text="",
            font=self._ui_font(12, "bold"),
            text_color="#8f98a8",
        )
        self.key_info_label.pack(anchor="w", padx=20, pady=(0, 10))

        self.tips_title = ctk.CTkLabel(
            self.right_panel,
            text="",
            font=self._ui_font(18, "bold"),
            text_color="#f4f7fb",
        )
        self.tips_title.pack(anchor="w", padx=20, pady=(14, 8))

        self.tips_box = ctk.CTkLabel(
            self.right_panel,
            text="",
            width=220,
            corner_radius=18,
            fg_color="#171b25",
            font=self._ui_font(13),
            text_color="#b8c1cf",
            justify="left",
            anchor="nw",
            wraplength=210,
        )
        self.tips_box.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        self.footer_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, sticky="ew", pady=(0, 0))
        self.footer_frame.grid_columnconfigure(0, weight=1)

        self.github_icon_image = self._load_ctk_image("assets/icons/github_icon.png", (14, 14))
        self.footer_button = ctk.CTkButton(
            self.footer_frame,
            text="Hidashimora",
            image=self.github_icon_image,
            compound="left",
            anchor="center",
            command=self._open_github,
            width=190,
            height=30,
            corner_radius=12,
            fg_color="transparent",
            hover_color="#1a1e27",
            text_color="#9aa7bd",
            font=self._ui_font(12, "bold"),
            border_width=0,
        )
        self.footer_button.grid(row=0, column=0)

        self._build_settings_overlay()
        self._apply_theme_colors()

    def _build_settings_overlay(self) -> None:
        self.settings_overlay = ctk.CTkFrame(
            self.main,
            corner_radius=0,
            fg_color="#0f141d",
            border_width=1,
            border_color="#2a3242",
        )
        header = ctk.CTkFrame(self.settings_overlay, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 8))

        self.settings_title_label = ctk.CTkLabel(
            header,
            text=self._text("settings_title"),
            font=self._ui_font(20, "bold"),
            text_color="#f5f7fb",
        )
        self.settings_title_label.pack(side="left")

        self.settings_close_x_btn = ctk.CTkButton(
            header,
            text="x",
            width=34,
            height=30,
            fg_color="#2f3645",
            hover_color="#454e64",
            command=self._close_settings,
        )
        self.settings_close_x_btn.pack(side="right")

        self.settings_container = ctk.CTkScrollableFrame(self.settings_overlay, fg_color="#121926")
        self.settings_container.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        self.settings_overlay.place_forget()

    def _apply_texts(self) -> None:
        self.root.title(self._text("title"))
        self.title_label.configure(text=self._text("title"))
        self.headline.configure(text=self._text("pick_file"))
        self.subheadline.configure(text=self._text("program_desc"))
        self.file_name_label.configure(text=self.selected_file.name if self.selected_file else self._text("file_not_selected"))
        self.select_button.configure(text=self._text("select_file"))
        self.convert_button.configure(text=self._text("convert"))
        self.open_button.configure(text=self._text("open_txt"))
        self.open_folder_button.configure(text=self._text("open_results_folder"))
        self.info_title.configure(text=self._text("status_title"))
        self.tips_title.configure(text=self._text("features_title"))
        self.settings_title_label.configure(text=self._text("settings_title"))

        self.tips_box.configure(text=self._text("features_text"))
        if self._key_info_current is not None and self._key_info_total is not None:
            self.key_info_label.configure(
                text=self._text("key_info_format").format(
                    current=self._key_info_current,
                    total=self._key_info_total,
                )
            )
        else:
            self.key_info_label.configure(text=self._text("key_info_idle"))

        if self.status_label.cget("text") in {"", TEXTS["ru"]["status_waiting"], TEXTS["en"]["status_waiting"]}:
            self.status_label.configure(text=self._text("status_waiting"))

    def _ui_call(self, callback) -> None:
        self.root.after(0, callback)

    def _set_status(self, text: str) -> None:
        self._ui_call(lambda: self.status_label.configure(text=text))

    def _set_key_info(self, current: int, total: int) -> None:
        self._key_info_current = current
        self._key_info_total = total
        text = self._text("key_info_format").format(current=current, total=total)
        self._ui_call(lambda: self.key_info_label.configure(text=text))

    def _reset_key_info(self) -> None:
        self._key_info_current = None
        self._key_info_total = None
        self._ui_call(lambda: self.key_info_label.configure(text=self._text("key_info_idle")))

    def _set_convert_enabled(self, enabled: bool) -> None:
        self._ui_call(lambda: self.convert_button.configure(state="normal" if enabled else "disabled"))

    def _set_open_enabled(self, enabled: bool) -> None:
        self._ui_call(lambda: self.open_button.configure(state="normal" if enabled else "disabled"))

    def _show_error(self, text: str) -> None:
        self._ui_call(lambda: messagebox.showerror(self._text("status_error"), text))

    def _reset_status_badge(self) -> None:
        self._ui_call(lambda: self.status_badge.configure(fg_color="#1c1c1f"))
        self._ui_call(lambda: self.status_label.configure(text_color="#d6d6d6"))

    def _show_success_state(self) -> None:
        self.status_badge.configure(fg_color="#163d2a")
        self.status_label.configure(text_color="#7dffb2")
        self.root.after(1200, self._reset_status_badge)

    def _pulse_card(self) -> None:
        self.upload_card.configure(border_width=2, border_color="#4f8cff")
        self.root.after(180, lambda: self.upload_card.configure(border_width=1, border_color="#2b2b2b"))

    def _cleanup_temp_file(self) -> None:
        if self.uploaded_temp_file and self.uploaded_temp_file.exists():
            try:
                self.uploaded_temp_file.unlink()
            except OSError:
                pass
        self.uploaded_temp_file = None

    def _cleanup_uploads_folder(self) -> None:
        self.config.upload_folder.mkdir(parents=True, exist_ok=True)
        for item in self.config.upload_folder.iterdir():
            if item.is_file():
                try:
                    item.unlink()
                except OSError:
                    pass

    def _open_github(self) -> None:
        webbrowser.open_new_tab("https://github.com/Hidashimora")

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        value = hex_color.lstrip("#")
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)

    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _blend_hex(self, left: str, right: str, alpha: float) -> str:
        lr, lg, lb = self._hex_to_rgb(left)
        rr, rg, rb = self._hex_to_rgb(right)
        rgb = (
            int(lr + (rr - lr) * alpha),
            int(lg + (rg - lg) * alpha),
            int(lb + (rb - lb) * alpha),
        )
        return self._rgb_to_hex(rgb)

    def _paint_palette(self, palette: dict[str, str]) -> None:
        self.root.configure(fg_color=palette["root"])
        self.main.configure(fg_color=palette["main"])
        self.topbar.configure(fg_color=palette["topbar"])
        self.left_panel.configure(fg_color=palette["panel"])
        self.right_panel.configure(fg_color=palette["panel"])
        self.upload_card.configure(fg_color=palette["card"], border_color=palette["card_border"])
        self.status_badge.configure(fg_color=palette["status_badge"])
        self.tips_box.configure(fg_color=palette["tips_bg"])
        self.title_label.configure(text_color=palette["text_main"])
        self.headline.configure(text_color=palette["text_main"])
        self.file_name_label.configure(text_color=palette["text_main"])
        self.subheadline.configure(text_color=palette["text_muted"])
        self.info_title.configure(text_color=palette["text_main"])
        self.tips_title.configure(text_color=palette["text_main"])
        self.status_label.configure(text_color=palette["status_text"])
        self.key_info_label.configure(text_color=palette["text_muted"])
        self.footer_button.configure(text_color=palette["link_text"])
        self.settings_button.configure(fg_color=palette["icon_btn_bg"], hover_color=palette["icon_btn_hover"])

        if self.settings_close_x_btn is not None:
            self.settings_close_x_btn.configure(
                fg_color=palette["icon_btn_bg"],
                hover_color=palette["icon_btn_hover"],
                text_color=palette["text_main"],
            )

        if self.settings_overlay is not None:
            self.settings_overlay.configure(fg_color=palette["settings_overlay"], border_color=palette["card_border"])
        if self.settings_container is not None:
            self.settings_container.configure(fg_color=palette["settings_container"])

    def _apply_theme_colors(self, animated: bool = False) -> None:
        mode = ctk.get_appearance_mode().lower()
        is_light = mode == "light"

        palette = {
            "root": "#edf1f7" if is_light else "#0f1115",
            "main": "#edf1f7" if is_light else "#0f1115",
            "topbar": "#ffffff" if is_light else "#12151b",
            "panel": "#ffffff" if is_light else "#131720",
            "card": "#f7f9fd" if is_light else "#171b25",
            "card_border": "#d5dbe8" if is_light else "#2b2b2b",
            "status_badge": "#e8edf6" if is_light else "#1c1c1f",
            "tips_bg": "#f2f6fd" if is_light else "#171b25",
            "settings_overlay": "#f3f7ff" if is_light else "#0f141d",
            "settings_container": "#ffffff" if is_light else "#121926",
            "text_main": "#111827" if is_light else "#f4f7fb",
            "text_muted": "#4b5563" if is_light else "#98a2b3",
            "status_text": "#374151" if is_light else "#d6d6d6",
            "link_text": "#334155" if is_light else "#9aa7bd",
            "icon_btn_bg": "#e2e8f0" if is_light else "#1a2230",
            "icon_btn_hover": "#cbd5e1" if is_light else "#243044",
        }

        if animated and self._active_palette is not None:
            start = self._active_palette
            steps = 7

            def frame(step: int) -> None:
                alpha = step / steps
                mixed: dict[str, str] = {}
                for key, target in palette.items():
                    source = start.get(key, target)
                    mixed[key] = self._blend_hex(source, target, alpha)
                self._paint_palette(mixed)
                if step < steps:
                    self.root.after(16, lambda: frame(step + 1))
                else:
                    self._active_palette = palette

            frame(0)
            return

        self._paint_palette(palette)
        self._active_palette = palette

    def _attach_entry_edit_bindings(self, entry: ctk.CTkEntry) -> None:
        native_entry = getattr(entry, "_entry", entry)

        def on_paste(_event=None):
            try:
                text = self.root.clipboard_get()
                native_entry.insert("insert", text)
            except Exception:
                pass
            return "break"

        def on_copy(_event=None):
            try:
                selected = native_entry.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected)
            except Exception:
                pass
            return "break"

        def on_cut(_event=None):
            try:
                selected = native_entry.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected)
                native_entry.delete("sel.first", "sel.last")
            except Exception:
                pass
            return "break"

        def show_menu(event):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Р’СЃС‚Р°РІРёС‚СЊ", command=on_paste)
            menu.add_command(label="РљРѕРїРёСЂРѕРІР°С‚СЊ", command=on_copy)
            menu.add_command(label="Р’С‹СЂРµР·Р°С‚СЊ", command=on_cut)
            menu.tk_popup(event.x_root, event.y_root)
            return "break"

        def on_ctrl_keypress(event):
            keycode = int(getattr(event, "keycode", -1))
            if keycode == 86:  # V key
                return on_paste()
            if keycode == 67:  # C key
                return on_copy()
            if keycode == 88:  # X key
                return on_cut()

            key = (event.keysym or "").lower()
            if key == "v":
                return on_paste()
            if key == "c":
                return on_copy()
            if key == "x":
                return on_cut()
            return None

        native_entry.bind("<Control-v>", on_paste)
        native_entry.bind("<Control-V>", on_paste)
        native_entry.bind("<Shift-Insert>", on_paste)
        native_entry.bind("<Control-c>", on_copy)
        native_entry.bind("<Control-C>", on_copy)
        native_entry.bind("<Control-x>", on_cut)
        native_entry.bind("<Control-X>", on_cut)
        native_entry.bind("<Control-KeyPress>", on_ctrl_keypress)
        native_entry.bind("<Button-3>", show_menu)

    def _rebuild_client(self) -> None:
        keys: list[str] = []
        primary = self.settings.primary_api_key.strip()
        extras = [key.strip() for key in self.settings.extra_api_keys if key.strip()]

        if self.settings.use_multiple_keys:
            if primary:
                keys.append(primary)
            for key in extras:
                if key not in keys:
                    keys.append(key)
        else:
            single_key = primary or (extras[0] if extras else "")
            if single_key:
                keys = [single_key]

        self.client = AssemblyAIClient(
            api_keys=keys,
            use_multiple_keys=self.settings.use_multiple_keys,
            poll_interval_seconds=self.config.poll_interval_seconds,
            polling_timeout_seconds=self.config.transcription_timeout_seconds,
            key_info_callback=self._set_key_info,
        )

    def open_txt(self) -> None:
        if self.output_file and self.output_file.exists():
            os.startfile(str(self.output_file.resolve()))
            return
        messagebox.showwarning(self._text("warn_no_output_title"), self._text("warn_no_output_body"))

    def open_results_folder(self) -> None:
        self.config.result_folder.mkdir(parents=True, exist_ok=True)
        os.startfile(str(self.config.result_folder.resolve()))

    def select_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title=self._text("pick_file"),
            filetypes=[("Audio/Video Files", "*.mp3 *.wav *.m4a *.mp4 *.mov *.flac")],
        )
        if not file_path:
            return

        self.selected_file = Path(file_path)
        self.file_name_label.configure(text=self.selected_file.name)
        self._set_status(self._text("status_file_selected"))
        self._set_open_enabled(False)
        self._reset_status_badge()
        self._pulse_card()

    def start_transcription(self) -> None:
        if not self.selected_file:
            messagebox.showwarning(self._text("warn_no_file_title"), self._text("warn_no_file_body"))
            return

        if self.client is None or not self.client.has_keys():
            messagebox.showwarning(self._text("warn_no_key_title"), self._text("warn_no_key_body"))
            return

        self.output_file = None
        self._reset_status_badge()
        self._reset_key_info()
        self._set_convert_enabled(False)
        self._set_open_enabled(False)
        self._set_status(self._text("status_preparing"))

        worker = threading.Thread(target=self._process_transcription, daemon=True)
        worker.start()

    def _process_transcription(self) -> None:
        try:
            source_file = self.selected_file
            if source_file is None:
                raise RuntimeError(self._text("warn_no_file_body"))

            temp_name = f"upload_{uuid4().hex}{source_file.suffix.lower()}"
            temp_target = self.config.upload_folder / temp_name
            self.uploaded_temp_file = temp_target
            shutil.copy2(source_file, temp_target)

            if self.client is None:
                raise RuntimeError(self._text("warn_no_key_body"))

            self._set_status(self._text("status_uploading"))
            audio_url = self.client.upload_file(temp_target)

            self._set_status(self._text("status_job_creating"))
            transcript_id = self.client.request_transcription(audio_url)

            self._set_status(self._text("status_waiting_start"))
            result = self.client.wait_for_result(transcript_id, self._set_status)

            wrapped_text = wrap_text_by_words(result.text, self.config.words_per_line)
            output_file = self.config.result_folder / f"{source_file.stem}_{uuid4().hex}.txt"
            output_file.write_text(f"Language: {result.language_code}\n\n{wrapped_text}", encoding="utf-8")
            self.output_file = output_file

            self._set_status(self._text("status_done_lang").format(lang=result.language_code))
            self._set_open_enabled(True)
            self._ui_call(self._show_success_state)
        except Exception as exc:
            self._reset_status_badge()
            self._set_status(self._text("status_error"))
            self._show_error(str(exc))
        finally:
            self._cleanup_temp_file()
            self._cleanup_uploads_folder()
            self._set_convert_enabled(True)

    def _open_settings(self) -> None:
        if self.settings_overlay is None or self.settings_container is None:
            return

        if self.settings_overlay.winfo_ismapped():
            self._close_settings()
            return

        for child in self.settings_container.winfo_children():
            child.destroy()
        self.key_rows = []

        self.settings_title_label.configure(text=self._text("settings_title"))
        self.settings_overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.76, relheight=0.88)
        self.settings_overlay.lift()

        container = self.settings_container

        language_label = ctk.CTkLabel(container, text=self._text("lang_title"), font=self._ui_font(14, "bold"))
        language_label.pack(anchor="w", padx=14, pady=(14, 6))

        language_var = ctk.StringVar(value="\u0420\u0443\u0441\u0441\u043a\u0438\u0439" if self.settings.language == "ru" else "English")
        language_select = ctk.CTkSegmentedButton(
            container,
            values=["\u0420\u0443\u0441\u0441\u043a\u0438\u0439", "English"],
            variable=language_var,
        )
        language_select.pack(fill="x", padx=14)

        theme_label = ctk.CTkLabel(container, text=self._text("theme_title"), font=self._ui_font(14, "bold"))
        theme_label.pack(anchor="w", padx=14, pady=(14, 6))

        theme_values = [
            "\u0422\u0435\u043c\u043d\u0430\u044f / Dark",
            "\u0421\u0432\u0435\u0442\u043b\u0430\u044f / Light",
            "\u0421\u0438\u0441\u0442\u0435\u043c\u043d\u0430\u044f / System",
        ]
        theme_to_label = {
            "dark": theme_values[0],
            "light": theme_values[1],
            "system": theme_values[2],
        }
        label_to_theme = {value: key for key, value in theme_to_label.items()}
        theme_var = ctk.StringVar(value=theme_to_label.get(self.settings.theme, theme_values[0]))
        theme_menu = ctk.CTkOptionMenu(container, values=theme_values, variable=theme_var)
        theme_menu.pack(fill="x", padx=14)

        primary_key_label = ctk.CTkLabel(
            container, text=self._text("api_key_title"), font=self._ui_font(14, "bold")
        )
        primary_key_label.pack(anchor="w", padx=14, pady=(14, 6))

        primary_key_entry = ctk.CTkEntry(container, placeholder_text="aai_...", height=36)
        primary_key_entry.pack(fill="x", padx=14)
        self._attach_entry_edit_bindings(primary_key_entry)
        primary_key_entry.insert(0, self.settings.primary_api_key)

        multi_var = ctk.BooleanVar(value=self.settings.use_multiple_keys)
        multi_switch = ctk.CTkSwitch(container, text=self._text("multi_keys"), variable=multi_var)
        multi_switch.pack(anchor="w", padx=14, pady=(14, 6))

        extra_section = ctk.CTkFrame(container, fg_color="#171f2d", corner_radius=12)
        extra_title = ctk.CTkLabel(
            extra_section, text=self._text("extra_keys"), font=self._ui_font(14, "bold")
        )
        extra_title.pack(anchor="w", padx=10, pady=(10, 6))

        keys_frame = ctk.CTkScrollableFrame(extra_section, height=170, fg_color="#141b28")
        keys_frame.pack(fill="both", padx=10, pady=(0, 8), expand=False)

        pending_apply_job: str | None = None

        def collect_extra_keys() -> list[str]:
            extra_keys: list[str] = []
            primary_value = primary_key_entry.get().strip()
            for _, key_entry in self.key_rows:
                key = key_entry.get().strip()
                if key and key not in extra_keys and key != primary_value:
                    extra_keys.append(key)
            return extra_keys

        def apply_now(update_texts: bool = False, update_theme: bool = False) -> None:
            self.settings.language = "ru" if language_var.get() == "\u0420\u0443\u0441\u0441\u043a\u0438\u0439" else "en"
            self.settings.theme = label_to_theme.get(theme_var.get(), "dark")
            self.settings.primary_api_key = primary_key_entry.get().strip()
            self.settings.use_multiple_keys = bool(multi_var.get())
            self.settings.extra_api_keys = collect_extra_keys()

            if update_theme:
                ctk.set_appearance_mode(THEME_MAP.get(self.settings.theme, "dark"))
                self._apply_theme_colors(animated=True)
            if update_texts:
                self._apply_texts()
                language_label.configure(text=self._text("lang_title"))
                theme_label.configure(text=self._text("theme_title"))
                primary_key_label.configure(text=self._text("api_key_title"))
                multi_switch.configure(text=self._text("multi_keys"))
                extra_title.configure(text=self._text("extra_keys"))
                add_key_btn.configure(text=f"+ {self._text('add_key')}")
                close_btn.configure(text=self._text("cancel"))

            self._rebuild_client()
            save_settings(self.config.settings_path, self.settings)

        def schedule_apply(delay_ms: int = 220, update_texts: bool = False, update_theme: bool = False) -> None:
            nonlocal pending_apply_job
            if pending_apply_job is not None:
                try:
                    self.root.after_cancel(pending_apply_job)
                except Exception:
                    pass
                pending_apply_job = None

            def run_apply() -> None:
                nonlocal pending_apply_job
                pending_apply_job = None
                apply_now(update_texts=update_texts, update_theme=update_theme)

            pending_apply_job = self.root.after(delay_ms, run_apply)

        def remove_key_row(row: ctk.CTkFrame, entry: ctk.CTkEntry) -> None:
            for item in list(self.key_rows):
                if item[0] == row and item[1] == entry:
                    self.key_rows.remove(item)
                    break
            row.destroy()
            apply_now()

        def add_key_row(value: str = "") -> None:
            row = ctk.CTkFrame(keys_frame, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=4)

            entry = ctk.CTkEntry(row, placeholder_text="aai_...")
            entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
            self._attach_entry_edit_bindings(entry)
            if value:
                entry.insert(0, value)

            remove_btn = ctk.CTkButton(
                row,
                text=self._text("remove_key"),
                width=88,
                fg_color="#3a2022",
                hover_color="#542d30",
                command=lambda: remove_key_row(row, entry),
            )
            remove_btn.pack(side="right")
            self.key_rows.append((row, entry))

            entry.bind("<KeyRelease>", lambda _e: schedule_apply())
            entry.bind("<FocusOut>", lambda _e: apply_now())

        keys_actions = ctk.CTkFrame(extra_section, fg_color="transparent")
        keys_actions.pack(fill="x", padx=10, pady=(0, 10))

        add_key_btn = ctk.CTkButton(
            keys_actions,
            text=f"+ {self._text('add_key')}",
            width=150,
            command=lambda: (add_key_row(""), apply_now()),
        )
        add_key_btn.pack(side="left")

        for key in self.settings.extra_api_keys:
            add_key_row(key)
        if not self.settings.extra_api_keys:
            add_key_row("")

        def set_extra_visibility(enabled: bool) -> None:
            if enabled:
                if not extra_section.winfo_ismapped():
                    extra_section.pack(fill="x", padx=14, pady=(2, 12))
            else:
                if extra_section.winfo_ismapped():
                    extra_section.pack_forget()

        def on_multi_toggle() -> None:
            set_extra_visibility(bool(multi_var.get()))
            apply_now()

        multi_switch.configure(command=on_multi_toggle)
        set_extra_visibility(bool(multi_var.get()))

        primary_key_entry.bind("<KeyRelease>", lambda _e: schedule_apply())
        primary_key_entry.bind("<FocusOut>", lambda _e: apply_now())
        language_select.configure(command=lambda _v: apply_now(update_texts=True))
        theme_menu.configure(command=lambda _v: apply_now(update_theme=True))

        close_row = ctk.CTkFrame(container, fg_color="transparent")
        close_row.pack(fill="x", padx=14, pady=(8, 14))

        close_btn = ctk.CTkButton(
            close_row,
            text=self._text("cancel"),
            fg_color="#2a2f3a",
            hover_color="#3a4354",
            command=self._close_settings,
        )
        close_btn.pack(side="right")

    def _close_settings(self) -> None:
        if self.settings_overlay is not None:
            self.settings_overlay.place_forget()
