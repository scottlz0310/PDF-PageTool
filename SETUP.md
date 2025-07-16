# セットアップガイド

## 事前準備

### 1. Pythonのインストール
- Python 3.8以上が必要です
- [Python公式サイト](https://www.python.org/downloads/)からダウンロード

### 2. システム依存関係（pdf2image用）

#### Windows
```bash
# Chocolateyを使用する場合
choco install poppler

# または手動でpopplerをダウンロード・設定
# https://blog.alivate.com.au/poppler-windows/
```

#### macOS
```bash
# Homebrewを使用
brew install poppler
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install poppler-utils
```

## インストール手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/scottlz0310/PDF-PageTool.git
cd PDF-PageTool
```

### 2. 仮想環境の作成
```bash
python -m venv venv
```

### 3. 仮想環境のアクティベート
#### Windows (PowerShell)
```powershell
venv\Scripts\Activate.ps1
```

#### Windows (Command Prompt)
```cmd
venv\Scripts\activate.bat
```

#### macOS/Linux
```bash
source venv/bin/activate
```

### 4. 依存関係のインストール
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. アプリケーションの起動
```bash
python main.py
```

## トラブルシューティング

### pdf2imageエラー
```
pdf2image.exceptions.PDFInfoNotInstalledError
```
**解決方法**: popplerがインストールされていません。上記のシステム依存関係をインストールしてください。

### PyQt6インストールエラー
```
ERROR: Could not find a version that satisfies the requirement PyQt6
```
**解決方法**: 
- Pythonバージョンを確認（3.8以上必要）
- pipを最新版に更新: `pip install --upgrade pip`

### メモリエラー
```
MemoryError: cannot allocate memory
```
**解決方法**: 
- 大きなPDFファイルを処理する際は、サムネイルサイズを小さく設定
- 一度に処理するページ数を制限

### テーマが適用されない
- アプリケーションを再起動
- `ツール` → `詳細設定` でテーマ設定を確認

## 開発環境のセットアップ

### 追加の開発依存関係
```bash
pip install pytest pytest-qt black flake8 mypy
```

### コード品質チェック
```bash
# フォーマット
black src/

# リント
flake8 src/

# 型チェック
mypy src/
```

### テスト実行
```bash
pytest tests/
```

## パフォーマンス最適化

### 推奨設定
- **サムネイルサイズ**: 160px（デフォルト）
- **メモリ使用量**: 大きなPDFの場合は一度に少ないページ数で処理
- **テーマ**: システムに合わせて選択

### ハードウェア要件
- **最小**: RAM 512MB、CPU 1GHz
- **推奨**: RAM 2GB以上、CPU 2GHz以上
- **ストレージ**: 100MB以上の空き容量
