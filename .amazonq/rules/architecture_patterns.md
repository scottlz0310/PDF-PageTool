# PDF-PageTool アーキテクチャパターン

## 全体アーキテクチャ

### レイヤー構成
```
Presentation Layer (UI)
├── main_window.py          # メインウィンドウ
├── page_widgets.py         # ページウィジェット
├── settings_dialog.py      # 設定ダイアログ
└── theme_manager.py        # テーマ管理

Business Logic Layer
├── pdf_operations/         # PDF操作ロジック
└── batch_processor.py      # バッチ処理

Infrastructure Layer
├── utils/logger.py         # ログ管理
├── utils/settings_manager.py # 設定管理
└── temp file management    # 一時ファイル管理
```

## 設計パターン

### シングルトンパターン
- SettingsManager
- ThemeManager
- Logger

```python
_instance = None

def get_instance():
    global _instance
    if _instance is None:
        _instance = ClassName()
    return _instance
```

### オブザーバーパターン
- PyQt6のシグナル・スロット機構を活用
- UI更新とビジネスロジックの分離

```python
class PDFLoaderThread(QThread):
    file_loaded = pyqtSignal(str, list)
    
    def run(self):
        # 処理完了時にシグナル発行
        self.file_loaded.emit(file_path, pages)
```

### ファクトリーパターン
- ウィジェット生成
- テーマ適用

```python
def create_main_window(pdf_files: List[str] = None) -> MainWindow:
    return MainWindow(pdf_files)
```

## データフロー

### PDFファイル読み込みフロー
1. ユーザーがファイル選択
2. PDFLoaderThreadで非同期読み込み
3. ページ情報をPDFPageInfoオブジェクトに格納
4. サムネイル生成（別スレッド）
5. UIに表示

### ページ操作フロー
1. ユーザーがページ選択
2. 操作コマンド実行（回転、削除等）
3. PDFPageInfoオブジェクト更新
4. サムネイル再生成
5. UI更新

## メモリ管理

### 一時ファイル管理
- tempfileモジュールを使用
- アプリケーション終了時に自動クリーンアップ
- サムネイル画像は一時ディレクトリに保存

### リソース管理
```python
def cleanup(self):
    """リソースクリーンアップ"""
    if self.temp_dir and os.path.exists(self.temp_dir):
        shutil.rmtree(self.temp_dir)
```

## エラーハンドリング戦略

### 階層的エラーハンドリング
1. **UI層**: ユーザーフレンドリーなメッセージ表示
2. **ビジネス層**: 具体的なエラー処理とログ出力
3. **インフラ層**: システムレベルのエラー処理

### 例外の種類
- `FileNotFoundError`: ファイル関連エラー
- `ValueError`: データ検証エラー
- `RuntimeError`: 実行時エラー
- `Exception`: その他の予期しないエラー

## 設定管理

### 設定の種類
- **ユーザー設定**: テーマ、ウィンドウサイズ等
- **アプリケーション設定**: ログレベル、一時ディレクトリ等
- **システム設定**: ファイルパス、依存関係等

### 設定保存場所
- ユーザーホームディレクトリ
- JSON形式で保存
- 設定変更時の自動保存

## テーマシステム

### テーマ構成
- 統合テーママネージャー使用
- JSON形式でテーマ定義
- リアルタイムプレビュー対応

### テーマ適用フロー
1. テーマ選択
2. 設定ファイル更新
3. スタイルシート生成
4. アプリケーション全体に適用
5. 個別ウィジェットに適用