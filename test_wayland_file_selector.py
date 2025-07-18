#!/usr/bin/env python3
"""
Wayland環境向けファイル選択ダイアログ代替案
"""

import sys
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QPushButton, QFileDialog, QListWidget, 
                             QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

class WaylandFileSelector(QMainWindow):
    """Wayland環境向けファイル選択代替UI"""
    
    # シグナル定義
    files_selected = pyqtSignal(list)  # 選択されたファイルのリスト
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF-PageTool - ファイル選択 (Wayland対応)")
        self.setGeometry(300, 300, 700, 500)
        
        # 選択されたファイルのリスト
        self.selected_files = []
        
        # UI構築
        self.init_ui()
        
    def init_ui(self):
        """UI初期化"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # タイトル
        title_label = QLabel("📄 PDFファイル選択")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 説明
        info_label = QLabel(
            "Wayland環境でドラッグ&ドロップが機能しない場合の代替手段です。\n"
            "以下のボタンからPDFファイルを選択してください。"
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        # 単一ファイル選択ボタン
        self.single_file_btn = QPushButton("📄 単一ファイル選択")
        self.single_file_btn.clicked.connect(self.select_single_file)
        self.single_file_btn.setMinimumHeight(40)
        button_layout.addWidget(self.single_file_btn)
        
        # 複数ファイル選択ボタン
        self.multi_file_btn = QPushButton("📚 複数ファイル選択")
        self.multi_file_btn.clicked.connect(self.select_multiple_files)
        self.multi_file_btn.setMinimumHeight(40)
        button_layout.addWidget(self.multi_file_btn)
        
        layout.addLayout(button_layout)
        
        # ファイルリスト表示
        list_label = QLabel("選択されたファイル:")
        layout.addWidget(list_label)
        
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        layout.addWidget(self.file_list)
        
        # アクションボタン
        action_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🗑️ クリア")
        self.clear_btn.clicked.connect(self.clear_files)
        action_layout.addWidget(self.clear_btn)
        
        self.confirm_btn = QPushButton("✅ 確定してメインアプリに送る")
        self.confirm_btn.clicked.connect(self.confirm_selection)
        self.confirm_btn.setEnabled(False)
        action_layout.addWidget(self.confirm_btn)
        
        layout.addLayout(action_layout)
        
        # 環境情報表示
        env_info = QLabel(f"環境: {QApplication.instance().platformName()}")
        env_info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(env_info)
        
    def select_single_file(self):
        """単一ファイル選択"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "PDFファイルを選択",
            "",
            "PDFファイル (*.pdf);;すべてのファイル (*)"
        )
        
        if file_path:
            self.add_file(file_path)
            
    def select_multiple_files(self):
        """複数ファイル選択"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "PDFファイルを選択（複数可）",
            "",
            "PDFファイル (*.pdf);;すべてのファイル (*)"
        )
        
        for file_path in file_paths:
            self.add_file(file_path)
            
    def add_file(self, file_path):
        """ファイルをリストに追加"""
        if file_path not in self.selected_files:
            self.selected_files.append(file_path)
            self.file_list.addItem(f"📄 {Path(file_path).name}")
            self.confirm_btn.setEnabled(True)
            print(f"Added file: {file_path}")
            
    def clear_files(self):
        """ファイルリストをクリア"""
        self.selected_files.clear()
        self.file_list.clear()
        self.confirm_btn.setEnabled(False)
        print("File list cleared")
        
    def confirm_selection(self):
        """選択を確定"""
        if self.selected_files:
            print(f"Confirming selection of {len(self.selected_files)} files:")
            for file_path in self.selected_files:
                print(f"  - {file_path}")
            
            # シグナルを発信
            self.files_selected.emit(self.selected_files.copy())
            
            # メインアプリへの指示を表示
            msg = QMessageBox()
            msg.setWindowTitle("選択完了")
            msg.setText(
                f"{len(self.selected_files)}個のファイルが選択されました。\n\n"
                "メインアプリケーションでファイルを処理してください。"
            )
            msg.setInformativeText(
                "ファイルパス:\n" + 
                "\n".join([Path(f).name for f in self.selected_files])
            )
            msg.exec()
            
            # ウィンドウを閉じる
            self.close()

def test_file_selector():
    """ファイル選択テスト"""
    app = QApplication(sys.argv)
    
    print("=== Wayland対応ファイル選択テスト ===")
    print(f"Platform: {app.platformName()}")
    
    selector = WaylandFileSelector()
    
    # ファイル選択シグナルのハンドラ
    def handle_files_selected(files):
        print("🎉 Files selected via signal:")
        for file_path in files:
            print(f"  - {file_path}")
    
    selector.files_selected.connect(handle_files_selected)
    selector.show()
    
    sys.exit(app.exec())

def main():
    test_file_selector()

if __name__ == "__main__":
    main()
