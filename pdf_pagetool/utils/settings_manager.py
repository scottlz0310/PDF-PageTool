"""
Settings Manager Module
アプリケーション設定の管理
"""

import json
import os
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger


class SettingsManager:
    """設定管理クラス"""

    def __init__(self, app_name: str = "PDF-PageTool"):
        self.app_name = app_name
        self.logger = get_logger("SettingsManager")
        self.settings_file = self._get_settings_file_path()
        self._default_settings = self._get_default_settings()
        self._current_settings: dict[str, Any] = {}

        self.load_settings()

    def _get_settings_file_path(self) -> Path:
        """設定ファイルのパスを取得"""
        # OSに応じた適切な設定ディレクトリを選択
        if os.name == "nt":  # Windows
            config_dir = Path(os.environ.get("APPDATA", "")) / self.app_name
        else:  # Linux/macOS
            config_dir = Path.home() / ".config" / self.app_name

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "settings.json"

    def _get_default_settings(self) -> dict[str, Any]:
        """デフォルト設定を取得"""
        return {
            # 一般設定
            "output_folder": str(Path.home() / "Documents"),
            "filename_template": "output_{datetime}",
            "auto_save": False,
            "confirm_exit": True,
            "remember_window": True,
            # UI設定
            "theme": "ライト",
            "thumbnail_size": 160,
            "thumbnail_quality": "中",
            "show_page_numbers": True,
            "show_file_names": True,
            "show_tooltips": True,
            # ウィンドウ設定
            "window_width": 1200,
            "window_height": 800,
            "window_x": 100,
            "window_y": 100,
            "window_maximized": False,
            # パフォーマンス設定
            "cache_size_mb": 200,
            "thread_count": 4,
            "thumbnail_dpi": 150,
            "preload_pages": False,
            # 詳細設定
            "log_level": "WARNING",
            "log_to_file": True,
            "hardware_acceleration": False,
            "preview_mode": False,
            # 最近使用したファイル
            "recent_files": [],
            "max_recent_files": 10,
        }

    def load_settings(self) -> None:
        """設定をファイルから読み込み"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, encoding="utf-8") as f:
                    loaded_settings = json.load(f)

                # デフォルト設定をベースに、読み込んだ設定で上書き
                self._current_settings = self._default_settings.copy()
                self._current_settings.update(loaded_settings)

                self.logger.info(f"Settings loaded from {self.settings_file}")
            else:
                self._current_settings = self._default_settings.copy()
                self.logger.info("No settings file found, using defaults")

        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            self._current_settings = self._default_settings.copy()

    def save_settings(self) -> None:
        """設定をファイルに保存"""
        try:
            # 設定ディレクトリが存在することを確認
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self._current_settings, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Settings saved to {self.settings_file}")

        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        return self._current_settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """設定値を設定"""
        self._current_settings[key] = value

    def update(self, settings: dict[str, Any]) -> None:
        """複数の設定値を一括更新"""
        self._current_settings.update(settings)

    def get_all(self) -> dict[str, Any]:
        """すべての設定を取得"""
        return self._current_settings.copy()

    def reset_to_defaults(self) -> None:
        """設定をデフォルトに戻す"""
        self._current_settings = self._default_settings.copy()
        self.logger.info("Settings reset to defaults")

    def add_recent_file(self, file_path: str) -> None:
        """最近使用したファイルを追加"""
        recent_files = self._current_settings.get("recent_files", [])

        # 既に存在する場合は削除
        if file_path in recent_files:
            recent_files.remove(file_path)

        # 先頭に追加
        recent_files.insert(0, file_path)

        # 最大数を超えたら削除
        max_files = self._current_settings.get("max_recent_files", 10)
        if len(recent_files) > max_files:
            recent_files = recent_files[:max_files]

        self._current_settings["recent_files"] = recent_files

    def get_recent_files(self) -> list[str]:
        """最近使用したファイル一覧を取得"""
        recent_files = self._current_settings.get("recent_files", [])
        # 存在するファイルのみを返す
        existing_files = []
        for file_path in recent_files:
            if os.path.exists(file_path):
                existing_files.append(file_path)

        # 存在しないファイルがあった場合は設定を更新
        if len(existing_files) != len(recent_files):
            self._current_settings["recent_files"] = existing_files

        return existing_files

    def clear_recent_files(self) -> None:
        """最近使用したファイル一覧をクリア"""
        self._current_settings["recent_files"] = []
