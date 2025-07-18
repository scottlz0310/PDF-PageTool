# PDF-PageTool

🚀 **プロフェッショナルなPDFページ編集ツール**

PDF-PageToolは、直感的なUIと豊富な機能を持つモダンなPDFページ操作ツールです。複数のPDFファイルを同時に扱い、ページの結合・分割・並び替えを視覚的に操作できます。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)

## ✨ 主な機能

### 📁 ファイル操作
- **複数PDFファイル同時読み込み**（3つ以上対応）
- **ドラッグ&ドロップ**による直感的なファイル追加
- **動的グループボックス**による整理された表示

### 🖼️ ページ操作
- **サムネイル表示**による視覚的なページ管理
- **複数ページ選択**（CTRL/SHIFTクリック、矩形ドラッグ対応）
- **ドラッグ&ドロップ**による自由な順序変更
- **ページ回転**（90°、180°、270°）
- **ページ削除**機能

### 🎨 ユーザビリティ
- **ライト/ダークテーマ**対応
- **サムネイルサイズ調整**（50-300px、リアルタイム解像度変更）
- **水平スクロールバー**による効率的な表示
- **スプリッターアンカリング**による柔軟なレイアウト
- **直感的なメニューシステム**

### ⚙️ 高度な機能
- **バッチ処理**対応
- **設定の保存・復元**
- **ウィンドウ状態記憶**
- **詳細なログ出力**

## 🖥️ システム要件

- **Python**: 3.8以上
- **OS**: Windows / macOS / Linux
- **RAM**: 512MB以上推奨
- **ディスク容量**: 100MB以上

## 🚀 インストール

### 1. リポジトリのクローン
```bash
git clone https://github.com/scottlz0310/PDF-PageTool.git
cd PDF-PageTool
```

### 2. 仮想環境の作成（推奨）
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. アプリケーションの起動
```bash
python main.py
```

## 📖 使用方法

### 基本操作
1. **ファイルを開く**: `ファイル` → `開く` またはドラッグ&ドロップ
2. **ページ選択**: クリック、CTRL+クリック、SHIFT+クリック、矩形ドラッグ
3. **順序変更**: サムネイルをドラッグして出力エリアの好きな位置にドロップ
4. **保存**: `ファイル` → `保存` または `名前を付けて保存`

### ⚠️ 既知の制約
- **Linux/WSL (Wayland)環境**: ドラッグ&ドロップ機能が制限されます。代替手段として「ファイル → 開く」メニューをご利用ください。

### 高度な操作
- **サムネイルサイズ変更**: `ツール` → `サムネイルサイズ設定`
- **テーマ変更**: `ツール` → `テーマ設定`
- **詳細設定**: `ツール` → `詳細設定`

## 🛠️ 技術スタック

- **GUI Framework**: PyQt6
- **PDF処理**: PyPDF2, pdf2image
- **画像処理**: Pillow
- **テーマ管理**: カスタムテーママネージャー

## 📁 プロジェクト構成

```
PDF-PageTool/
├── main.py                 # アプリケーションエントリーポイント
├── requirements.txt        # Python依存関係
├── src/                    # ソースコード
│   ├── ui/                 # ユーザーインターフェース
│   ├── pdf_operations/     # PDF操作ロジック
│   └── utils/              # ユーティリティ
├── doc/                    # ドキュメント
└── asset/                  # アセット（アイコンなど）
```

## 🤝 コントリビューション

プルリクエストやイシューの報告を歓迎します！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📜 変更履歴

### v1.0.0 (2025-01-17)
- ✅ 初回リリース
- ✅ 15項目のUI改善実装完了
- ✅ 複数ページ選択機能
- ✅ 動的グループボックス対応
- ✅ サムネイルサイズ設定機能
- ✅ 水平スクロールバー実装
- ✅ テーマシステム完全対応

## 📄 ライセンス

このプロジェクトはMITライセンスの下で提供されます。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 👨‍💻 開発者

**scottlz0310**
- GitHub: [@scottlz0310](https://github.com/scottlz0310)

## 🙏 謝辞

このプロジェクトは以下のオープンソースライブラリを使用しています：
- PyQt6
- PyPDF2
- pdf2image
- Pillow

---

**⭐ 気に入ったらスターをお願いします！**
