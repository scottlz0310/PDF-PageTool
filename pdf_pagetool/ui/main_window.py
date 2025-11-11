"""
PDF-PageTool Main Window

メインGUIアプリケーションウィンドウの実装
"""

import os
from pathlib import Path
from typing import Any

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from ..pdf_operations import PDFOperations, PDFPageInfo
from ..utils.logger import get_logger
from ..utils.settings_manager import SettingsManager
from .batch_processor import BatchProcessorDialog
from .integrated_theme_manager import get_integrated_theme_manager
from .keyboard_shortcuts import get_shortcut_manager, setup_main_window_shortcuts
from .main_window_ui import Ui_MainWindow
from .page_widgets import OutputArea, PageThumbnailWidget
from .settings_dialog import SettingsDialog
from .thumbnail_size_dialog import ThumbnailSizeDialog


class PDFLoaderThread(QThread):
    """PDFファイルの読み込みを別スレッドで行うクラス"""

    # シグナル定義
    file_loaded = pyqtSignal(str, list)  # ファイルパス, ページリスト
    thumbnail_generated = pyqtSignal(str, str, object)  # ファイルパス, サムネイルパス, ページ情報
    error_occurred = pyqtSignal(str, str)  # ファイルパス, エラーメッセージ
    progress_updated = pyqtSignal(str, int, int)  # ファイルパス, 現在, 総数

    def __init__(self, pdf_files: list[str], log_level: str = "INFO"):
        super().__init__()
        self.pdf_files = pdf_files
        self.pdf_ops = PDFOperations(log_level)
        self.logger = get_logger("PDFLoaderThread", log_level)

    def run(self):
        """スレッドのメイン処理"""
        try:
            for pdf_file in self.pdf_files:
                self.logger.debug(f"Loading PDF: {pdf_file}")

                # PDFファイルを読み込み
                pages = self.pdf_ops.load_pdf(pdf_file)
                self.file_loaded.emit(pdf_file, pages)

                # 各ページのサムネイルを生成
                for i, page_info in enumerate(pages):
                    try:
                        thumbnail_path = self.pdf_ops.generate_thumbnail(page_info)
                        self.thumbnail_generated.emit(pdf_file, thumbnail_path, page_info)
                        self.progress_updated.emit(pdf_file, i + 1, len(pages))
                    except Exception as e:
                        self.logger.error(f"Failed to generate thumbnail for page {i + 1}: {e}")
                        self.error_occurred.emit(pdf_file, f"サムネイル生成エラー (ページ {i + 1}): {e}")

        except Exception as e:
            self.logger.error(f"PDF loading error: {e}")
            self.error_occurred.emit("", f"PDFファイル読み込みエラー: {e}")


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""

    def __init__(self, pdf_files: list[str] | None = None, log_level: str = "INFO"):
        super().__init__()

        # 設定管理システム初期化
        self.settings_manager = SettingsManager()

        # ログ設定（設定から取得）
        self.log_level = self.settings_manager.get("log_level", log_level)
        self.logger = get_logger("MainWindow", str(self.log_level))

        # 統合テーママネージャーを初期化
        self.theme_manager = get_integrated_theme_manager(self.settings_manager)

        # ショートカットマネージャーを初期化
        self.shortcut_manager = get_shortcut_manager(self, self.settings_manager)

        # UI設定
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 内部状態
        self.pdf_operations = PDFOperations(self.log_level)
        self.loaded_files: dict[str, list[PDFPageInfo]] = {}
        self.thumbnail_widgets: dict[str, list[PageThumbnailWidget]] = {}
        self.thumbnail_cache: dict[str, str] = {}  # ページキー -> サムネイルパス

        # 動的グループボックス管理
        self.dynamic_group_boxes: list[QtWidgets.QGroupBox] = []
        self.dynamic_layouts: list[QtWidgets.QGridLayout] = []

        # 出力エリアを置き換え
        self.output_area = OutputArea()
        self.output_area.setObjectName("OutputArea")  # テーマ適用のため識別子設定
        self.output_area.page_added.connect(self._on_output_page_added)
        self.output_area.page_removed.connect(self._on_output_page_removed)

        # 出力エリアにサムネイルキャッシュへのアクセスを提供
        self.output_area.get_thumbnail_path = self._get_cached_thumbnail_path

        # 既存の出力エリアを置き換え
        self.ui.gridLayoutOutput.addWidget(self.output_area, 0, 0)

        # ドロップ受け入れ設定（メインウィンドウレベル）
        self.setAcceptDrops(True)
        self.logger.info("Main window drop acceptance enabled")
        self.logger.info(f"Main window acceptDrops status: {self.acceptDrops()}")

        # UI初期化
        self._setup_ui()
        self._connect_signals()

        # 公式Theme-Manager互換のテーマのみを適用（旧テーママネージャーは使用しない）
        # 注意: 両方のテーママネージャーを同時に使用すると競合するため、公式版のみ使用

        # ショートカットを設定
        setup_main_window_shortcuts(self, self.shortcut_manager)

        self._load_window_settings()

        # 初期ファイルがある場合は読み込み
        if pdf_files:
            self.load_pdf_files(pdf_files)

    def _setup_ui(self) -> None:
        """UI初期設定"""
        # ウィンドウタイトル設定
        self.setWindowTitle("PDF-PageTool")

        # ウィンドウアイコン設定
        icon_path = Path(__file__).parent.parent.parent / "asset" / "pdf-tool.ico"
        if icon_path.exists():
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))
            self.logger.debug(f"Window icon set: {icon_path}")
        else:
            self.logger.warning(f"Icon file not found: {icon_path}")

        # メニューバーの問題を修正（クリックのみで展開、オンマウス展開を無効化）
        # より安全なアプローチ：既存のメニューバーを直接制御
        menu_bar = self.ui.menubar if hasattr(self.ui, "menubar") else self.menuBar()
        if menu_bar and hasattr(menu_bar, "setNativeMenuBar"):
            menu_bar.setNativeMenuBar(False)

        # メニューバーでのマウスホバー自動展開を無効にするスタイル設定
        if menu_bar:
            menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: palette(window);
                color: palette(window-text);
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QMenuBar::item:pressed {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """)

        # メニューの設定
        for menu in [self.ui.menuFile, self.ui.menuEdit, self.ui.menuTool, self.ui.menuHelp]:
            if hasattr(menu, "setTearOffEnabled"):
                menu.setTearOffEnabled(False)
            # フォーカス外れたら自動的に閉じる設定
            menu.aboutToHide.connect(lambda: self.setFocus())

        # 出力エリアをドロップターゲットに設定（ページドロップ用）
        # 注意: 外部ファイルドロップはメインウィンドウで処理するため、子ウィジェットでは無効化
        # self.ui.scrollAreaOutput.setAcceptDrops(True)
        # self.ui.scrollAreaWidgetOutput.setAcceptDrops(True)

        # 入力エリアのドロップも無効化（メインウィンドウで処理）
        # self.ui.scrollAreaInputs.setAcceptDrops(True)
        # self.ui.scrollAreaWidgetInputs.setAcceptDrops(True)

        # 初期状態では入力PDFエリアを非表示
        self.ui.groupBoxPDF1.setVisible(False)
        self.ui.groupBoxPDF2.setVisible(False)

        # 上部パネルのスクロールバー設定を初期化
        self._setup_inputs_scroll_area()

        # スプリッターの初期比率を設定（上部:下部 = 1:1）
        self._setup_splitter_proportions()

        # 公式Theme-Manager互換のテーマを適用
        app = QApplication.instance()
        if isinstance(app, QApplication):
            self.theme_manager.apply_theme_to_application(app)

        # メインウィンドウにも直接テーマを適用
        self.theme_manager.apply_theme_to_widget(self)

        # 個別ウィジェットにもテーマを適用（初期化時）
        self._apply_theme_to_widgets()

        # ウィンドウフレームとタイトルバーを強制的にテーマに合わせる
        # 統合テーママネージャーのスタイルシートを適用
        self.theme_manager.apply_theme_to_widget(self)

        # ウィンドウが表示された後にもう一度テーマを適用（確実にテーマが適用されるよう）
        QtCore.QTimer.singleShot(100, self._force_theme_reapply)

        self.logger.debug("UI setup completed")

    def _connect_signals(self) -> None:
        """シグナル・スロット接続"""
        # メニューアクション
        self.ui.actionOpen.triggered.connect(self.open_files)
        self.ui.actionSave.triggered.connect(self.save_pdf)
        self.ui.actionSaveAs.triggered.connect(self.save_pdf_as)
        self.ui.actionClose.triggered.connect(self.close)

        # 編集メニュー
        self.ui.actionRotateRight.triggered.connect(lambda: self.rotate_selected_pages(90))
        self.ui.actionRotateLeft.triggered.connect(lambda: self.rotate_selected_pages(-90))
        self.ui.actionRotate180.triggered.connect(lambda: self.rotate_selected_pages(180))
        self.ui.actionRemovePage.triggered.connect(self.remove_selected_pages)

        # ツールメニュー
        if hasattr(self.ui, "actionBatchProcess"):
            self.ui.actionBatchProcess.triggered.connect(self.open_batch_processor)

        # ヘルプメニュー
        self.ui.actionAbout.triggered.connect(self.show_about)

        # 設定メニュー
        self.ui.actionSettings.triggered.connect(self.open_settings)
        self.ui.actionThumbnailSize.triggered.connect(self.open_thumbnail_size_dialog)

        self.logger.debug("Signals connected")

    def load_pdf_files(self, pdf_files: list[str]) -> None:
        """PDFファイルを読み込み"""
        self.logger.info(f"Loading {len(pdf_files)} PDF files")

        # ローダースレッドを開始
        self.loader_thread = PDFLoaderThread(pdf_files, self.log_level)
        self.loader_thread.file_loaded.connect(self._on_file_loaded)
        self.loader_thread.thumbnail_generated.connect(self._on_thumbnail_generated)
        self.loader_thread.error_occurred.connect(self._on_loading_error)
        self.loader_thread.progress_updated.connect(self._on_progress_updated)
        self.loader_thread.finished.connect(self._on_loading_finished)

        self.loader_thread.start()

    def _on_file_loaded(self, file_path: str, pages: list[PDFPageInfo]) -> None:
        """ファイル読み込み完了時の処理（動的グループボックス対応）"""
        self.loaded_files[file_path] = pages
        self.logger.info(f"Loaded {file_path}: {len(pages)} pages")

        # グループボックスを表示・設定
        file_index = len(self.loaded_files) - 1

        if file_index == 0:
            # 1つ目のファイル - 既存のgroupBoxPDF1を使用
            self.ui.groupBoxPDF1.setVisible(True)
            self.ui.groupBoxPDF1.setTitle(Path(file_path).name)
        elif file_index == 1:
            # 2つ目のファイル - 既存のgroupBoxPDF2を使用
            self.ui.groupBoxPDF2.setVisible(True)
            self.ui.groupBoxPDF2.setTitle(Path(file_path).name)
        else:
            # 3つ目以降 - 動的にグループボックスを作成
            self._create_dynamic_group_box(file_path, file_index)

    def _create_dynamic_group_box(self, file_path: str, file_index: int) -> None:
        """3つ目以降のファイル用の動的グループボックスを作成"""
        try:
            # グループボックスを作成
            group_box = QtWidgets.QGroupBox(self.ui.scrollAreaWidgetInputs)  # 正しい親を指定
            group_box.setTitle(Path(file_path).name)
            group_box.setObjectName(f"groupBoxPDF{file_index + 1}")

            # 垂直レイアウトを作成（PDF1, PDF2と同じ構造）
            vertical_layout = QtWidgets.QVBoxLayout(group_box)
            vertical_layout.setObjectName(f"verticalLayoutPDF{file_index + 1}")

            # スクロールエリアを作成（各グループボックス内のサムネイル用）
            scroll_area = QtWidgets.QScrollArea(group_box)
            scroll_area.setWidgetResizable(True)
            scroll_area.setObjectName(f"scrollAreaPDF{file_index + 1}")

            # スクロールエリア内のウィジェット
            scroll_widget = QtWidgets.QWidget()
            scroll_widget.setObjectName(f"scrollAreaWidgetPDF{file_index + 1}")

            # グリッドレイアウトを作成（サムネイル配置用）
            grid_layout = QtWidgets.QGridLayout(scroll_widget)
            grid_layout.setSpacing(10)
            grid_layout.setObjectName(f"gridLayoutPDF{file_index + 1}")

            # スクロールエリアにウィジェットを設定
            scroll_area.setWidget(scroll_widget)
            vertical_layout.addWidget(scroll_area)

            # 水平レイアウト（scrollAreaWidgetInputs内のhorizontalLayoutInputs）に追加
            self.ui.horizontalLayoutInputs.addWidget(group_box)

            # 上部パネル全体のスクロールエリアのサイズを調整
            self._update_inputs_scroll_area()

            # 管理リストに追加
            self.dynamic_group_boxes.append(group_box)
            self.dynamic_layouts.append(grid_layout)

            self.logger.debug(f"Created dynamic group box for file {file_index + 1}: {Path(file_path).name}")

        except Exception as e:
            self.logger.error(f"Failed to create dynamic group box: {e}")

    def _setup_splitter_proportions(self) -> None:
        """スプリッターの比率を設定（上部パネルと下部パネルの高さ比率）"""
        # ウィンドウの高さを取得
        window_height = self.height()
        # 上部パネルと下部パネルを1:1の比率で設定
        half_height = window_height // 2
        self.ui.splitter.setSizes([half_height, half_height])

        # 上部パネルの最小高さを設定（サムネイルが見える程度）
        self.ui.scrollAreaInputs.setMinimumHeight(200)

        # ウィンドウリサイズ時のスプリッター比率維持
        self.ui.splitter.setStretchFactor(0, 1)  # 上部パネル
        self.ui.splitter.setStretchFactor(1, 1)  # 下部パネル

    def _setup_inputs_scroll_area(self) -> None:
        """上部パネルのスクロールエリアを初期設定"""
        # 水平スクロールバーを表示
        self.ui.scrollAreaInputs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # 垂直スクロールバーは非表示
        self.ui.scrollAreaInputs.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # ウィジェットリサイズ可能
        self.ui.scrollAreaInputs.setWidgetResizable(True)

        # スプリッターによって高さが制御されるため、固定高さは設定しない
        # 代わりに最小高さのみを設定
        if hasattr(self.ui, "scrollAreaWidgetInputs"):
            self.ui.scrollAreaWidgetInputs.setMinimumHeight(160)  # 最小限の高さのみ

    def _update_inputs_scroll_area(self) -> None:
        """上部パネルのスクロールエリアのサイズを更新"""
        try:
            # 現在のグループボックス数を取得
            visible_groups = 0
            if self.ui.groupBoxPDF1.isVisible():
                visible_groups += 1
            if self.ui.groupBoxPDF2.isVisible():
                visible_groups += 1
            visible_groups += len(self.dynamic_group_boxes)

            # 各グループボックスの最小幅を設定（例：600px）
            group_width = 600
            total_width = visible_groups * group_width + (visible_groups - 1) * 10  # 間隔も考慮

            # scrollAreaWidgetInputsの最小幅を設定
            self.ui.scrollAreaWidgetInputs.setMinimumWidth(total_width)

            # 水平スクロールポリシーを確実に有効化
            self.ui.scrollAreaInputs.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.ui.scrollAreaInputs.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            self.logger.debug(f"Updated scroll area for {visible_groups} groups, total width: {total_width}")

        except Exception as e:
            self.logger.error(f"Failed to update inputs scroll area: {e}")

    def _on_thumbnail_generated(self, file_path: str, thumbnail_path: str, page_info: PDFPageInfo) -> None:
        """サムネイル生成完了時の処理"""
        # サムネイルをキャッシュに保存
        cache_key = f"{page_info.source_file}:{page_info.page_number}:{page_info.rotation}"
        self.thumbnail_cache[cache_key] = thumbnail_path

        # サムネイルウィジェットを作成
        thumbnail_widget = PageThumbnailWidget(page_info, thumbnail_path, is_output=False, parent=self)
        thumbnail_widget.clicked.connect(self._on_thumbnail_clicked)
        thumbnail_widget.double_clicked.connect(self._on_thumbnail_double_clicked)
        thumbnail_widget.right_clicked.connect(self._on_thumbnail_right_clicked)

        # 適切なレイアウトに追加
        if file_path not in self.thumbnail_widgets:
            self.thumbnail_widgets[file_path] = []

        self.thumbnail_widgets[file_path].append(thumbnail_widget)

        # レイアウトに配置
        if len(self.loaded_files) == 1 or file_path == list(self.loaded_files.keys())[0]:
            layout = self.ui.gridLayoutPDF1
        elif len(self.loaded_files) == 2 or file_path == list(self.loaded_files.keys())[1]:
            layout = self.ui.gridLayoutPDF2
        else:
            # 動的グループボックスの場合
            index = list(self.loaded_files.keys()).index(file_path)
            layout = self.dynamic_layouts[index - 2]  # 最初の2つは固定グループボックス

        row = page_info.page_number // 3
        col = page_info.page_number % 3
        layout.addWidget(thumbnail_widget, row, col)

        # スクロールエリアのサイズを更新
        self._update_inputs_scroll_area()

    def _get_cached_thumbnail_path(self, page_info: PDFPageInfo) -> str | None:
        """キャッシュからサムネイルパスを取得"""
        cache_key = f"{page_info.source_file}:{page_info.page_number}:{page_info.rotation}"
        cached_path = self.thumbnail_cache.get(cache_key)

        if cached_path and os.path.exists(cached_path):
            return cached_path

        # キャッシュにない場合は新しく生成
        try:
            thumbnail_path = self.pdf_operations.generate_thumbnail(page_info)
            self.thumbnail_cache[cache_key] = thumbnail_path
            return thumbnail_path
        except Exception as e:
            self.logger.error(f"Failed to generate thumbnail: {e}")
            return None

    def _on_loading_error(self, file_path: str, error_message: str) -> None:
        """読み込みエラー時の処理"""
        self.logger.error(f"Loading error for {file_path}: {error_message}")
        QMessageBox.warning(self, "読み込みエラー", error_message)

    def _on_progress_updated(self, file_path: str, current: int, total: int) -> None:
        """進捗更新"""
        self.logger.debug(f"Progress {file_path}: {current}/{total}")
        # TODO: プログレスバー表示

    def _on_loading_finished(self) -> None:
        """読み込み完了"""
        self.logger.info("All files loaded successfully")
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("ファイル読み込み完了", 3000)

    def _on_thumbnail_clicked(self, page_info: PDFPageInfo) -> None:
        """サムネイルクリック時の処理"""
        self.logger.debug(f"Thumbnail clicked: {page_info}")
        # TODO: ページ選択状態の管理

    def _on_thumbnail_double_clicked(self, page_info: PDFPageInfo) -> None:
        """サムネイルダブルクリック時の処理（出力エリアに追加）"""
        self.logger.debug(f"Adding page to output: {page_info}")

        # サムネイルパスを取得
        thumbnail_path = page_info.thumbnail_path
        if not thumbnail_path:
            # サムネイルパスが設定されていない場合は再生成
            try:
                thumbnail_path = self.pdf_operations.generate_thumbnail(page_info)
            except Exception as e:
                self.logger.error(f"Failed to generate thumbnail: {e}")
                return

        # 出力エリアに追加
        self.output_area.add_page(page_info, thumbnail_path)

    def _on_output_page_added(self, page_info: PDFPageInfo) -> None:
        """出力エリアにページが追加された時の処理"""
        self.logger.info(f"Page added to output: {page_info}")
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(f"ページを出力に追加しました: ページ {page_info.page_number + 1}", 2000)

    def _on_output_page_removed(self, page_info: PDFPageInfo) -> None:
        """出力エリアからページが削除された時の処理"""
        self.logger.info(f"Page removed from output: {page_info}")
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(f"ページを出力から削除しました: ページ {page_info.page_number + 1}", 2000)

    def open_files(self) -> None:
        """ファイルを開くダイアログ"""
        files, _ = QFileDialog.getOpenFileNames(self, "PDFファイルを選択", "", "PDF Files (*.pdf)")
        if files:
            self.load_pdf_files(files)

    def _on_thumbnail_right_clicked(self, page_info: PDFPageInfo) -> None:
        """サムネイル右クリック時の処理"""
        self.logger.debug(f"Thumbnail right-clicked: {page_info}")
        # TODO: コンテキストメニュー表示

    def save_pdf(self) -> None:
        """PDFを保存"""
        output_pages = self.output_area.get_pages()
        if not output_pages:
            QMessageBox.information(self, "情報", "出力するページが選択されていません")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "PDFファイルを保存", "output.pdf", "PDF Files (*.pdf)")

        if file_path:
            try:
                self.pdf_operations.merge_pages(output_pages, file_path)
                QMessageBox.information(self, "完了", f"PDFファイルを保存しました: {file_path}")
                self.logger.info(f"PDF saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"保存に失敗しました: {e}")
                self.logger.error(f"Save failed: {e}")

    def save_pdf_as(self) -> None:
        """名前を付けてPDFを保存"""
        self.save_pdf()

    def rotate_selected_pages(self, angle: int) -> None:
        """選択されたページを回転"""
        # TODO: 選択されたページの回転処理
        self.logger.debug(f"Rotate pages by {angle} degrees")

    def remove_selected_pages(self) -> None:
        """選択されたページを削除"""
        # TODO: 選択されたページの削除処理
        self.logger.debug("Remove selected pages")

    def show_about(self) -> None:
        """バージョン情報表示"""
        QMessageBox.about(
            self,
            "PDF-PageTool について",
            "PDF-PageTool v0.1.0\n\nPDFページの抽出・結合ツール\nシンプルで直感的な操作を提供します。",
        )

    def open_settings(self) -> None:
        """設定ダイアログを開く"""
        try:
            current_settings = self.settings_manager.get_all()
            dialog = SettingsDialog(current_settings, self)

            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                new_settings = dialog.get_settings()
                self.settings_manager.update(new_settings)
                self.settings_manager.save_settings()

                # 設定変更を適用
                self._apply_settings_changes(new_settings)

                self.logger.info("Settings updated")

        except Exception as e:
            self.logger.error(f"Failed to open settings dialog: {e}")
            QMessageBox.warning(self, "エラー", f"設定ダイアログの表示に失敗しました: {e}")

    def open_thumbnail_size_dialog(self) -> None:
        """サムネイルサイズ設定ダイアログを開く"""
        try:
            current_size = self.settings_manager.get("thumbnail_size", 160)
            dialog = ThumbnailSizeDialog(current_size, self)

            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                new_size = dialog.get_size()
                self.settings_manager.set("thumbnail_size", new_size)
                self.settings_manager.save_settings()
                self._update_thumbnail_sizes(new_size)
                self.logger.info(f"Thumbnail size updated to {new_size}px")

        except Exception as e:
            self.logger.error(f"Error opening thumbnail size dialog: {e}")
            QMessageBox.critical(self, "エラー", f"サムネイルサイズ設定ダイアログを開く際にエラーが発生しました: {e}")

    def _apply_settings_changes(self, new_settings: dict[str, Any]) -> None:
        """設定変更を適用"""
        try:
            # ログレベルの変更
            if new_settings.get("log_level") != self.log_level:
                self.log_level = new_settings.get("log_level", "INFO")
                self.logger = get_logger("MainWindow", self.log_level)
                self.pdf_operations = PDFOperations(self.log_level)

            # テーマの変更
            theme = new_settings.get("theme", "ライト")
            self._apply_theme(theme)

            # サムネイルサイズの変更
            thumbnail_size = new_settings.get("thumbnail_size", 160)
            self._update_thumbnail_sizes(thumbnail_size)

        except Exception as e:
            self.logger.error(f"Failed to apply settings changes: {e}")

    def _apply_theme(self, theme_name: str) -> None:
        """テーマを適用（統合テーママネージャーを使用）"""
        try:
            # 統合テーママネージャーを使用してテーマを適用
            success = self.theme_manager.set_theme(theme_name)

            if success:
                # 個別ウィジェットにもテーマを適用
                self._apply_theme_to_widgets()

                self.logger.info(f"Applied theme: {theme_name}")
            else:
                self.logger.error(f"Failed to set theme: {theme_name}")

        except Exception as e:
            self.logger.error(f"Failed to apply theme: {e}")

    def _apply_theme_to_widgets(self) -> None:
        """個別ウィジェットにテーマを強制適用"""
        try:
            # メインウィンドウとその子ウィジェットすべてにテーマを適用
            self.theme_manager.apply_theme_to_widget(self)

            # 重要なウィジェット群に個別適用
            widgets_to_theme = [
                self.ui.centralwidget,
                self.ui.scrollAreaInputs,
                self.ui.scrollAreaWidgetInputs,
                self.ui.scrollAreaOutput,
                self.ui.scrollAreaWidgetOutput,
                self.ui.groupBoxPDF1,
                self.ui.groupBoxPDF2,
                self.ui.groupBoxOutput,
                self.ui.scrollAreaPDF1,
                self.ui.scrollAreaWidgetPDF1,
                self.ui.scrollAreaPDF2,
                self.ui.scrollAreaWidgetPDF2,
            ]

            for widget in widgets_to_theme:
                if widget:
                    self.theme_manager.apply_theme_to_widget(widget)

            # 出力エリアのページウィジェットにもテーマを適用
            if hasattr(self, "output_area") and self.output_area:
                self.theme_manager.apply_theme_to_widget(self.output_area)

            # 入力エリアのページウィジェットにもテーマを適用
            for widgets_list in self.thumbnail_widgets.values():
                for widget in widgets_list:
                    self.theme_manager.apply_theme_to_widget(widget)

        except Exception as e:
            self.logger.error(f"Failed to apply theme to individual widgets: {e}")

    def _update_thumbnail_sizes(self, size: int) -> None:
        """サムネイルサイズを更新"""
        try:
            # 既存のサムネイルを削除して再生成
            self._regenerate_thumbnails_with_new_size(size)

        except Exception as e:
            self.logger.error(f"Failed to update thumbnail sizes: {e}")

    def _regenerate_thumbnails_with_new_size(self, size: int) -> None:
        """新しいサイズでサムネイルを再生成"""
        try:
            # サムネイルサイズを計算（4:3比率）
            thumbnail_size = (size, int(size * 1.375))

            # 既存のサムネイルファイルを削除
            self._clear_existing_thumbnails()

            # 各サムネイルウィジェットのページ情報に対してサムネイルを再生成
            for _file_path, widgets_list in self.thumbnail_widgets.items():
                for widget in widgets_list:
                    if hasattr(widget, "page_info"):
                        page_info = widget.page_info

                        # 既存のサムネイルパスをクリア
                        page_info.thumbnail_path = None

                        # 新しいサイズでサムネイルを生成
                        try:
                            thumbnail_path = self.pdf_operations.generate_thumbnail(page_info, thumbnail_size)
                            page_info.thumbnail_path = thumbnail_path

                            # サムネイルウィジェットを更新
                            self._update_thumbnail_widget(page_info, size)

                        except Exception as e:
                            self.logger.error(f"Failed to regenerate thumbnail for {page_info}: {e}")

            # レイアウトを更新（水平方向の再整列）
            self._update_layouts_for_new_size(size)

            self.logger.info(f"Thumbnails regenerated with size {size}px")

        except Exception as e:
            self.logger.error(f"Failed to regenerate thumbnails: {e}")

    def _clear_existing_thumbnails(self) -> None:
        """既存のサムネイルファイルを削除"""
        try:
            temp_dir = self.pdf_operations.temp_dir
            if temp_dir and os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    if filename.startswith("thumb_") and filename.endswith(".png"):
                        file_path = os.path.join(temp_dir, filename)
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            self.logger.warning(f"Failed to remove thumbnail file {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to clear existing thumbnails: {e}")

    def _update_thumbnail_widget(self, page_info: PDFPageInfo, size: int) -> None:
        """サムネイルウィジェットを更新"""
        try:
            # 該当するサムネイルウィジェットを検索して更新
            for widgets_list in self.thumbnail_widgets.values():
                for widget in widgets_list:
                    if (
                        hasattr(widget, "page_info")
                        and widget.page_info.source_file == page_info.source_file
                        and widget.page_info.page_number == page_info.page_number
                    ):
                        # ウィジェットサイズを更新
                        widget.setFixedSize(size, int(size * 1.375))

                        # サムネイル画像を再読み込み
                        if page_info.thumbnail_path and os.path.exists(page_info.thumbnail_path):
                            widget.thumbnail_path = page_info.thumbnail_path
                            widget._load_thumbnail()  # 既存の_load_thumbnailメソッドを呼び出し
                        break

        except Exception as e:
            self.logger.error(f"Failed to update thumbnail widget: {e}")

    def _update_layouts_for_new_size(self, size: int) -> None:
        """新しいサムネイルサイズに合わせてレイアウトを更新"""
        try:
            # 出力エリアのレイアウト更新
            if hasattr(self, "output_area") and hasattr(self.output_area, "update_thumbnail_sizes"):
                self.output_area.update_thumbnail_sizes(size)

            # 上部パネルの各PDFエリアのレイアウト更新
            if hasattr(self.ui, "scrollAreaPDF1"):
                self._update_input_area_layout(self.ui.scrollAreaPDF1, size)
            if hasattr(self.ui, "scrollAreaPDF2"):
                self._update_input_area_layout(self.ui.scrollAreaPDF2, size)

            # 動的に作成されたグループボックスのレイアウト更新
            for widgets_list in self.thumbnail_widgets.values():
                if widgets_list:
                    # グループボックス内のレイアウトを強制更新
                    parent_widget = widgets_list[0].parent()
                    if parent_widget:
                        self._force_layout_update(parent_widget)

        except Exception as e:
            self.logger.error(f"Failed to update layouts for new size: {e}")

    def _update_input_area_layout(self, scroll_area: Any, size: int) -> None:
        """入力エリアのレイアウトを更新"""
        try:
            if hasattr(scroll_area, "widget"):
                widget = scroll_area.widget()
                if widget and hasattr(widget, "layout"):
                    layout = widget.layout()
                    if layout:
                        # レイアウトの再計算を強制
                        widget.updateGeometry()
                        layout.update()
        except Exception as e:
            self.logger.warning(f"Failed to update input area layout: {e}")

    def _force_layout_update(self, widget: Any) -> None:
        """ウィジェットのレイアウト更新を強制"""
        try:
            if widget and hasattr(widget, "layout"):
                layout = widget.layout()
                if layout:
                    # レイアウトを無効化して再計算を強制
                    layout.invalidate()
                    layout.update()
                    widget.updateGeometry()
        except Exception as e:
            self.logger.warning(f"Failed to force layout update: {e}")

    def _load_window_settings(self) -> None:
        """ウィンドウ設定を読み込み"""
        try:
            width = self.settings_manager.get("window_width", 1200)
            height = self.settings_manager.get("window_height", 800)
            x = self.settings_manager.get("window_x", 100)
            y = self.settings_manager.get("window_y", 100)
            maximized = self.settings_manager.get("window_maximized", False)

            self.resize(width, height)
            self.move(x, y)

            if maximized:
                self.showMaximized()

        except Exception as e:
            self.logger.error(f"Failed to load window settings: {e}")

    def _save_window_settings(self) -> None:
        """ウィンドウ設定を保存"""
        try:
            if self.isMaximized():
                self.settings_manager.set("window_maximized", True)
            else:
                self.settings_manager.set("window_maximized", False)
                self.settings_manager.set("window_width", self.width())
                self.settings_manager.set("window_height", self.height())
                self.settings_manager.set("window_x", self.x())
                self.settings_manager.set("window_y", self.y())

            self.settings_manager.save_settings()

        except Exception as e:
            self.logger.error(f"Failed to save window settings: {e}")

    def dragEnterEvent(self, event: QDragEnterEvent | None) -> None:
        if event is None:
            return
        """ドラッグエンター時の処理"""
        try:
            self.logger.info("=== dragEnterEvent called ===")

            # mimeDataがNoneでないかチェック
            mime_data = event.mimeData()
            if mime_data is None:
                self.logger.error("mimeData is None")
                event.ignore()
                return

            self.logger.info(f"mimeData available: {mime_data}")
            self.logger.info(f"Has URLs: {mime_data.hasUrls()}")
            self.logger.info(f"Formats: {mime_data.formats()}")

            if mime_data.hasUrls():
                # PDFファイルがあるかチェック
                pdf_files = []
                urls = mime_data.urls()
                self.logger.info(f"Number of URLs: {len(urls)}")

                for i, url in enumerate(urls):
                    self.logger.info(f"URL {i}: {url.toString()}")
                    self.logger.info(f"  isLocalFile: {url.isLocalFile()}")
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        self.logger.info(f"  Local file path: {file_path}")
                        self.logger.info(f"  Is PDF: {file_path.lower().endswith('.pdf')}")
                        if file_path.lower().endswith(".pdf"):
                            pdf_files.append(file_path)

                if pdf_files:
                    event.acceptProposedAction()
                    self.logger.info(f"ACCEPTING drop of {len(pdf_files)} PDF files")
                    return
                else:
                    self.logger.warning("No PDF files in drop, REJECTING")
            else:
                self.logger.warning("No URLs in mimeData, REJECTING")

            event.ignore()
        except Exception as e:
            self.logger.error(f"Error in dragEnterEvent: {e}")
            event.ignore()

    def dropEvent(self, event: QDropEvent | None) -> None:
        if event is None:
            return
        """ドロップ時の処理"""
        try:
            self.logger.info("=== dropEvent called ===")

            # mimeDataがNoneでないかチェック
            mime_data = event.mimeData()
            if mime_data is None:
                self.logger.error("mimeData is None in dropEvent")
                event.ignore()
                return

            files = []
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(".pdf"):
                        files.append(file_path)

            if files:
                self.logger.info(f"Successfully dropping {len(files)} PDF files: {[Path(f).name for f in files]}")
                self.load_pdf_files(files)
                event.acceptProposedAction()
            else:
                self.logger.warning("No valid PDF files in drop")
                event.ignore()
        except Exception as e:
            self.logger.error(f"Error in dropEvent: {e}")
            event.ignore()

    def closeEvent(self, event: Any) -> None:
        """ウィンドウクローズ時の処理"""
        try:
            # 確認ダイアログ表示（設定で有効な場合）
            if self.settings_manager.get("confirm_exit", True):
                reply = QMessageBox.question(
                    self,
                    "終了確認",
                    "アプリケーションを終了しますか？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    event.ignore()
                    return

            # ウィンドウ設定を保存
            if self.settings_manager.get("remember_window", True):
                self._save_window_settings()

            # PDFオペレーションのクリーンアップ
            self.pdf_operations.cleanup()

            event.accept()

        except Exception as e:
            self.logger.error(f"Error during application close: {e}")
            event.accept()  # エラーがあっても終了

    def open_batch_processor(self) -> None:
        """バッチ処理ダイアログを開く"""
        try:
            dialog = BatchProcessorDialog(self)
            dialog.exec()

        except Exception as e:
            self.logger.error(f"Failed to open batch processor: {e}")
            QMessageBox.warning(self, "エラー", f"バッチ処理ダイアログの表示に失敗しました: {e}")

    def open_theme_manager(self) -> None:
        """統合テーママネージャーのテーマ設定ダイアログを開く"""
        try:
            from PyQt6.QtWidgets import (
                QComboBox,
                QDialog,
                QDialogButtonBox,
                QHBoxLayout,
                QLabel,
                QVBoxLayout,
            )

            dialog = QDialog(self)
            dialog.setWindowTitle("テーマ設定")
            dialog.setModal(True)
            dialog.resize(450, 250)

            layout = QVBoxLayout(dialog)

            # 説明ラベル
            info_label = QLabel("テーマを選択してください。変更は即座に反映されます：")
            layout.addWidget(info_label)

            # テーマ選択
            theme_layout = QHBoxLayout()
            theme_label = QLabel("テーマ:")
            theme_combo = QComboBox()

            # 利用可能なテーマを取得
            themes = self.theme_manager.get_available_themes()
            current_theme = self.theme_manager.get_current_theme()
            original_theme = current_theme  # 元のテーマを保存

            for theme_name, theme_config in themes.items():
                if isinstance(theme_config, dict):
                    display_name = theme_config.get("display_name", theme_name)
                else:
                    display_name = str(theme_config)
                theme_combo.addItem(f"{display_name} ({theme_name})", theme_name)

                # 現在のテーマを選択
                if theme_name == current_theme:
                    theme_combo.setCurrentIndex(theme_combo.count() - 1)

            # テーマ変更時のリアルタイムプレビュー
            def apply_preview_theme():
                selected_theme = theme_combo.currentData()
                if selected_theme:
                    # プレビュー用の一時的なテーマ変更
                    self.theme_manager.preview_theme(selected_theme)
                    self._apply_theme_to_widgets()

            theme_combo.currentTextChanged.connect(apply_preview_theme)

            theme_layout.addWidget(theme_label)
            theme_layout.addWidget(theme_combo)
            layout.addLayout(theme_layout)

            # プレビュー情報
            preview_label = QLabel("プレビュー: テーマを選択すると即座に適用されます")
            preview_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(preview_label)

            # ボタン
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

            def accept_changes():
                # 選択されたテーマで確定保存
                selected_theme = theme_combo.currentData()
                if selected_theme:
                    self.theme_manager.set_theme(selected_theme)
                    self.logger.info(f"Theme saved: {selected_theme}")
                dialog.accept()

            def reject_changes():
                # 元のテーマに戻す
                self.theme_manager.set_theme(original_theme)
                self.logger.info(f"Theme reverted to: {original_theme}")
                dialog.reject()

            button_box.accepted.connect(accept_changes)
            button_box.rejected.connect(reject_changes)
            layout.addWidget(button_box)

            # ダイアログ実行
            dialog.exec()

        except Exception as e:
            self.logger.error(f"Failed to open theme manager: {e}")
            QMessageBox.warning(self, "エラー", f"テーマ設定ダイアログの表示に失敗しました: {e}")

    def _force_theme_reapply(self) -> None:
        """ウィンドウ表示後にテーマを強制的に再適用"""
        try:
            current_theme = self.theme_manager.get_current_theme()
            if current_theme:
                self.theme_manager.apply_theme_to_application()
                self._apply_theme_to_widgets()
                self.logger.debug(f"Force reapplied theme: {current_theme}")
        except Exception as e:
            self.logger.error(f"Failed to force reapply theme: {e}")


def create_main_window(pdf_files: list[str] | None = None, log_level: str = "INFO") -> MainWindow:
    """メインウィンドウを作成"""
    return MainWindow(pdf_files, log_level)
