# PDF-PageTool テストスイート

このディレクトリには、PDF-PageToolの全テストが整理されています。

## ディレクトリ構造

```
tests/
├── __init__.py           # テストパッケージ初期化
├── run_all_tests.py      # 全テスト実行スクリプト
├── README.md            # このファイル
├── debug/               # デバッグ関連
│   ├── debug_test.py    # デバッグテストスクリプト
│   └── *.log           # アプリケーションログファイル
├── unit/                # ユニットテスト
│   └── test_official_theme_manager.py
└── integration/         # 統合テスト
    ├── test_features.py
    ├── test_new_features.py
    └── test_theme_functionality.py
```

## テスト実行方法

### 全テスト実行

```bash
# プロジェクトルートから
python tests/run_all_tests.py

# または
python -m tests.run_all_tests
```

### 個別テスト実行

```bash
# デバッグテスト
python tests/debug/debug_test.py

# ユニットテスト
python tests/unit/test_official_theme_manager.py

# 統合テスト  
python tests/integration/test_features.py
python tests/integration/test_new_features.py
python tests/integration/test_theme_functionality.py
```

## テストカテゴリ

### 🔍 デバッグテスト
- アプリケーションの基本動作確認
- 設定ダイアログ、メインウィンドウ、ログレベル、テーマシステムのテスト
- 問題の修正確認とデバッグ情報の収集

### 🧪 ユニットテスト
- 個別コンポーネントの単体テスト
- テーママネージャーの機能テスト

### 🔗 統合テスト
- 複数コンポーネント間の連携テスト
- 新機能の統合テスト
- UI機能の総合テスト

## ログファイル

`debug/` ディレクトリには、アプリケーション実行時に生成されたログファイルが保存されています。
これらのログは問題の診断やデバッグに使用されます。

## 注意事項

- テスト実行前に、仮想環境をアクティベートし、必要な依存関係がインストールされていることを確認してください
- PyQt6を使用するテストは、GUIが利用可能な環境で実行する必要があります
- 一部のテストはファイルシステムへの書き込み権限が必要です
