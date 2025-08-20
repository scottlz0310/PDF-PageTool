# PDF-PageTool UI開発ガイドライン

## PyQt6 UI開発規約

### ウィジェット設計原則
- **レスポンシブデザイン**: 異なる画面サイズに対応
- **アクセシビリティ**: キーボードナビゲーション対応
- **直感的操作**: ドラッグ&ドロップ、右クリックメニュー
- **視覚的フィードバック**: 操作状態の明確な表示

### レイアウト管理
```python
# グリッドレイアウトの使用例
layout = QtWidgets.QGridLayout()
layout.setSpacing(10)
layout.addWidget(widget, row, col)

# 動的レイアウト更新
widget.updateGeometry()
layout.update()
```

### ドラッグ&ドロップ実装
```python
def dragEnterEvent(self, event: QDragEnterEvent):
    if event.mimeData().hasUrls():
        pdf_files = [url.toLocalFile() for url in event.mimeData().urls() 
                    if url.toLocalFile().lower().endswith('.pdf')]
        if pdf_files:
            event.acceptProposedAction()
    event.ignore()

def dropEvent(self, event: QDropEvent):
    files = [url.toLocalFile() for url in event.mimeData().urls()]
    self.load_pdf_files(files)
    event.acceptProposedAction()
```

## テーマシステム統合

### テーマ適用パターン
```python
# 統合テーママネージャーの使用
self.theme_manager = get_integrated_theme_manager(self.settings_manager)
self.theme_manager.apply_theme_to_widget(self)

# 個別ウィジェットへの適用
for widget in self.findChildren(QWidget):
    self.theme_manager.apply_theme_to_widget(widget)
```

### カスタムスタイル
- QSSファイルでカスタムスタイル定義
- テーマ変更時の動的スタイル更新
- ダークモード対応

## ユーザーインタラクション

### マウス操作
- **左クリック**: 選択
- **Ctrl+左クリック**: 複数選択
- **Shift+左クリック**: 範囲選択
- **右クリック**: コンテキストメニュー
- **ダブルクリック**: アクション実行

### キーボードショートカット
```python
# ショートカット定義
shortcuts = {
    'Ctrl+O': self.open_files,
    'Ctrl+S': self.save_pdf,
    'Ctrl+Q': self.close,
    'Delete': self.remove_selected_pages,
    'Ctrl+R': lambda: self.rotate_selected_pages(90)
}
```

## サムネイル表示システム

### サムネイル生成
```python
def generate_thumbnail(self, page_info: PDFPageInfo, size: Tuple[int, int] = (150, 200)) -> str:
    # pdf2imageでページを画像変換
    images = convert_from_path(page_info.source_file, 
                              first_page=page_info.page_number + 1,
                              last_page=page_info.page_number + 1)
    
    # サムネイルサイズにリサイズ
    image = images[0]
    image.thumbnail(size, Image.Resampling.LANCZOS)
    
    # 一時ファイルに保存
    thumbnail_path = os.path.join(self.temp_dir, f"thumb_{uuid.uuid4()}.png")
    image.save(thumbnail_path, "PNG")
    return thumbnail_path
```

### サムネイルキャッシュ
- メモリ効率を考慮したキャッシュシステム
- サイズ変更時の自動再生成
- 一時ファイルの適切な管理

## 動的UI要素

### 動的グループボックス
```python
def _create_dynamic_group_box(self, file_path: str, file_index: int):
    group_box = QtWidgets.QGroupBox(self.ui.scrollAreaWidgetInputs)
    group_box.setTitle(Path(file_path).name)
    
    # レイアウト設定
    layout = QtWidgets.QGridLayout(group_box)
    layout.setSpacing(10)
    
    # 親レイアウトに追加
    self.ui.horizontalLayoutInputs.addWidget(group_box)
    self.dynamic_group_boxes.append(group_box)
```

### スクロールエリア管理
- 水平スクロール対応
- 動的サイズ調整
- スムーズなスクロール体験

## 非同期処理とUI更新

### スレッド使用パターン
```python
class PDFLoaderThread(QThread):
    progress_updated = pyqtSignal(str, int, int)
    file_loaded = pyqtSignal(str, list)
    
    def run(self):
        for i, file_path in enumerate(self.pdf_files):
            pages = self.load_pdf(file_path)
            self.file_loaded.emit(file_path, pages)
            self.progress_updated.emit(file_path, i+1, len(self.pdf_files))
```

### プログレス表示
- 長時間処理のプログレスバー表示
- キャンセル機能の提供
- 非ブロッキングUI

## エラー表示とユーザーフィードバック

### メッセージボックス
```python
# 情報表示
QMessageBox.information(self, "完了", "PDFファイルを保存しました")

# 警告表示
QMessageBox.warning(self, "警告", "ファイルが見つかりません")

# エラー表示
QMessageBox.critical(self, "エラー", "保存に失敗しました")
```

### ステータスバー
- 操作状況の表示
- 一時的なメッセージ表示
- プログレス情報の表示

## アクセシビリティ

### キーボードナビゲーション
- Tab順序の適切な設定
- ショートカットキーの提供
- フォーカス表示の明確化

### 視覚的配慮
- 十分なコントラスト比
- 適切なフォントサイズ
- 色だけに依存しない情報表示