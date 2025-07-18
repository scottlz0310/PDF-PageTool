"""
Settings Dialog Module

アプリケーション設定ダイアログ
"""

from typing import Dict, Any, Optional
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QWidget, QLabel, QSpinBox, QCheckBox, QComboBox,
                            QPushButton, QGroupBox, QSlider, QColorDialog,
                            QFileDialog, QMessageBox, QFormLayout, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from ..utils.logger import get_logger
from .integrated_theme_manager import get_integrated_theme_manager


class SettingsDialog(QDialog):
    """設定ダイアログ"""
    
    settings_changed = pyqtSignal(dict)  # 設定変更時のシグナル
    
    def __init__(self, current_settings: Dict[str, Any], parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.logger = get_logger("SettingsDialog")
        self.current_settings = current_settings.copy()
        self.temp_settings = current_settings.copy()
        
        # 統合テーママネージャーを取得
        self.theme_manager = get_integrated_theme_manager()
        
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self):
        """UI設定"""
        self.setWindowTitle("設定")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 各タブを設定
        self._setup_general_tab()
        self._setup_ui_tab()
        self._setup_performance_tab()
        self._setup_advanced_tab()
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("デフォルトに戻す")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._accept_settings)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def _setup_general_tab(self):
        """一般設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "一般")
        
        layout = QVBoxLayout(tab)
        
        # ファイル設定
        file_group = QGroupBox("ファイル設定")
        file_layout = QVBoxLayout(file_group)
        
        # デフォルト出力フォルダ
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("デフォルト出力フォルダ:"))
        
        self.output_folder_edit = QtWidgets.QLineEdit()
        output_layout.addWidget(self.output_folder_edit)
        
        browse_button = QPushButton("参照...")
        browse_button.clicked.connect(self._browse_output_folder)
        output_layout.addWidget(browse_button)
        
        file_layout.addLayout(output_layout)
        
        # ファイル名テンプレート
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("ファイル名テンプレート:"))
        self.filename_template_edit = QtWidgets.QLineEdit()
        template_layout.addWidget(self.filename_template_edit)
        file_layout.addLayout(template_layout)
        
        layout.addWidget(file_group)
        
        # 動作設定
        behavior_group = QGroupBox("動作設定")
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.auto_save_check = QCheckBox("自動保存を有効にする")
        behavior_layout.addWidget(self.auto_save_check)
        
        self.confirm_exit_check = QCheckBox("終了時に確認する")
        behavior_layout.addWidget(self.confirm_exit_check)
        
        self.remember_window_check = QCheckBox("ウィンドウサイズと位置を記憶する")
        behavior_layout.addWidget(self.remember_window_check)
        
        layout.addWidget(behavior_group)
        
        layout.addStretch()
    
    def _setup_ui_tab(self):
        """UI設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "表示")
        
        layout = QVBoxLayout(tab)
        
        # テーマ設定
        theme_group = QGroupBox("テーマ設定")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_layout_h = QHBoxLayout()
        theme_layout_h.addWidget(QLabel("テーマ:"))
        self.theme_combo = QComboBox()
        # 公式Theme-Manager互換のテーママネージャーから利用可能なテーマを取得
        available_themes = list(self.theme_manager.get_available_themes().keys())
        self.theme_combo.addItems(available_themes)
        # テーマ変更時の処理を接続
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_layout_h.addWidget(self.theme_combo)
        theme_layout_h.addStretch()
        theme_layout.addLayout(theme_layout_h)
        
        layout.addWidget(theme_group)
        
        # サムネイル設定
        thumbnail_group = QGroupBox("サムネイル設定")
        thumbnail_layout = QVBoxLayout(thumbnail_group)
        
        # サムネイルサイズ
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("サムネイルサイズ:"))
        self.thumbnail_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.thumbnail_size_slider.setRange(100, 300)
        self.thumbnail_size_slider.setValue(160)
        self.thumbnail_size_slider.valueChanged.connect(self._update_thumbnail_size_label)
        size_layout.addWidget(self.thumbnail_size_slider)
        
        self.thumbnail_size_label = QLabel("160px")
        size_layout.addWidget(self.thumbnail_size_label)
        thumbnail_layout.addLayout(size_layout)
        
        # サムネイル品質
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("サムネイル品質:"))
        self.thumbnail_quality_combo = QComboBox()
        self.thumbnail_quality_combo.addItems(["低", "中", "高", "最高"])
        quality_layout.addWidget(self.thumbnail_quality_combo)
        quality_layout.addStretch()
        thumbnail_layout.addLayout(quality_layout)
        
        layout.addWidget(thumbnail_group)
        
        # 表示設定
        display_group = QGroupBox("表示設定")
        display_layout = QVBoxLayout(display_group)
        
        self.show_page_numbers_check = QCheckBox("ページ番号を表示")
        display_layout.addWidget(self.show_page_numbers_check)
        
        self.show_file_names_check = QCheckBox("ファイル名を表示")
        display_layout.addWidget(self.show_file_names_check)
        
        self.show_tooltips_check = QCheckBox("ツールチップを表示")
        display_layout.addWidget(self.show_tooltips_check)
        
        # Waylandドラッグ&ドロップ問題の回避策
        self.show_file_selection_button_check = QCheckBox("ファイル選択ボタンを表示（ドラッグ&ドロップ代替手段）")
        self.show_file_selection_button_check.setToolTip(
            "Wayland環境でドラッグ&ドロップが機能しない場合の代替手段として、\n"
            "ファイル選択ボタンを表示します"
        )
        display_layout.addWidget(self.show_file_selection_button_check)
        
        layout.addWidget(display_group)
        
        layout.addStretch()
    
    def _setup_performance_tab(self):
        """パフォーマンス設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "パフォーマンス")
        
        layout = QVBoxLayout(tab)
        
        # メモリ設定
        memory_group = QGroupBox("メモリ設定")
        memory_layout = QVBoxLayout(memory_group)
        
        # キャッシュサイズ
        cache_layout = QHBoxLayout()
        cache_layout.addWidget(QLabel("サムネイルキャッシュサイズ (MB):"))
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(50, 1000)
        self.cache_size_spin.setValue(200)
        cache_layout.addWidget(self.cache_size_spin)
        cache_layout.addStretch()
        memory_layout.addLayout(cache_layout)
        
        # 並列処理
        parallel_layout = QHBoxLayout()
        parallel_layout.addWidget(QLabel("並列処理スレッド数:"))
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(1, 16)
        self.thread_count_spin.setValue(4)
        parallel_layout.addWidget(self.thread_count_spin)
        parallel_layout.addStretch()
        memory_layout.addLayout(parallel_layout)
        
        layout.addWidget(memory_group)
        
        # PDF処理設定
        pdf_group = QGroupBox("PDF処理設定")
        pdf_layout = QVBoxLayout(pdf_group)
        
        # DPI設定
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("サムネイル生成DPI:"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 300)
        self.dpi_spin.setValue(150)
        dpi_layout.addWidget(self.dpi_spin)
        dpi_layout.addStretch()
        pdf_layout.addLayout(dpi_layout)
        
        self.preload_pages_check = QCheckBox("ページを事前読み込みする")
        pdf_layout.addWidget(self.preload_pages_check)
        
        layout.addWidget(pdf_group)
        
        layout.addStretch()
    
    def _setup_advanced_tab(self):
        """詳細設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "詳細")
        
        layout = QVBoxLayout(tab)
        
        # ログ設定
        log_group = QGroupBox("ログ設定")
        log_layout = QVBoxLayout(log_group)
        
        log_level_layout = QHBoxLayout()
        log_level_layout.addWidget(QLabel("ログレベル:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "VERBOSE", "INFO", "WARNING", "ERROR"])
        log_level_layout.addWidget(self.log_level_combo)
        log_level_layout.addStretch()
        log_layout.addLayout(log_level_layout)
        
        self.log_to_file_check = QCheckBox("ファイルにログを出力")
        log_layout.addWidget(self.log_to_file_check)
        
        layout.addWidget(log_group)
        
        # 実験的機能
        experimental_group = QGroupBox("実験的機能")
        experimental_layout = QVBoxLayout(experimental_group)
        
        self.hardware_acceleration_check = QCheckBox("ハードウェアアクセラレーション (実験的)")
        experimental_layout.addWidget(self.hardware_acceleration_check)
        
        self.preview_mode_check = QCheckBox("プレビューモード (実験的)")
        experimental_layout.addWidget(self.preview_mode_check)
        
        layout.addWidget(experimental_group)
        
        layout.addStretch()
    
    def _on_theme_changed(self, theme_name: str):
        """テーマ変更時の処理（統合テーママネージャー互換）"""
        try:
            # 一時設定を更新
            self.temp_settings["theme"] = theme_name
            
            # 統合テーママネージャーを使用してプレビュー適用
            self.theme_manager.preview_theme(theme_name)
            
            self.logger.debug(f"Theme changed to: {theme_name}")
        except Exception as e:
            self.logger.error(f"Failed to change theme: {e}")

    def _browse_output_folder(self):
        """出力フォルダ選択"""
        folder = QFileDialog.getExistingDirectory(
            self, "出力フォルダを選択", self.output_folder_edit.text()
        )
        if folder:
            self.output_folder_edit.setText(folder)
    
    def _update_thumbnail_size_label(self, value):
        """サムネイルサイズラベル更新"""
        self.thumbnail_size_label.setText(f"{value}px")
    
    def _load_settings(self):
        """現在の設定を読み込み"""
        # 一般設定
        self.output_folder_edit.setText(self.temp_settings.get("output_folder", ""))
        self.filename_template_edit.setText(self.temp_settings.get("filename_template", "output_{datetime}"))
        self.auto_save_check.setChecked(self.temp_settings.get("auto_save", False))
        self.confirm_exit_check.setChecked(self.temp_settings.get("confirm_exit", True))
        self.remember_window_check.setChecked(self.temp_settings.get("remember_window", True))
        
        # UI設定
        theme = self.temp_settings.get("theme", "light")  # 公式Theme-Managerのデフォルトテーマ
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.thumbnail_size_slider.setValue(self.temp_settings.get("thumbnail_size", 160))
        
        quality = self.temp_settings.get("thumbnail_quality", "中")
        index = self.thumbnail_quality_combo.findText(quality)
        if index >= 0:
            self.thumbnail_quality_combo.setCurrentIndex(index)
        
        self.show_page_numbers_check.setChecked(self.temp_settings.get("show_page_numbers", True))
        self.show_file_names_check.setChecked(self.temp_settings.get("show_file_names", True))
        self.show_tooltips_check.setChecked(self.temp_settings.get("show_tooltips", True))
        self.show_file_selection_button_check.setChecked(self.temp_settings.get("show_file_selection_button", False))
        
        # パフォーマンス設定
        self.cache_size_spin.setValue(self.temp_settings.get("cache_size_mb", 200))
        self.thread_count_spin.setValue(self.temp_settings.get("thread_count", 4))
        self.dpi_spin.setValue(self.temp_settings.get("thumbnail_dpi", 150))
        self.preload_pages_check.setChecked(self.temp_settings.get("preload_pages", False))
        
        # 詳細設定
        log_level = self.temp_settings.get("log_level", "INFO")
        index = self.log_level_combo.findText(log_level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
        
        self.log_to_file_check.setChecked(self.temp_settings.get("log_to_file", True))
        self.hardware_acceleration_check.setChecked(self.temp_settings.get("hardware_acceleration", False))
        self.preview_mode_check.setChecked(self.temp_settings.get("preview_mode", False))
    
    def _save_settings(self):
        """現在のUI状態を設定に保存"""
        # 一般設定
        self.temp_settings["output_folder"] = self.output_folder_edit.text()
        self.temp_settings["filename_template"] = self.filename_template_edit.text()
        self.temp_settings["auto_save"] = self.auto_save_check.isChecked()
        self.temp_settings["confirm_exit"] = self.confirm_exit_check.isChecked()
        self.temp_settings["remember_window"] = self.remember_window_check.isChecked()
        
        # UI設定
        self.temp_settings["theme"] = self.theme_combo.currentText()
        self.temp_settings["thumbnail_size"] = self.thumbnail_size_slider.value()
        self.temp_settings["thumbnail_quality"] = self.thumbnail_quality_combo.currentText()
        self.temp_settings["show_page_numbers"] = self.show_page_numbers_check.isChecked()
        self.temp_settings["show_file_names"] = self.show_file_names_check.isChecked()
        self.temp_settings["show_tooltips"] = self.show_tooltips_check.isChecked()
        
        # パフォーマンス設定
        self.temp_settings["cache_size_mb"] = self.cache_size_spin.value()
        self.temp_settings["thread_count"] = self.thread_count_spin.value()
        self.temp_settings["thumbnail_dpi"] = self.dpi_spin.value()
        self.temp_settings["preload_pages"] = self.preload_pages_check.isChecked()
        
        # 詳細設定
        self.temp_settings["log_level"] = self.log_level_combo.currentText()
        self.temp_settings["log_to_file"] = self.log_to_file_check.isChecked()
        self.temp_settings["hardware_acceleration"] = self.hardware_acceleration_check.isChecked()
        self.temp_settings["preview_mode"] = self.preview_mode_check.isChecked()
    
    def _reset_to_defaults(self):
        """デフォルト設定に戻す"""
        reply = QMessageBox.question(
            self, "設定をリセット", 
            "すべての設定をデフォルトに戻しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.temp_settings = self._get_default_settings()
            self._load_settings()
    
    def _get_default_settings(self):
        """デフォルト設定を取得"""
        return {
            "output_folder": "",
            "filename_template": "output_{datetime}",
            "auto_save": False,
            "confirm_exit": True,
            "remember_window": True,
            "theme": "ライト",
            "thumbnail_size": 160,
            "thumbnail_quality": "中",
            "show_page_numbers": True,
            "show_file_names": True,
            "show_tooltips": True,
            "cache_size_mb": 200,
            "thread_count": 4,
            "thumbnail_dpi": 150,
            "preload_pages": False,
            "log_level": "INFO",
            "log_to_file": True,
            "hardware_acceleration": False,
            "preview_mode": False
        }
    
    def _accept_settings(self):
        """設定を適用して閉じる"""
        self._save_settings()
        self.settings_changed.emit(self.temp_settings)
        self.accept()
    
    def get_settings(self):
        """現在の設定を取得"""
        return self.temp_settings.copy()
