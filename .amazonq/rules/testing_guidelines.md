# PDF-PageTool テストガイドライン

## テスト戦略

### テストピラミッド
```
E2E Tests (少数)
├── 統合テスト (中程度)
└── 単体テスト (多数)
```

### テスト種別
- **単体テスト**: 個別関数・メソッドのテスト
- **統合テスト**: モジュール間の連携テスト
- **UI テスト**: ユーザーインターフェースのテスト
- **E2E テスト**: エンドツーエンドのワークフローテスト

## 単体テスト

### テスト対象
- PDF操作ロジック
- ユーティリティ関数
- 設定管理
- ログ機能

```python
import unittest
from unittest.mock import Mock, patch
from src.pdf_operations import PDFOperations, PDFPageInfo

class TestPDFOperations(unittest.TestCase):
    def setUp(self):
        self.pdf_ops = PDFOperations(log_level="ERROR")

    def test_load_pdf_success(self):
        """PDFファイル読み込み成功テスト"""
        with patch('os.path.exists', return_value=True):
            with patch('PyPDF2.PdfReader') as mock_reader:
                mock_reader.return_value.pages = [Mock(), Mock()]
                pages = self.pdf_ops.load_pdf("test.pdf")
                self.assertEqual(len(pages), 2)

    def test_load_pdf_file_not_found(self):
        """PDFファイル未存在エラーテスト"""
        with self.assertRaises(FileNotFoundError):
            self.pdf_ops.load_pdf("nonexistent.pdf")
```

## 統合テスト

### テスト対象
- UI とビジネスロジックの連携
- ファイル操作とUI更新
- テーマシステムの動作

```python
class TestMainWindowIntegration(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.main_window = MainWindow(log_level="ERROR")

    def test_load_pdf_files_integration(self):
        """PDFファイル読み込み統合テスト"""
        test_files = ["test1.pdf", "test2.pdf"]
        with patch.object(self.main_window, 'pdf_operations') as mock_ops:
            mock_ops.load_pdf.return_value = [PDFPageInfo("test.pdf", 0)]
            self.main_window.load_pdf_files(test_files)
            self.assertEqual(len(self.main_window.loaded_files), 2)
```

## UIテスト

### PyQt6テストパターン
```python
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

class TestMainWindowUI(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.main_window = MainWindow()

    def test_menu_actions(self):
        """メニューアクションテスト"""
        # ファイルメニューのテスト
        QTest.mouseClick(self.main_window.ui.actionOpen, Qt.MouseButton.LeftButton)
        # ダイアログが開かれることを確認

    def test_drag_drop(self):
        """ドラッグ&ドロップテスト"""
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile("test.pdf")])

        drag_event = QDragEnterEvent(
            QPoint(0, 0), Qt.DropAction.CopyAction, mime_data,
            Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
        )

        self.main_window.dragEnterEvent(drag_event)
        self.assertTrue(drag_event.isAccepted())
```

## モックとスタブ

### 外部依存のモック化
```python
# ファイルシステムのモック
@patch('os.path.exists')
@patch('tempfile.mkdtemp')
def test_with_mocked_filesystem(self, mock_mkdtemp, mock_exists):
    mock_exists.return_value = True
    mock_mkdtemp.return_value = "/tmp/test"
    # テスト実行

# PDF処理ライブラリのモック
@patch('pdf2image.convert_from_path')
def test_thumbnail_generation(self, mock_convert):
    mock_convert.return_value = [Mock()]
    # サムネイル生成テスト
```

## テストデータ管理

### テスト用PDFファイル
```python
class TestDataManager:
    @staticmethod
    def create_test_pdf(pages: int = 1) -> str:
        """テスト用PDFファイルを作成"""
        from reportlab.pdfgen import canvas

        filename = f"test_{pages}pages.pdf"
        c = canvas.Canvas(filename)
        for i in range(pages):
            c.drawString(100, 750, f"Test Page {i+1}")
            c.showPage()
        c.save()
        return filename

    @staticmethod
    def cleanup_test_files():
        """テストファイルをクリーンアップ"""
        import glob
        for file in glob.glob("test_*.pdf"):
            os.remove(file)
```

## パフォーマンステスト

### メモリ使用量テスト
```python
import psutil
import os

class TestPerformance(unittest.TestCase):
    def test_memory_usage(self):
        """メモリ使用量テスト"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 大量のPDFファイルを読み込み
        large_files = [f"large_file_{i}.pdf" for i in range(10)]
        self.main_window.load_pdf_files(large_files)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # メモリ使用量が閾値以下であることを確認
        self.assertLess(memory_increase, 100 * 1024 * 1024)  # 100MB
```

## テスト実行

### テストランナー設定
```python
# tests/run_all_tests.py
import unittest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """全テストを実行"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

### CI/CD統合
```bash
# テスト実行コマンド
python -m pytest tests/ -v --cov=src --cov-report=html

# 静的解析
flake8 src/ tests/
mypy src/
```

## テストカバレッジ

### カバレッジ目標
- **単体テスト**: 80%以上
- **統合テスト**: 主要ワークフローをカバー
- **UI テスト**: 重要な操作をカバー

### カバレッジレポート
```python
# .coveragerc
[run]
source = src/
omit =
    */tests/*
    */venv/*
    */build/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## デバッグとトラブルシューティング

### テストデバッグ
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# テスト実行時のログ出力
def test_with_debug_logging(self):
    with self.assertLogs('PDF-PageTool', level='DEBUG') as log:
        self.pdf_ops.load_pdf("test.pdf")
        self.assertIn('Loading PDF file', log.output[0])
```

### テスト環境の分離
- 各テストで独立した環境を使用
- 一時ディレクトリの使用
- テスト後のクリーンアップ確実実行
