"""
PDF Page Widget Module

ドラッグ&ドロップ対応のページウィジェットと出力エリア管理
"""

import os

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QMimeData, QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QDrag, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QWidget,
)

from ..pdf_operations import PDFPageInfo
from ..utils.logger import get_logger


class PageThumbnailWidget(QLabel):
    """
    ドラッグ&ドロップ対応のページサムネイルウィジェット
    """

    # シグナル定義
    clicked = pyqtSignal(object)  # PDFPageInfo
    double_clicked = pyqtSignal(object)
    right_clicked = pyqtSignal(object)
    rotation_requested = pyqtSignal(object, int)  # PDFPageInfo, angle
    removal_requested = pyqtSignal(object)  # PDFPageInfo

    def __init__(
        self, page_info: PDFPageInfo, thumbnail_path: str, is_output: bool = False, parent: QWidget | None = None
    ):
        super().__init__(parent)

        self.page_info = page_info
        self.thumbnail_path = thumbnail_path
        self.is_output = is_output
        self.logger = get_logger("PageThumbnailWidget")
        self.selected = False

        self._setup_widget()
        self._load_thumbnail()

    def _setup_widget(self):
        """ウィジェットの基本設定"""
        self.setFixedSize(160, 220)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFrameStyle(QFrame.Shape.Box)

        # 出力エリアの場合のみドロップを受け入れ（順序変更用）
        # 入力エリアの場合はドロップを受け入れない（ファイルドロップと競合回避）
        if self.is_output:
            self.setAcceptDrops(True)
        else:
            self.setAcceptDrops(False)

        # ツールチップ設定
        self._setup_tooltip()

        # スタイル設定
        self._update_style()

    def _setup_tooltip(self):
        """ツールチップを設定"""
        try:
            file_name = os.path.basename(self.page_info.source_file)
            tooltip_text = f"""ファイル: {file_name}
ページ: {self.page_info.page_number + 1}
回転: {self.page_info.rotation}°"""
            self.setToolTip(tooltip_text)

        except Exception as e:
            self.logger.error(f"Failed to setup tooltip: {e}")
            self.setToolTip("PDF ページ")

    def _update_style(self):
        """ウィジェットのスタイルを更新"""
        if self.selected:
            border_color = "#0078d4"
            bg_color = "#e6f3ff"
        else:
            border_color = "#cccccc"
            bg_color = "#ffffff"

        self.setStyleSheet(f"""
            QLabel {{
                border: 2px solid {border_color};
                background-color: {bg_color};
                border-radius: 8px;
                margin: 2px;
                padding: 5px;
            }}
            QLabel:hover {{
                border-color: #0078d4;
                background-color: #f0f8ff;
            }}
        """)

    def _load_thumbnail(self):
        """サムネイル画像をロード"""
        try:
            pixmap = QPixmap(self.thumbnail_path)

            # 回転を適用
            if self.page_info.rotation != 0:
                transform = QtGui.QTransform()
                transform.rotate(self.page_info.rotation)
                pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

            # サイズ調整
            scaled_pixmap = pixmap.scaled(
                140, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )

            # ページ番号をオーバーレイ
            painter = QPainter(scaled_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 背景矩形
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 180)))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRoundedRect(5, 5, 30, 20, 3, 3)

            # ページ番号テキスト
            painter.setPen(QtGui.QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(8, 20, str(self.page_info.page_number + 1))

            painter.end()

            self.setPixmap(scaled_pixmap)

        except Exception as e:
            self.logger.error(f"Failed to load thumbnail: {e}")
            self.setText("エラー")

    def set_selected(self, selected: bool):
        """選択状態を設定"""
        self.selected = selected
        self._update_style()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """マウスクリックイベント（複数選択対応）"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 修飾キーに応じた選択処理
            modifiers = event.modifiers()

            if modifiers & Qt.KeyboardModifier.ControlModifier:
                # Ctrlキー押下: 個別選択切り替え
                self.clicked.emit(self.page_info)
                self.set_selected(not self.selected)
            elif modifiers & Qt.KeyboardModifier.ShiftModifier:
                # Shiftキー押下: 範囲選択（親ウィジェットで処理）
                self.clicked.emit(self.page_info)
            else:
                # 通常クリック: 単一選択
                self.clicked.emit(self.page_info)

        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        """マウスダブルクリックイベント"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.page_info)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        """ドラッグ開始"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self._start_drag()

    def _start_drag(self):
        """ドラッグ操作開始"""
        try:
            drag = QDrag(self)
            mimeData = QMimeData()

            # ドラッグデータを設定
            drag_data = f"page:{self.page_info.source_file}:{self.page_info.page_number}:{self.page_info.rotation}"
            mimeData.setText(drag_data)

            # MimeDataを設定してからドラッグ画像を設定
            drag.setMimeData(mimeData)

            # ドラッグ画像を設定
            if self.pixmap() and not self.pixmap().isNull():
                drag_pixmap = self.pixmap().scaled(80, 100, Qt.AspectRatioMode.KeepAspectRatio)
                drag.setPixmap(drag_pixmap)

            # ドラッグ実行
            drop_action = drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)

            # 出力エリアからの移動の場合の処理
            if drop_action == Qt.DropAction.MoveAction and self.is_output:
                # ドラッグ削除機能を無効化 - 並び替え専用に変更
                # 削除は右クリックメニューからのみ実行可能
                self.logger.debug(f"Page {self.page_info.page_number + 1} drag completed - reordering only, no removal")

        except Exception as e:
            self.logger.error(f"Failed to start drag: {e}")

    def _show_context_menu(self, position: QPoint):
        """右クリックコンテキストメニュー表示"""
        menu = QtWidgets.QMenu(self)

        # 出力エリアの場合のみ回転メニューと削除メニューを表示
        # 入力エリアでは原稿ファイルを編集しない原則に従う
        if self.is_output:
            # 回転メニュー
            rotate_menu = menu.addMenu("回転")

            rotate_right = rotate_menu.addAction("右90°回転")
            rotate_right.triggered.connect(lambda: self.rotation_requested.emit(self.page_info, 90))

            rotate_left = rotate_menu.addAction("左90°回転")
            rotate_left.triggered.connect(lambda: self.rotation_requested.emit(self.page_info, -90))

            rotate_180 = rotate_menu.addAction("180°回転")
            rotate_180.triggered.connect(lambda: self.rotation_requested.emit(self.page_info, 180))

            menu.addSeparator()
            remove_action = menu.addAction("出力から削除")
            remove_action.triggered.connect(lambda: self.removal_requested.emit(self.page_info))
        else:
            # 入力エリアでは情報表示のみ
            info_action = menu.addAction(f"ページ {self.page_info.page_number + 1}")
            info_action.setEnabled(False)

        menu.exec(position)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        """ドラッグエンター"""
        # ページ間のドラッグ&ドロップの場合
        if event.mimeData().hasText() and event.mimeData().text().startswith("page:"):
            event.acceptProposedAction()
            return

        # 外部ファイルのドラッグの場合は親ウィンドウに委譲
        if event.mimeData().hasUrls():
            # 親ウィンドウのMainWindowにイベントを伝播させる
            event.ignore()
            return

        # その他の場合は無視
        event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent):
        """ドロップ"""
        # ページ間のドロッグ&ドロップの場合のみ処理
        if event.mimeData().hasText() and event.mimeData().text().startswith("page:"):
            if self.is_output:
                # 出力エリアでの並び替え処理
                event.acceptProposedAction()
                return

        # 外部ファイルのドロップは親ウィンドウに委譲
        event.ignore()


class OutputArea(QWidget):
    """
    出力エリア - ページの並び替えとプレビュー
    """

    # シグナル定義
    page_added = pyqtSignal(object)  # PDFPageInfo
    page_removed = pyqtSignal(object)  # PDFPageInfo
    page_order_changed = pyqtSignal(list)  # List[PDFPageInfo]

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.logger = get_logger("OutputArea")
        self.pages: list[PDFPageInfo] = []
        self.page_widgets: list[PageThumbnailWidget] = []
        self.get_thumbnail_path = None  # メインウィンドウから設定される関数

        self._setup_ui()

    def _setup_ui(self):
        """UI設定"""
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setSpacing(10)
        # ドロップ受け入れ設定（ページドロップのみ、外部ファイルはメインウィンドウで処理）
        self.setAcceptDrops(True)
        self.logger.debug("OutputArea drop acceptance enabled (pages only)")

        # 空の状態メッセージ
        self.empty_label = QLabel("ページをここにドラッグしてください")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setObjectName("outputEmptyLabel")  # テーマ対応のため識別子を設定
        # スタイルはテーマシステムから自動適用されるよう削除
        self.layout.addWidget(self.empty_label, 0, 0)

    def add_page(self, page_info: PDFPageInfo, thumbnail_path: str):
        """ページを追加"""
        self.logger.debug(f"Adding page to output: {page_info}")

        # 空メッセージを非表示
        if self.empty_label.isVisible():
            self.empty_label.hide()

        # ページをリストに追加
        self.pages.append(page_info)

        # ウィジェット作成
        page_widget = PageThumbnailWidget(page_info, thumbnail_path, is_output=True, parent=self)
        page_widget.rotation_requested.connect(self._on_rotation_requested)
        page_widget.removal_requested.connect(self._on_removal_requested)

        self.page_widgets.append(page_widget)

        # レイアウトに配置
        self._update_layout()

        self.page_added.emit(page_info)

    def remove_page(self, page_info: PDFPageInfo):
        """ページを削除"""
        try:
            index = self.pages.index(page_info)
            self.pages.pop(index)

            # ウィジェットを削除
            widget = self.page_widgets.pop(index)
            widget.deleteLater()

            # レイアウト更新
            self._update_layout()

            # 空の場合はメッセージ表示
            if not self.pages:
                self.empty_label.show()

            self.page_removed.emit(page_info)

        except ValueError:
            self.logger.warning(f"Page not found for removal: {page_info}")

    def _update_layout(self):
        """レイアウトを更新"""
        # 既存のウィジェットをレイアウトから削除
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item and item.widget() != self.empty_label:
                self.layout.removeItem(item)

        # 現在のサムネイルサイズを取得
        current_thumbnail_size = self._get_current_thumbnail_size()

        # ウィジェットを再配置（マージンを考慮した幅計算）
        widget_width = current_thumbnail_size + 20  # マージン考慮
        cols = max(1, self.width() // widget_width)
        for i, widget in enumerate(self.page_widgets):
            row = i // cols
            col = i % cols
            self.layout.addWidget(widget, row, col)

    def _get_current_thumbnail_size(self):
        """現在のサムネイルサイズを取得"""
        if self.page_widgets:
            # 最初のウィジェットからサイズを取得
            first_widget = self.page_widgets[0]
            return first_widget.width()
        return 160  # デフォルトサイズ

    def update_thumbnail_sizes(self, size: int):
        """サムネイルサイズを更新（外部から呼び出し可能）"""
        # 各ウィジェットのサイズを更新
        for widget in self.page_widgets:
            widget.setFixedSize(size, int(size * 1.375))

        # レイアウトを再計算
        self._update_layout()

    def _on_rotation_requested(self, page_info: PDFPageInfo, angle: int):
        """回転要求処理"""
        # 現在の回転角度に追加
        new_rotation = (page_info.rotation + angle) % 360
        page_info.rotation = new_rotation

        # サムネイルを再生成（簡易版：ウィジェットを再読み込み）
        try:
            index = self.pages.index(page_info)
            widget = self.page_widgets[index]
            widget._load_thumbnail()  # サムネイル再読み込み
        except ValueError:
            pass

    def _on_removal_requested(self, page_info: PDFPageInfo):
        """削除要求処理"""
        self.remove_page(page_info)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        """ドラッグエンター"""
        # ページ間のドラッグ&ドロップの場合
        if event.mimeData().hasText() and event.mimeData().text().startswith("page:"):
            event.acceptProposedAction()
            return

        # 外部ファイルのドラッグの場合は親ウィンドウに委譲
        if event.mimeData().hasUrls():
            # 親ウィンドウのMainWindowにイベントを伝播させる
            event.ignore()
            return

        # その他の場合は無視
        event.ignore()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        """ドラッグ移動"""
        event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent):
        """ドロップ"""
        # ページ間のドラッグ&ドロップの場合のみ処理
        if event.mimeData().hasText():
            drag_data = event.mimeData().text()
            if drag_data.startswith("page:"):
                try:
                    # ドラッグデータを解析
                    parts = drag_data.split(":")
                    source_file = parts[1]
                    page_number = int(parts[2])
                    rotation = int(parts[3]) if len(parts) > 3 else 0

                    # ページ情報を作成
                    page_info = PDFPageInfo(source_file, page_number, rotation)

                    # ドロップ位置を計算
                    drop_position = event.position().toPoint()
                    insert_index = self._calculate_insert_position(drop_position)

                    # 既存ページの並び替えかどうかを確認
                    existing_index = -1
                    for i, existing_page in enumerate(self.pages):
                        if (
                            existing_page.source_file == page_info.source_file
                            and existing_page.page_number == page_info.page_number
                            and existing_page.rotation == page_info.rotation
                        ):
                            existing_index = i
                            break

                    if existing_index >= 0:
                        # 既存ページの並び替え
                        self.logger.debug(f"Reordering page from index {existing_index} to {insert_index}")

                        # インデックス調整（移動後の位置を正確に計算）
                        if existing_index < insert_index:
                            insert_index -= 1

                        # 同じ位置への移動は無視
                        if existing_index == insert_index:
                            event.acceptProposedAction()
                            return

                        # ページとウィジェットを移動
                        moved_page = self.pages.pop(existing_index)
                        moved_widget = self.page_widgets.pop(existing_index)

                        self.pages.insert(insert_index, moved_page)
                        self.page_widgets.insert(insert_index, moved_widget)

                        # レイアウト更新
                        self._update_layout()

                        # ページ順序変更シグナルを発行
                        self.page_order_changed.emit(self.pages)

                        self.logger.info(f"Page reordered: {page_info} moved to position {insert_index + 1}")

                    else:
                        # 新しいページの挿入
                        # メインウィンドウからサムネイルパスを取得
                        thumbnail_path = None
                        if self.get_thumbnail_path:
                            thumbnail_path = self.get_thumbnail_path(page_info)

                        # サムネイルパスが取得できない場合のフォールバック
                        if not thumbnail_path:
                            import os
                            import tempfile
                            from pathlib import Path

                            thumbnail_filename = f"thumb_{Path(source_file).stem}_p{page_number + 1}.png"
                            # 一時ディレクトリを検索
                            for temp_dir in [tempfile.gettempdir()]:
                                potential_path = os.path.join(temp_dir, thumbnail_filename)
                                if os.path.exists(potential_path):
                                    thumbnail_path = potential_path
                                    break

                            # まだ見つからない場合は警告
                            if not thumbnail_path:
                                self.logger.warning(f"Thumbnail not found for {page_info}")
                                thumbnail_path = ""  # 空のパスで作成

                        # ページを挿入
                        self.insert_page(insert_index, page_info, thumbnail_path)

                    event.acceptProposedAction()
                    return

                except Exception as e:
                    self.logger.error(f"Failed to process drop: {e}")
                    event.ignore()
                    return

        # 外部ファイルのドロップは親ウィンドウに委譲
        event.ignore()

    def _calculate_insert_position(self, drop_position: QPoint) -> int:
        """ドロップ位置から挿入インデックスを計算"""
        if not self.page_widgets:
            return 0

        # ドロップ位置に最も近いウィジェットを探す
        min_distance = float("inf")
        closest_index = len(self.page_widgets)

        for i, widget in enumerate(self.page_widgets):
            widget_center = widget.geometry().center()
            distance = (
                (drop_position.x() - widget_center.x()) ** 2 + (drop_position.y() - widget_center.y()) ** 2
            ) ** 0.5

            if distance < min_distance:
                min_distance = distance
                closest_index = i

                # ドロップ位置がウィジェットの右半分なら次の位置に挿入
                if drop_position.x() > widget_center.x():
                    closest_index = i + 1

        return min(closest_index, len(self.page_widgets))

    def insert_page(self, index: int, page_info: PDFPageInfo, thumbnail_path: str):
        """指定位置にページを挿入"""
        self.logger.debug(f"Inserting page at index {index}: {page_info}")

        # 空メッセージを非表示
        if self.empty_label.isVisible():
            self.empty_label.hide()

        # 重複チェック
        for existing_page in self.pages:
            if (
                existing_page.source_file == page_info.source_file
                and existing_page.page_number == page_info.page_number
            ):
                self.logger.info(f"Page already exists in output: {page_info}")
                return

        # リストに挿入
        self.pages.insert(index, page_info)

        # ウィジェット作成
        page_widget = PageThumbnailWidget(page_info, thumbnail_path, is_output=True, parent=self)
        page_widget.rotation_requested.connect(self._on_rotation_requested)
        page_widget.removal_requested.connect(self._on_removal_requested)

        self.page_widgets.insert(index, page_widget)

        # レイアウト更新
        self._update_layout()

        # ページ順序変更シグナルを発行
        self.page_order_changed.emit(self.pages)
        self.page_added.emit(page_info)

    def resizeEvent(self, event):
        """リサイズイベント"""
        super().resizeEvent(event)
        self._update_layout()

    def get_pages(self) -> list[PDFPageInfo]:
        """現在の出力ページリストを取得"""
        return self.pages.copy()

    def clear(self):
        """すべてのページをクリア"""
        for widget in self.page_widgets:
            widget.deleteLater()

        self.pages.clear()
        self.page_widgets.clear()
        self.empty_label.show()
