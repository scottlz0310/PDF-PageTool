# PDF-PageTool コーディング規約

## Python コーディング規約

### 基本原則
- PEP 8に準拠したコーディングスタイル
- 型ヒントを必須とする（Python 3.11+の機能を活用）
- docstringは必須（Google形式推奨）
- 変数名・関数名は日本語コメントで説明

### 型ヒント
```python
from typing import List, Dict, Optional, Tuple
from pathlib import Path

def load_pdf_files(pdf_files: List[str]) -> Dict[str, List[PDFPageInfo]]:
    """PDFファイルを読み込む"""
    pass
```

### エラーハンドリング
- 例外処理は具体的なException型を指定
- ログ出力を必ず行う
- ユーザーフレンドリーなエラーメッセージ

```python
try:
    result = some_operation()
except FileNotFoundError as e:
    self.logger.error(f"ファイルが見つかりません: {e}")
    raise
except Exception as e:
    self.logger.error(f"予期しないエラー: {e}")
    raise
```

## PyQt6 固有の規約

### シグナル・スロット
- シグナル名は動詞形（clicked, changed, etc.）
- スロット名は `_on_` プレフィックス

```python
# シグナル定義
file_loaded = pyqtSignal(str, list)

# スロット接続
self.ui.actionOpen.triggered.connect(self._on_open_triggered)
```

### ウィジェット命名
- UI要素は機能を表す名前
- プレフィックスでタイプを識別（btn, lbl, etc.）

### レイアウト管理
- 動的レイアウト変更時は必ずupdateGeometry()を呼び出す
- メモリリークを防ぐため、不要なウィジェットは適切に削除

## ログ出力規約

### ログレベル使い分け
- **DEBUG**: 開発時のデバッグ情報
- **INFO**: 一般的な動作情報
- **WARNING**: 警告（処理は継続）
- **ERROR**: エラー（処理中断の可能性）

### ログメッセージ形式
```python
self.logger.info(f"PDFファイル読み込み開始: {file_path}")
self.logger.error(f"サムネイル生成失敗: {page_info} - {error}")
```

## ファイル構成規約

### モジュール構成
- 1ファイル500行以内を目安
- 機能別にモジュールを分割
- `__init__.py`で公開APIを明示

### インポート順序
1. 標準ライブラリ
2. サードパーティライブラリ
3. プロジェクト内モジュール

```python
import os
from pathlib import Path
from typing import List, Dict

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from ..utils.logger import get_logger
from .pdf_handler import PDFOperations
```
