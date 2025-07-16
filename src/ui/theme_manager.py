"""
テーマ管理モジュール
"""

from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette

from src.utils.logger import get_logger
from src.utils.settings_manager import SettingsManager

logger = get_logger(__name__)


class ThemeManager(QObject):
    """テーマ管理クラス"""
    
    theme_changed = pyqtSignal(str)  # テーマ変更時のシグナル
    
    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings = settings_manager
        self._current_theme: str = str(self.settings.get('theme', 'ライト'))
        
        # テーマ定義
        self._themes = {
            'ライト': self._create_light_theme(),
            'ダーク': self._create_dark_theme(),
            'ブルー': self._create_blue_theme(),
            'グリーン': self._create_green_theme()
        }
        
        logger.info(f"ThemeManager initialized with theme: {self._current_theme}")
    
    def _create_light_theme(self) -> Dict[str, Any]:
        """ライトテーマ定義"""
        return {
            'name': 'ライト',
            'style': """
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QMenuBar {
                    background-color: #f0f0f0;
                    color: #000000;
                    border-bottom: 1px solid #d0d0d0;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                }
                QMenu::item:selected {
                    background-color: #e0e0e0;
                }
                QToolBar {
                    background-color: #f8f8f8;
                    border: 1px solid #d0d0d0;
                    spacing: 2px;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: #000000;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                    border-color: #b0b0b0;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
                QPushButton:disabled {
                    background-color: #f5f5f5;
                    color: #a0a0a0;
                    border-color: #e0e0e0;
                }
                QScrollArea {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                }
                QLabel {
                    color: #000000;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    color: #000000;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                    border-color: #007acc;
                }
                QTabWidget::pane {
                    border: 1px solid #d0d0d0;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    border: 1px solid #d0d0d0;
                    padding: 6px 12px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom-color: #ffffff;
                }
                QProgressBar {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    background-color: #f0f0f0;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #007acc;
                    border-radius: 3px;
                }
            """,
            'colors': {
                'background': '#ffffff',
                'foreground': '#000000',
                'accent': '#007acc',
                'border': '#d0d0d0',
                'hover': '#f0f0f0',
                'selected': '#e0e0e0'
            }
        }
    
    def _create_dark_theme(self) -> Dict[str, Any]:
        """ダークテーマ定義"""
        return {
            'name': 'ダーク',
            'style': """
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border-bottom: 1px solid #555555;
                }
                QMenuBar::item:selected {
                    background-color: #4a4a4a;
                }
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QMenu::item:selected {
                    background-color: #4a4a4a;
                }
                QToolBar {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    spacing: 2px;
                }
                QPushButton {
                    background-color: #4a4a4a;
                    border: 1px solid #666666;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                    border-color: #777777;
                }
                QPushButton:pressed {
                    background-color: #606060;
                }
                QPushButton:disabled {
                    background-color: #363636;
                    color: #666666;
                    border-color: #444444;
                }
                QScrollArea {
                    background-color: #2b2b2b;
                    border: 1px solid #555555;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #4a4a4a;
                    border: 1px solid #666666;
                    border-radius: 4px;
                    padding: 4px;
                    color: #ffffff;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                    border-color: #007acc;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    padding: 6px 12px;
                    margin-right: 2px;
                    color: #ffffff;
                }
                QTabBar::tab:selected {
                    background-color: #2b2b2b;
                    border-bottom-color: #2b2b2b;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    background-color: #3c3c3c;
                    text-align: center;
                    color: #ffffff;
                }
                QProgressBar::chunk {
                    background-color: #007acc;
                    border-radius: 3px;
                }
                QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 8px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 4px 0 4px;
                }
                QCheckBox, QRadioButton {
                    color: #ffffff;
                }
                QCheckBox::indicator, QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    border: 1px solid #666666;
                    background-color: #4a4a4a;
                }
                QCheckBox::indicator:checked {
                    border: 1px solid #007acc;
                    background-color: #007acc;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #555555;
                    height: 6px;
                    background: #3c3c3c;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: #007acc;
                    border: 1px solid #007acc;
                    width: 16px;
                    margin: -4px 0;
                    border-radius: 8px;
                }
            """,
            'colors': {
                'background': '#2b2b2b',
                'foreground': '#ffffff',
                'accent': '#007acc',
                'border': '#555555',
                'hover': '#5a5a5a',
                'selected': '#4a4a4a'
            }
        }
    
    def _create_blue_theme(self) -> Dict[str, Any]:
        """ブルーテーマ定義"""
        return {
            'name': 'ブルー',
            'style': """
                QMainWindow {
                    background-color: #1e3a5f;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #2a4d73;
                    color: #ffffff;
                    border-bottom: 1px solid #4a6d93;
                }
                QMenuBar::item:selected {
                    background-color: #3a5d83;
                }
                QMenu {
                    background-color: #2a4d73;
                    color: #ffffff;
                    border: 1px solid #4a6d93;
                }
                QMenu::item:selected {
                    background-color: #3a5d83;
                }
                QPushButton {
                    background-color: #3a5d83;
                    border: 1px solid #5a7da3;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #4a7db3;
                    border-color: #6a9dc3;
                }
                QPushButton:pressed {
                    background-color: #5a8dc3;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #3a5d83;
                    border: 1px solid #5a7da3;
                    border-radius: 4px;
                    padding: 4px;
                    color: #ffffff;
                }
                QProgressBar {
                    border: 1px solid #4a6d93;
                    border-radius: 4px;
                    background-color: #2a4d73;
                    text-align: center;
                    color: #ffffff;
                }
                QProgressBar::chunk {
                    background-color: #00aaff;
                    border-radius: 3px;
                }
            """,
            'colors': {
                'background': '#1e3a5f',
                'foreground': '#ffffff',
                'accent': '#00aaff',
                'border': '#4a6d93',
                'hover': '#4a7db3',
                'selected': '#3a5d83'
            }
        }
    
    def _create_green_theme(self) -> Dict[str, Any]:
        """グリーンテーマ定義"""
        return {
            'name': 'グリーン',
            'style': """
                QMainWindow {
                    background-color: #1e3e2e;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #2a4a3a;
                    color: #ffffff;
                    border-bottom: 1px solid #4a6a5a;
                }
                QMenuBar::item:selected {
                    background-color: #3a5a4a;
                }
                QMenu {
                    background-color: #2a4a3a;
                    color: #ffffff;
                    border: 1px solid #4a6a5a;
                }
                QMenu::item:selected {
                    background-color: #3a5a4a;
                }
                QPushButton {
                    background-color: #3a5a4a;
                    border: 1px solid #5a7a6a;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #4a7a5a;
                    border-color: #6a9a7a;
                }
                QPushButton:pressed {
                    background-color: #5a8a6a;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #3a5a4a;
                    border: 1px solid #5a7a6a;
                    border-radius: 4px;
                    padding: 4px;
                    color: #ffffff;
                }
                QProgressBar {
                    border: 1px solid #4a6a5a;
                    border-radius: 4px;
                    background-color: #2a4a3a;
                    text-align: center;
                    color: #ffffff;
                }
                QProgressBar::chunk {
                    background-color: #00aa55;
                    border-radius: 3px;
                }
            """,
            'colors': {
                'background': '#1e3e2e',
                'foreground': '#ffffff',
                'accent': '#00aa55',
                'border': '#4a6a5a',
                'hover': '#4a7a5a',
                'selected': '#3a5a4a'
            }
        }
    
    @property
    def current_theme(self) -> str:
        """現在のテーマ名を取得"""
        return self._current_theme
    
    @property
    def available_themes(self) -> List[str]:
        """利用可能なテーマ一覧を取得"""
        return list(self._themes.keys())
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """テーマの色情報を取得"""
        if theme_name is None:
            theme_name = self._current_theme
        return self._themes.get(theme_name, {}).get('colors', {})
    
    def apply_theme(self, theme_name: str, app: Optional[QApplication] = None):
        """テーマを適用"""
        if theme_name not in self._themes:
            logger.warning(f"Unknown theme: {theme_name}")
            return
        
        if app is None:
            app_instance = QApplication.instance()
            if isinstance(app_instance, QApplication):
                app = app_instance
        
        if app is None:
            logger.error("No QApplication instance found")
            return
        
        theme = self._themes[theme_name]
        
        # スタイルシートを適用
        app.setStyleSheet(theme['style'])
        
        # 現在のテーマを更新
        old_theme = self._current_theme
        self._current_theme = theme_name
        
        # 設定に保存
        self.settings.set('theme', theme_name)
        
        logger.info(f"Theme changed from '{old_theme}' to '{theme_name}'")
        
        # シグナル発信
        self.theme_changed.emit(theme_name)
    
    def load_theme_from_settings(self, app: Optional[QApplication] = None):
        """設定からテーマを読み込んで適用"""
        theme_name = str(self.settings.get('theme', 'ライト'))
        self.apply_theme(theme_name, app)
    
    def get_theme_preview_style(self, theme_name: str) -> str:
        """テーマプレビュー用の簡易スタイルを取得"""
        if theme_name not in self._themes:
            return ""
        
        colors = self._themes[theme_name]['colors']
        return f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['foreground']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 8px;
            }}
        """
    
    def create_theme_preview_widget(self, theme_name: str, parent: Optional[QWidget] = None) -> QWidget:
        """テーマプレビューウィジェット作成"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        # テーマ名ラベル
        name_label = QLabel(theme_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        # プレビューエリア
        preview = QWidget()
        preview.setFixedSize(120, 80)
        preview.setStyleSheet(self.get_theme_preview_style(theme_name))
        
        preview_layout = QVBoxLayout(preview)
        preview_layout.addWidget(QLabel("Sample"))
        
        layout.addWidget(name_label)
        layout.addWidget(preview)
        
        return widget


def apply_system_theme(app: QApplication):
    """システムテーマの適用（フォールバック）"""
    try:
        # システムの設定に応じてライト/ダークテーマを判定
        palette = app.palette()
        bg_color = palette.color(QPalette.ColorRole.Window)
        
        # 背景色の明度でテーマを判定
        is_dark = bg_color.lightness() < 128
        
        theme_manager = ThemeManager(SettingsManager())
        default_theme = 'ダーク' if is_dark else 'ライト'
        theme_manager.apply_theme(default_theme, app)
        
        logger.info(f"Applied system theme: {default_theme}")
        
    except Exception as e:
        logger.error(f"Failed to apply system theme: {e}")


# テーマ管理の簡易アクセス関数
_theme_manager_instance = None

def get_theme_manager(settings_manager: Optional[SettingsManager] = None) -> ThemeManager:
    """テーママネージャーのシングルトンインスタンスを取得"""
    global _theme_manager_instance
    if _theme_manager_instance is None:
        if settings_manager is None:
            settings_manager = SettingsManager()
        _theme_manager_instance = ThemeManager(settings_manager)
    return _theme_manager_instance
