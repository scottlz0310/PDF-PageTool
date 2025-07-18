#!/usr/bin/env python3
"""
Linux向け改良ドラッグ&ドロップテスト
"""

import sys
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QMimeData, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

class LinuxDragDropWindow(QMainWindow):
    """Linux向け改良ドラッグ&ドロップテストウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux対応ドラッグ&ドロップテスト")
        self.setGeometry(300, 300, 600, 400)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        self.label = QLabel("PDFファイルをドラッグ&ドロップしてください\n(Linux環境対応版)")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 3px dashed #666;
                padding: 40px;
                font-size: 16px;
                background-color: #fafafa;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.label)
        
        # ドロップ受け入れを有効化
        self.setAcceptDrops(True)
        
        # 子ウィジェットではドロップを明示的に無効化
        central_widget.setAcceptDrops(False)
        self.label.setAcceptDrops(False)
        
        print(f"Main window acceptDrops: {self.acceptDrops()}")
        print(f"Central widget acceptDrops: {central_widget.acceptDrops()}")
        print(f"Label acceptDrops: {self.label.acceptDrops()}")
        
        # ウィンドウプロパティを設定（Linux環境で推奨）
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptDrops, True)
        
    def dragEnterEvent(self, event):
        """ドラッグエンター時の処理 - Linux対応版"""
        print("=== dragEnterEvent called (Linux version) ===")
        
        try:
            # イベント型確認
            print(f"Event type: {type(event)}")
            print(f"Event accepted: {event.isAccepted()}")
            
            # mimeDataの詳細チェック
            mime_data = event.mimeData()
            if mime_data is None:
                print("ERROR: mimeData is None!")
                event.ignore()
                return
            
            print(f"mimeData: {mime_data}")
            print(f"mimeData type: {type(mime_data)}")
            
            # 利用可能なフォーマットを確認
            formats = mime_data.formats()
            print(f"Available formats: {formats}")
            
            # 各フォーマットの内容を確認
            for fmt in formats:
                print(f"Format '{fmt}': {mime_data.hasFormat(fmt)}")
            
            # URLの詳細チェック
            has_urls = mime_data.hasUrls()
            print(f"Has URLs: {has_urls}")
            
            if has_urls:
                urls = mime_data.urls()
                print(f"Number of URLs: {len(urls)}")
                
                pdf_count = 0
                for i, url in enumerate(urls):
                    print(f"URL {i}:")
                    print(f"  toString(): {url.toString()}")
                    print(f"  scheme(): {url.scheme()}")
                    print(f"  isLocalFile(): {url.isLocalFile()}")
                    print(f"  isValid(): {url.isValid()}")
                    
                    if url.isLocalFile():
                        local_path = url.toLocalFile()
                        print(f"  toLocalFile(): {local_path}")
                        print(f"  exists: {Path(local_path).exists()}")
                        print(f"  is PDF: {local_path.lower().endswith('.pdf')}")
                        
                        if local_path.lower().endswith('.pdf'):
                            pdf_count += 1
                
                # 結果に基づいてアクション決定
                if pdf_count > 0:
                    print(f"✅ ACCEPTING drop of {pdf_count} PDF files")
                    event.acceptProposedAction()
                    self.label.setText(f"✅ {pdf_count}個のPDFファイルを受け入れます")
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 3px dashed #4CAF50;
                            padding: 40px;
                            font-size: 16px;
                            background-color: #E8F5E8;
                            color: #2E7D32;
                            border-radius: 10px;
                        }
                    """)
                else:
                    print("❌ REJECTING: No PDF files found")
                    event.ignore()
                    self.label.setText("❌ PDFファイルが見つかりません")
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 3px dashed #f44336;
                            padding: 40px;
                            font-size: 16px;
                            background-color: #FFEBEE;
                            color: #C62828;
                            border-radius: 10px;
                        }
                    """)
            else:
                print("❌ REJECTING: No URLs in mimeData")
                event.ignore()
                self.label.setText("❌ URLが見つかりません")
                
        except Exception as e:
            print(f"❌ Exception in dragEnterEvent: {e}")
            import traceback
            traceback.print_exc()
            event.ignore()
    
    def dragMoveEvent(self, event):
        """ドラッグ移動時の処理"""
        print("dragMoveEvent called")
        # dragEnterEventで許可されていれば、移動も許可
        if event.mimeData() and event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """ドラッグリーブ時の処理"""
        print("dragLeaveEvent called")
        self.label.setText("PDFファイルをドラッグ&ドロップしてください\n(Linux環境対応版)")
        self.label.setStyleSheet("""
            QLabel {
                border: 3px dashed #666;
                padding: 40px;
                font-size: 16px;
                background-color: #fafafa;
                border-radius: 10px;
            }
        """)
    
    def dropEvent(self, event):
        """ドロップ時の処理"""
        print("=== dropEvent called (Linux version) ===")
        
        try:
            mime_data = event.mimeData()
            if mime_data is None:
                print("ERROR: mimeData is None in dropEvent!")
                event.ignore()
                return
            
            pdf_files = []
            if mime_data.hasUrls():
                for url in mime_data.urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        print(f"Processing file: {file_path}")
                        if file_path.lower().endswith('.pdf'):
                            pdf_files.append(file_path)
            
            if pdf_files:
                print(f"🎉 SUCCESS: Dropped {len(pdf_files)} PDF files:")
                for pdf_file in pdf_files:
                    print(f"  - {pdf_file}")
                
                event.acceptProposedAction()
                self.label.setText(f"🎉 成功！{len(pdf_files)}個のPDFファイルをドロップしました\n\n" + 
                                  "\n".join([Path(f).name for f in pdf_files]))
                self.label.setStyleSheet("""
                    QLabel {
                        border: 3px solid #4CAF50;
                        padding: 40px;
                        font-size: 16px;
                        background-color: #C8E6C9;
                        color: #1B5E20;
                        border-radius: 10px;
                    }
                """)
            else:
                print("❌ ERROR: No valid PDF files in dropEvent")
                event.ignore()
                
        except Exception as e:
            print(f"❌ Exception in dropEvent: {e}")
            import traceback
            traceback.print_exc()
            event.ignore()

def main():
    app = QApplication(sys.argv)
    
    print("=== Linux対応ドラッグ&ドロップテスト開始 ===")
    print(f"Qt version: {app.applicationVersion()}")
    print(f"Platform: {app.platformName()}")
    
    window = LinuxDragDropWindow()
    window.show()
    
    print("テストウィンドウが表示されました")
    print("PDFファイルをドラッグ&ドロップしてテストしてください")
    print("詳細なデバッグ情報がコンソールに表示されます")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
