"""
キーボードショートカット管理モジュール
"""

from typing import Callable, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow

from src.utils.logger import get_logger
from src.utils.settings_manager import SettingsManager

logger = get_logger(__name__)


class ShortcutManager(QObject):
    """キーボードショートカット管理クラス"""

    shortcut_activated = pyqtSignal(str)  # ショートカット名

    def __init__(self, main_window: QMainWindow, settings_manager: SettingsManager):
        super().__init__()
        self.main_window = main_window
        self.settings = settings_manager
        self.shortcuts: Dict[str, QShortcut] = {}
        self.actions: Dict[str, Callable[[], None]] = {}

        # デフォルトショートカット定義
        self.default_shortcuts = {
            # ファイル操作
            'open_files': 'Ctrl+O',
            'save_pdf': 'Ctrl+S',
            'save_pdf_as': 'Ctrl+Shift+S',
            'close_file': 'Ctrl+W',
            'quit_app': 'Ctrl+Q',

            # 編集操作
            'select_all': 'Ctrl+A',
            'remove_selected': 'Delete',
            'rotate_right': 'Ctrl+R',
            'rotate_left': 'Ctrl+Shift+R',
            'rotate_180': 'Ctrl+Alt+R',

            # 表示操作
            'zoom_in': 'Ctrl++',
            'zoom_out': 'Ctrl+-',
            'zoom_fit': 'Ctrl+0',
            'toggle_fullscreen': 'F11',

            # ナビゲーション
            'next_page': 'Page_Down',
            'prev_page': 'Page_Up',
            'first_page': 'Home',
            'last_page': 'End',

            # ツール
            'batch_processor': 'Ctrl+B',
            'settings': 'Ctrl+,',
            'preferences': 'F2',

            # ヘルプ
            'show_help': 'F1',
            'show_about': 'Ctrl+F1',

            # デバッグ
            'toggle_debug': 'F12',
            'reload_ui': 'Ctrl+F5'
        }

        logger.info("ShortcutManager initialized")

    def register_action(self, name: str, action: Callable[[], None], shortcut_key: Optional[str] = None):
        """アクションとショートカットを登録"""
        self.actions[name] = action

        if shortcut_key is None:
            shortcut_key = self.default_shortcuts.get(name)

        if shortcut_key:
            self.create_shortcut(name, shortcut_key, action)

    def create_shortcut(self, name: str, key_sequence: str, action: Callable[[], None]):
        """ショートカットを作成"""
        try:
            # 既存のショートカットがあれば削除
            if name in self.shortcuts:
                self.shortcuts[name].deleteLater()

            # 新しいショートカットを作成
            shortcut = QShortcut(QKeySequence(key_sequence), self.main_window)
            shortcut.activated.connect(lambda: self._execute_action(name, action))

            self.shortcuts[name] = shortcut

            logger.debug(f"Shortcut created: {name} -> {key_sequence}")

        except Exception as e:
            logger.error(f"Failed to create shortcut {name}: {e}")

    def _execute_action(self, name: str, action: Callable[[], None]):
        """アクションを実行"""
        try:
            logger.debug(f"Executing shortcut action: {name}")
            action()
            self.shortcut_activated.emit(name)
        except Exception as e:
            logger.error(f"Error executing shortcut action {name}: {e}")

    def remove_shortcut(self, name: str):
        """ショートカットを削除"""
        if name in self.shortcuts:
            self.shortcuts[name].deleteLater()
            del self.shortcuts[name]
            logger.debug(f"Shortcut removed: {name}")

    def update_shortcut(self, name: str, new_key_sequence: str):
        """ショートカットキーを更新"""
        if name in self.actions:
            self.create_shortcut(name, new_key_sequence, self.actions[name])

    def get_shortcut_key(self, name: str) -> Optional[str]:
        """ショートカットキーを取得"""
        if name in self.shortcuts:
            return self.shortcuts[name].key().toString()
        return None

    def get_all_shortcuts(self) -> Dict[str, str]:
        """全ショートカットの辞書を取得"""
        result = {}
        for name, shortcut in self.shortcuts.items():
            result[name] = shortcut.key().toString()
        return result

    def load_shortcuts_from_settings(self):
        """設定からショートカットを読み込み"""
        custom_shortcuts = self.settings.get('keyboard_shortcuts', {})

        for name, key_sequence in custom_shortcuts.items():
            if name in self.actions:
                self.update_shortcut(name, key_sequence)

    def save_shortcuts_to_settings(self):
        """ショートカットを設定に保存"""
        shortcuts_dict = self.get_all_shortcuts()
        self.settings.set('keyboard_shortcuts', shortcuts_dict)

    def reset_to_defaults(self):
        """デフォルトショートカットにリセット"""
        for name, action in self.actions.items():
            default_key = self.default_shortcuts.get(name)
            if default_key:
                self.create_shortcut(name, default_key, action)

        logger.info("Shortcuts reset to defaults")

    def get_shortcut_help_text(self) -> str:
        """ショートカットヘルプテキストを生成"""
        shortcuts = self.get_all_shortcuts()

        help_text = "キーボードショートカット一覧\n"
        help_text += "=" * 40 + "\n\n"

        categories = {
            'ファイル操作': ['open_files', 'save_pdf', 'save_pdf_as', 'close_file', 'quit_app'],
            '編集操作': ['select_all', 'remove_selected', 'rotate_right', 'rotate_left', 'rotate_180'],
            '表示操作': ['zoom_in', 'zoom_out', 'zoom_fit', 'toggle_fullscreen'],
            'ナビゲーション': ['next_page', 'prev_page', 'first_page', 'last_page'],
            'ツール': ['batch_processor', 'settings', 'preferences'],
            'ヘルプ': ['show_help', 'show_about']
        }

        action_names = {
            'open_files': 'ファイルを開く',
            'save_pdf': '保存',
            'save_pdf_as': '名前を付けて保存',
            'close_file': 'ファイルを閉じる',
            'quit_app': 'アプリケーション終了',
            'select_all': '全て選択',
            'remove_selected': '選択項目を削除',
            'rotate_right': '右に回転',
            'rotate_left': '左に回転',
            'rotate_180': '180度回転',
            'zoom_in': 'ズームイン',
            'zoom_out': 'ズームアウト',
            'zoom_fit': 'ウィンドウに合わせる',
            'toggle_fullscreen': 'フルスクリーン切替',
            'next_page': '次のページ',
            'prev_page': '前のページ',
            'first_page': '最初のページ',
            'last_page': '最後のページ',
            'batch_processor': 'バッチ処理',
            'settings': '設定',
            'preferences': '環境設定',
            'show_help': 'ヘルプ',
            'show_about': 'このアプリについて'
        }

        for category, shortcut_names in categories.items():
            help_text += f"[{category}]\n"
            for name in shortcut_names:
                if name in shortcuts:
                    action_name = action_names.get(name, name)
                    help_text += f"  {action_name}: {shortcuts[name]}\n"
            help_text += "\n"

        return help_text


class ShortcutDialog:
    """ショートカット設定ダイアログ（将来実装予定）"""
    pass


def setup_main_window_shortcuts(main_window, shortcut_manager: ShortcutManager):
    """メインウィンドウのショートカットを設定"""

    # ファイル操作
    shortcut_manager.register_action('open_files', main_window.open_files)
    shortcut_manager.register_action('save_pdf', main_window.save_pdf)
    shortcut_manager.register_action('save_pdf_as', main_window.save_pdf_as)
    shortcut_manager.register_action('quit_app', main_window.close)

    # 編集操作
    if hasattr(main_window, 'select_all_pages'):
        shortcut_manager.register_action('select_all', main_window.select_all_pages)
    if hasattr(main_window, 'remove_selected_pages'):
        shortcut_manager.register_action('remove_selected', main_window.remove_selected_pages)
    if hasattr(main_window, 'rotate_selected_pages'):
        shortcut_manager.register_action('rotate_right', lambda: main_window.rotate_selected_pages(90))
        shortcut_manager.register_action('rotate_left', lambda: main_window.rotate_selected_pages(-90))
        shortcut_manager.register_action('rotate_180', lambda: main_window.rotate_selected_pages(180))

    # ツール
    if hasattr(main_window, 'open_settings'):
        shortcut_manager.register_action('settings', main_window.open_settings)
    if hasattr(main_window, 'open_batch_processor'):
        shortcut_manager.register_action('batch_processor', main_window.open_batch_processor)

    # ヘルプ
    if hasattr(main_window, 'show_about'):
        shortcut_manager.register_action('show_about', main_window.show_about)
    if hasattr(main_window, 'show_help'):
        shortcut_manager.register_action('show_help', main_window.show_help)

    # 設定から読み込み
    shortcut_manager.load_shortcuts_from_settings()

    logger.info("Main window shortcuts configured")


# ショートカット管理の簡易アクセス関数
_shortcut_manager_instance = None

def get_shortcut_manager(main_window: QMainWindow, settings_manager: SettingsManager) -> ShortcutManager:
    """ショートカットマネージャーのインスタンスを取得"""
    global _shortcut_manager_instance
    if _shortcut_manager_instance is None:
        _shortcut_manager_instance = ShortcutManager(main_window, settings_manager)
    return _shortcut_manager_instance
