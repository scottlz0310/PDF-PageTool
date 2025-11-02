# PDF-PageTool パフォーマンス最適化ガイドライン

## メモリ管理

### サムネイル画像の最適化
```python
# 適切なサムネイルサイズの設定
THUMBNAIL_SIZES = {
    'small': (100, 133),    # 4:3比率
    'medium': (150, 200),   # デフォルト
    'large': (200, 267)     # 大きめ
}

# メモリ効率的な画像リサイズ
def optimize_thumbnail(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    # アスペクト比を保持してリサイズ
    image.thumbnail(target_size, Image.Resampling.LANCZOS)

    # 不要なメタデータを削除
    if hasattr(image, '_getexif'):
        image._getexif = lambda: None

    return image
```

### 一時ファイル管理
```python
class TempFileManager:
    def __init__(self, max_cache_size: int = 100):
        self.temp_dir = tempfile.mkdtemp(prefix="pdf_pagetool_")
        self.cache_files = {}
        self.max_cache_size = max_cache_size

    def cleanup_old_files(self):
        """古いキャッシュファイルを削除"""
        if len(self.cache_files) > self.max_cache_size:
            # 最も古いファイルから削除
            sorted_files = sorted(self.cache_files.items(),
                                key=lambda x: x[1]['created_at'])

            for file_path, _ in sorted_files[:10]:  # 10個ずつ削除
                try:
                    os.remove(file_path)
                    del self.cache_files[file_path]
                except OSError:
                    pass
```

## 非同期処理の最適化

### スレッドプール使用
```python
from concurrent.futures import ThreadPoolExecutor
import threading

class OptimizedPDFLoader:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loading_lock = threading.Lock()

    def load_multiple_pdfs(self, pdf_files: List[str]) -> Dict[str, List[PDFPageInfo]]:
        """複数PDFファイルを並列読み込み"""
        futures = {}

        for pdf_file in pdf_files:
            future = self.executor.submit(self._load_single_pdf, pdf_file)
            futures[pdf_file] = future

        results = {}
        for pdf_file, future in futures.items():
            try:
                results[pdf_file] = future.result(timeout=30)
            except Exception as e:
                self.logger.error(f"Failed to load {pdf_file}: {e}")

        return results
```

### サムネイル生成の最適化
```python
class ThumbnailGenerator:
    def __init__(self):
        self.generation_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def _worker(self):
        """バックグラウンドでサムネイル生成"""
        while True:
            try:
                page_info, callback = self.generation_queue.get(timeout=1)
                thumbnail_path = self._generate_thumbnail(page_info)
                callback(thumbnail_path)
                self.generation_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Thumbnail generation error: {e}")

    def generate_async(self, page_info: PDFPageInfo, callback):
        """非同期でサムネイル生成を依頼"""
        self.generation_queue.put((page_info, callback))
```

## UI レスポンシブ性

### 遅延読み込み（Lazy Loading）
```python
class LazyThumbnailWidget(QWidget):
    def __init__(self, page_info: PDFPageInfo):
        super().__init__()
        self.page_info = page_info
        self.thumbnail_loaded = False
        self.placeholder_pixmap = self._create_placeholder()

    def paintEvent(self, event):
        if not self.thumbnail_loaded and self.isVisible():
            # 表示されたタイミングでサムネイル読み込み
            self._load_thumbnail_async()
        super().paintEvent(event)

    def _load_thumbnail_async(self):
        """非同期でサムネイル読み込み"""
        def on_thumbnail_ready(thumbnail_path):
            self.thumbnail_loaded = True
            self.update()  # 再描画

        thumbnail_generator.generate_async(self.page_info, on_thumbnail_ready)
```

### 仮想化スクロール
```python
class VirtualizedScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.visible_items = {}
        self.item_height = 200
        self.buffer_size = 5  # 表示領域外のバッファ

    def update_visible_items(self):
        """表示領域内のアイテムのみを更新"""
        viewport_rect = self.viewport().rect()
        scroll_value = self.verticalScrollBar().value()

        start_index = max(0, (scroll_value // self.item_height) - self.buffer_size)
        end_index = min(len(self.all_items),
                       ((scroll_value + viewport_rect.height()) // self.item_height) + self.buffer_size)

        # 表示範囲外のアイテムを非表示
        for index, item in self.visible_items.items():
            if index < start_index or index > end_index:
                item.setVisible(False)

        # 表示範囲内のアイテムを表示
        for index in range(start_index, end_index):
            if index not in self.visible_items:
                self.visible_items[index] = self._create_item(index)
            self.visible_items[index].setVisible(True)
```

## データ構造の最適化

### 効率的なページ管理
```python
from collections import OrderedDict
import weakref

class OptimizedPageManager:
    def __init__(self):
        # 順序を保持しつつ高速アクセス
        self.pages = OrderedDict()
        # 弱参照でメモリリークを防止
        self.thumbnail_cache = weakref.WeakValueDictionary()

    def add_page(self, page_info: PDFPageInfo):
        page_key = f"{page_info.source_file}:{page_info.page_number}"
        self.pages[page_key] = page_info

    def get_pages_in_range(self, start: int, end: int) -> List[PDFPageInfo]:
        """指定範囲のページを効率的に取得"""
        items = list(self.pages.items())
        return [page_info for _, page_info in items[start:end]]
```

## ファイルI/O最適化

### バッファリング読み込み
```python
class BufferedPDFReader:
    def __init__(self, buffer_size: int = 8192):
        self.buffer_size = buffer_size
        self.file_cache = {}

    def read_pdf_buffered(self, file_path: str) -> PdfReader:
        """バッファリングしてPDF読み込み"""
        if file_path in self.file_cache:
            return self.file_cache[file_path]

        with open(file_path, 'rb', buffering=self.buffer_size) as file:
            # ファイル内容をメモリに読み込み
            file_data = file.read()
            reader = PdfReader(io.BytesIO(file_data))

            # キャッシュに保存（メモリ使用量に注意）
            if len(self.file_cache) < 10:  # 最大10ファイル
                self.file_cache[file_path] = reader

            return reader
```

## プロファイリングとモニタリング

### パフォーマンス測定
```python
import time
import functools
import psutil
import os

def performance_monitor(func):
    """パフォーマンス測定デコレータ"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # メモリ使用量測定開始
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss

        # 実行時間測定開始
        start_time = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # 測定終了
            end_time = time.perf_counter()
            end_memory = process.memory_info().rss

            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory

            logger.debug(f"{func.__name__} - Time: {execution_time:.3f}s, "
                        f"Memory: {memory_delta / 1024 / 1024:.2f}MB")

    return wrapper

# 使用例
@performance_monitor
def load_large_pdf(file_path: str):
    return pdf_operations.load_pdf(file_path)
```

### メモリリーク検出
```python
import gc
import tracemalloc

class MemoryLeakDetector:
    def __init__(self):
        tracemalloc.start()
        self.snapshots = []

    def take_snapshot(self, label: str):
        """メモリスナップショットを取得"""
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append((label, snapshot))

    def compare_snapshots(self, start_label: str, end_label: str):
        """スナップショット間の差分を比較"""
        start_snapshot = None
        end_snapshot = None

        for label, snapshot in self.snapshots:
            if label == start_label:
                start_snapshot = snapshot
            elif label == end_label:
                end_snapshot = snapshot

        if start_snapshot and end_snapshot:
            top_stats = end_snapshot.compare_to(start_snapshot, 'lineno')

            print(f"Top 10 memory differences between {start_label} and {end_label}:")
            for stat in top_stats[:10]:
                print(stat)
```

## 設定による最適化

### パフォーマンス設定
```python
PERFORMANCE_SETTINGS = {
    'thumbnail_cache_size': 100,
    'max_concurrent_loads': 4,
    'thumbnail_quality': 85,  # JPEG品質
    'enable_lazy_loading': True,
    'buffer_size': 8192,
    'max_memory_usage': 512 * 1024 * 1024,  # 512MB
}

class PerformanceOptimizer:
    def __init__(self, settings: Dict):
        self.settings = settings
        self._apply_optimizations()

    def _apply_optimizations(self):
        """設定に基づいて最適化を適用"""
        if self.settings.get('enable_lazy_loading'):
            self._enable_lazy_loading()

        cache_size = self.settings.get('thumbnail_cache_size', 100)
        self._configure_cache(cache_size)
```
