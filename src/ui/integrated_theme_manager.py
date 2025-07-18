"""
統合テーママネージャー
PyPIパッケージ (qt-theme-manager) を使用したテーマ管理システム
"""

import os
import json
from typing import Dict, Optional
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QObject, pyqtSignal

# PyPIパッケージのテーママネージャーをインポート
from theme_manager import ThemeController, StylesheetGenerator

from src.utils.logger import get_logger
from src.utils.settings_manager import SettingsManager

logger = get_logger(__name__)


class PDFPageToolThemeManager(QObject):
    """PDF-PageTool専用テーママネージャー（PyPIパッケージベース）"""
    
    # シグナル定義
    theme_changed = pyqtSignal(str)  # テーマ変更シグナル
    
    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        
        # テーマ設定ファイルパス
        self.theme_config_path = self._get_theme_config_path()
        
        # PyPIパッケージのThemeControllerを初期化
        self.theme_controller = ThemeController(self.theme_config_path)
        
        # 設定マネージャーとの連携
        self._current_theme = str(self.settings_manager.get('theme', 'light'))
        
        # テーマ設定ファイルを初期化
        self._initialize_theme_config()
        
        # 初期テーマを適用
        self._apply_initial_theme()
        
        logger.info(f"PDFPageToolThemeManager initialized with theme: {self._current_theme}")
    
    def _get_theme_config_path(self) -> str:
        """テーマ設定ファイルのパスを取得"""
        current_dir = Path(__file__).parent
        return str(current_dir / "pdf_pagetool_themes.json")
    
    def _initialize_theme_config(self):
        """テーマ設定ファイルを初期化"""
        if not os.path.exists(self.theme_config_path):
            default_config = {
                "current_theme": "light",
                "available_themes": {
                    "light": {
                        "name": "light",
                        "display_name": "ライト",
                        "description": "明るい背景の標準テーマ",
                        "backgroundColor": "#ffffff",
                        "textColor": "#000000",
                        "primaryColor": "#f8f9fa",
                        "accentColor": "#007acc",
                        "button": {
                            "background": "#e9ecef",
                            "text": "#212529",
                            "hover": "#007acc",
                            "pressed": "#0056b3",
                            "border": "#ced4da"
                        },
                        "panel": {
                            "background": "#ffffff",
                            "border": "#dee2e6",
                            "header": {
                                "background": "#f8f9fa",
                                "text": "#212529",
                                "border": "#dee2e6"
                            }
                        },
                        "text": {
                            "primary": "#212529",
                            "secondary": "#6c757d",
                            "muted": "#adb5bd",
                            "heading": "#212529",
                            "link": "#007acc",
                            "success": "#28a745",
                            "warning": "#ffc107",
                            "error": "#dc3545"
                        },
                        "input": {
                            "background": "#ffffff",
                            "text": "#212529",
                            "border": "#ced4da",
                            "focus": "#007acc",
                            "placeholder": "#6c757d"
                        },
                        "menu": {
                            "background": "#ffffff",
                            "text": "#212529",
                            "hover": "#f8f9fa",
                            "separator": "#dee2e6"
                        },
                        "scrollbar": {
                            "background": "#f8f9fa",
                            "handle": "#ced4da",
                            "handleHover": "#adb5bd"
                        }
                    },
                    "dark": {
                        "name": "dark",
                        "display_name": "ダーク",
                        "description": "ダークモードテーマ",
                        "backgroundColor": "#2b2b2b",
                        "textColor": "#ffffff",
                        "primaryColor": "#3c3c3c",
                        "accentColor": "#0078d4",
                        "button": {
                            "background": "#404040",
                            "text": "#ffffff",
                            "hover": "#0078d4",
                            "pressed": "#106ebe",
                            "border": "#555555"
                        },
                        "panel": {
                            "background": "#2b2b2b",
                            "border": "#404040",
                            "header": {
                                "background": "#3c3c3c",
                                "text": "#ffffff",
                                "border": "#404040"
                            }
                        },
                        "text": {
                            "primary": "#ffffff",
                            "secondary": "#b0b0b0",
                            "muted": "#808080",
                            "heading": "#ffffff",
                            "link": "#0078d4",
                            "success": "#107c10",
                            "warning": "#ffb900",
                            "error": "#d13438"
                        },
                        "input": {
                            "background": "#3c3c3c",
                            "text": "#ffffff",
                            "border": "#555555",
                            "focus": "#0078d4",
                            "placeholder": "#b0b0b0"
                        },
                        "menu": {
                            "background": "#2b2b2b",
                            "text": "#ffffff",
                            "hover": "#3c3c3c",
                            "separator": "#404040"
                        },
                        "scrollbar": {
                            "background": "#3c3c3c",
                            "handle": "#555555",
                            "handleHover": "#666666"
                        }
                    },
                    "blue": {
                        "name": "blue",
                        "display_name": "ブルー",
                        "description": "青系テーマ",
                        "backgroundColor": "#f0f8ff",
                        "textColor": "#000080",
                        "primaryColor": "#e6f3ff",
                        "accentColor": "#0066cc",
                        "button": {
                            "background": "#cce7ff",
                            "text": "#000080",
                            "hover": "#0066cc",
                            "pressed": "#0052a3",
                            "border": "#99d6ff"
                        },
                        "panel": {
                            "background": "#f0f8ff",
                            "border": "#b3d9ff",
                            "header": {
                                "background": "#e6f3ff",
                                "text": "#000080",
                                "border": "#b3d9ff"
                            }
                        },
                        "text": {
                            "primary": "#000080",
                            "secondary": "#4169e1",
                            "muted": "#6495ed",
                            "heading": "#000080",
                            "link": "#0066cc",
                            "success": "#228b22",
                            "warning": "#ff8c00",
                            "error": "#dc143c"
                        },
                        "input": {
                            "background": "#ffffff",
                            "text": "#000080",
                            "border": "#99d6ff",
                            "focus": "#0066cc",
                            "placeholder": "#4169e1"
                        },
                        "menu": {
                            "background": "#f0f8ff",
                            "text": "#000080",
                            "hover": "#e6f3ff",
                            "separator": "#b3d9ff"
                        },
                        "scrollbar": {
                            "background": "#e6f3ff",
                            "handle": "#99d6ff",
                            "handleHover": "#66ccff"
                        }
                    },
                    "green": {
                        "name": "green",
                        "display_name": "グリーン",
                        "description": "緑系テーマ",
                        "backgroundColor": "#f0fff0",
                        "textColor": "#006400",
                        "primaryColor": "#e6ffe6",
                        "accentColor": "#228b22",
                        "button": {
                            "background": "#ccffcc",
                            "text": "#006400",
                            "hover": "#228b22",
                            "pressed": "#1c7a1c",
                            "border": "#99ff99"
                        },
                        "panel": {
                            "background": "#f0fff0",
                            "border": "#b3ffb3",
                            "header": {
                                "background": "#e6ffe6",
                                "text": "#006400",
                                "border": "#b3ffb3"
                            }
                        },
                        "text": {
                            "primary": "#006400",
                            "secondary": "#228b22",
                            "muted": "#32cd32",
                            "heading": "#006400",
                            "link": "#228b22",
                            "success": "#228b22",
                            "warning": "#ff8c00",
                            "error": "#dc143c"
                        },
                        "input": {
                            "background": "#ffffff",
                            "text": "#006400",
                            "border": "#99ff99",
                            "focus": "#228b22",
                            "placeholder": "#228b22"
                        },
                        "menu": {
                            "background": "#f0fff0",
                            "text": "#006400",
                            "hover": "#e6ffe6",
                            "separator": "#b3ffb3"
                        },
                        "scrollbar": {
                            "background": "#e6ffe6",
                            "handle": "#99ff99",
                            "handleHover": "#66ff66"
                        }
                    }
                }
            }
            
            try:
                with open(self.theme_config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                logger.info(f"Default theme config created: {self.theme_config_path}")
            except Exception as e:
                logger.error(f"Failed to create theme config: {e}")
    
    def _apply_initial_theme(self):
        """初期テーマを適用"""
        if self._current_theme:
            self.set_theme(self._current_theme)
    
    def get_available_themes(self) -> Dict[str, str]:
        """利用可能なテーマのリストを取得"""
        try:
            themes = self.theme_controller.get_available_themes()
            return {name: config.get('display_name', name) for name, config in themes.items()}
        except Exception as e:
            logger.error(f"Failed to get available themes: {e}")
            return {"light": "ライト", "dark": "ダーク"}
    
    def get_current_theme(self) -> str:
        """現在のテーマ名を取得"""
        return self._current_theme
    
    def set_theme(self, theme_name: str) -> bool:
        """テーマを設定"""
        try:
            # PyPIパッケージのThemeControllerでテーマを設定
            if self.theme_controller.set_theme(theme_name, save_settings=True):
                old_theme = self._current_theme
                self._current_theme = theme_name
                
                # 設定マネージャーにも保存
                self.settings_manager.set('theme', theme_name)
                
                # アプリケーションにテーマを適用
                self.apply_theme_to_application()
                
                # シグナルを発行
                self.theme_changed.emit(theme_name)
                
                logger.info(f"Theme changed from '{old_theme}' to '{theme_name}'")
                return True
            else:
                logger.error(f"Failed to set theme: {theme_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting theme '{theme_name}': {e}")
            return False
    
    def apply_theme_to_application(self, app: Optional[QApplication] = None) -> bool:
        """アプリケーション全体にテーマを適用"""
        try:
            if app is None:
                app_instance = QApplication.instance()
                if app_instance is not None and isinstance(app_instance, QApplication):
                    app = app_instance
            if app is not None:
                stylesheet = self.theme_controller.get_current_stylesheet()
                app.setStyleSheet(stylesheet)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to apply theme to application: {e}")
            return False
    
    def apply_theme_to_widget(self, widget: QWidget) -> bool:
        """特定のウィジェットにテーマを適用"""
        try:
            stylesheet = self.theme_controller.get_current_stylesheet()
            widget.setStyleSheet(stylesheet)
            return True
        except Exception as e:
            logger.error(f"Failed to apply theme to widget: {e}")
            return False
    
    def get_theme_stylesheet(self, theme_name: Optional[str] = None) -> str:
        """テーマのスタイルシートを取得"""
        try:
            if theme_name and theme_name != self._current_theme:
                # 一時的に指定テーマのスタイルシートを取得
                theme_config = self.theme_controller.loader.get_theme_config(theme_name)
                if theme_config:
                    generator = StylesheetGenerator(theme_config)
                    return generator.generate_qss()
            
            # 現在のテーマのスタイルシートを取得
            return self.theme_controller.get_current_stylesheet()
        except Exception as e:
            logger.error(f"Failed to get theme stylesheet: {e}")
            return ""
    
    def export_theme_qss(self, output_path: str, theme_name: Optional[str] = None) -> bool:
        """テーマのQSSファイルをエクスポート"""
        try:
            return self.theme_controller.export_qss(output_path, theme_name)
        except Exception as e:
            logger.error(f"Failed to export theme QSS: {e}")
            return False
    
    def reload_themes(self) -> bool:
        """テーマ設定を再読み込み"""
        try:
            return self.theme_controller.reload_themes()
        except Exception as e:
            logger.error(f"Failed to reload themes: {e}")
            return False


# シングルトンインスタンス
_theme_manager_instance: Optional[PDFPageToolThemeManager] = None


def get_integrated_theme_manager(settings_manager: Optional[SettingsManager] = None) -> PDFPageToolThemeManager:
    """統合テーママネージャーのシングルトンインスタンスを取得"""
    global _theme_manager_instance
    
    if _theme_manager_instance is None:
        if settings_manager is None:
            settings_manager = SettingsManager()
        _theme_manager_instance = PDFPageToolThemeManager(settings_manager)
    
    return _theme_manager_instance


def apply_theme_to_widget_simple(widget: QWidget, theme_name: Optional[str] = None) -> bool:
    """ウィジェットにテーマを適用する簡単な関数"""
    try:
        theme_manager = get_integrated_theme_manager()
        if theme_name:
            # 一時的にテーマを変更
            current_theme = theme_manager.get_current_theme()
            if theme_manager.set_theme(theme_name):
                result = theme_manager.apply_theme_to_widget(widget)
                # 元のテーマに戻す
                theme_manager.set_theme(current_theme)
                return result
        else:
            return theme_manager.apply_theme_to_widget(widget)
    except Exception as e:
        logger.error(f"Failed to apply theme to widget: {e}")
        return False
    
    return False


def apply_theme_to_application_simple(app: Optional[QApplication] = None, theme_name: Optional[str] = None) -> bool:
    """アプリケーションにテーマを適用する簡単な関数"""
    try:
        theme_manager = get_integrated_theme_manager()
        if theme_name:
            theme_manager.set_theme(theme_name)
        return theme_manager.apply_theme_to_application(app)
    except Exception as e:
        logger.error(f"Failed to apply theme to application: {e}")
        return False
