import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget,
                             QColorDialog, QMenuBar, QAction, QMenu, QToolBar,
                             QScrollBar, QFileDialog, QLabel, QVBoxLayout,
                             QSpinBox)
from PyQt5.QtCore import (Qt, pyqtSignal, QPoint, QSize)
from PyQt5.QtGui import (QImage, QIcon, QColor, QPixmap, QKeySequence,
                         QPainter, QPainterPath, QPen, QTabletEvent)


class CanvasUi(QWidget):
    def __init__(self):  # инициализация объекта
        super().__init__()
        self.init_UI()

    def init_UI(self):  # UI окна
        self.setWindowIcon(QIcon('icon.png'))
        self.setWindowTitle('Camena')
        self.setGeometry(330, 250, 1244, 700)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(palette)

        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(1)

        self.showMaximized()

    def make_menus(self):  # выносим создание тулбара в отдельную функцию
        self.new_action = QAction(QIcon('icons/create.png'), 'Новый', self)
        self.new_action.setShortcut(QKeySequence('Ctrl+N'))
        self.open_action = QAction(QIcon('icons/open.png'), 'Открыть', self)
        self.open_action.setShortcut(QKeySequence('Ctrl+O'))
        self.save_action = QAction(QIcon('icons/save.png'), 'Сохранить', self)
        self.save_action.setShortcut(QKeySequence('Ctrl+S'))
        self.quicksave_action = QAction(QIcon('icons/quicksave.png'),
                                        'Быстрое сохранение', self)
        self.quicksave_action.setShortcut(QKeySequence('Ctrl+Shift+S'))
        self.open_color_settings = QAction(QIcon('icons/palette.png'),
                                           'Изменить цвет', self)
        self.open_color_settings.setShortcut(QKeySequence('Ctrl+C'))
        self.eraser_mode = QAction(QIcon('icons/eraser.png'), 'Стерка', self)
        self.eraser_mode.setShortcut(QKeySequence('Ctrl+E'))
        self.brush_mode = QAction(QIcon('icons/pencil.png'), 'Кисть', self)
        self.toolbar = self.addToolBar('Скрыть/показать панель')
        self.change_size_action = QAction(QIcon('icons/size.png'),
                                          'Изменить размер кисти', self)
        self.change_background_action = QAction(QIcon('icons/background.png'),
                                                'Изменить цвет фона', self)
        self.change_toolbar_color_action = QAction(QIcon('icons/settings.png'),
                                                   'Изменить цвет панели',
                                                   self)

        self.toolbar.addAction(self.new_action)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addAction(self.save_action)
        self.toolbar.addAction(self.quicksave_action)
        self.toolbar.addAction(self.eraser_mode)
        self.toolbar.addAction(self.brush_mode)
        self.toolbar.addAction(self.open_color_settings)
        self.toolbar.addAction(self.change_background_action)
        self.toolbar.addAction(self.change_toolbar_color_action)
        self.toolbar.addWidget(self.spinbox)
        self.toolbar.setIconSize(QSize(32, 32))

        self.show()


class Canvas(QMainWindow, CanvasUi):  # наследуем методы от QMainWindow, \
                                      # a внешний вид от CanvasUi
    color, bg_color, size, drawing = Qt.black, Qt.white, 1, False  # параметры
    drawing_color = color  # назначаем цвет, который рисует кисть, черным
    # для удобства определим форматы
    FORMATS = \
        "JPEG (*.jpg *.jpeg);;PNG (*.png);;All files (*.*)"
    canvas = QImage(1920, 1080, QImage.Format_RGB32)
    canvas.fill(Qt.white)

    def __init__(self):
        super().__init__()
        Canvas.init_UI(self)
        CanvasUi.make_menus(self)
        # назначаем функции, ответственные за действия
        self.new_action.triggered.connect(self.clear)
        self.eraser_mode.triggered.connect(self.change_mode)
        self.brush_mode.triggered.connect(self.change_mode)
        self.change_background_action.triggered.connect(
            self.change_background_color)
        self.change_toolbar_color_action.triggered.connect(
            self.change_toolbar_color)
        self.open_color_settings.triggered.connect(self.change_color)
        self.save_action.triggered.connect(self.save_file)
        self.open_action.triggered.connect(self.open_file)
        self.quicksave_action.triggered.connect(self.save_file)
        self.spinbox.valueChanged.connect(self.change_size)

    def change_size(self):  # меняем размер кисти на значение spinbox
        self.size = self.spinbox.value()

    def change_mode(self):  # смена режима в зависимости от отправителя сигнала
        if self.sender().text() == 'Стерка':
            self.drawing_color = self.bg_color
        else:
            self.drawing_color = self.color

    def change_background_color(self):  # заливка холста выбранным цветом
        chosen_color = QColorDialog.getColor()
        self.bg_color = chosen_color
        self.canvas.fill(chosen_color)
        self.update()

    def change_toolbar_color(self):  # смена цвета фона программы и тулбара
        chosen_color = QColorDialog.getColor()
        palette = self.palette()
        palette.setColor(self.backgroundRole(), chosen_color)
        self.setPalette(palette)

    def mousePressEvent(self, event):  # при нажатии на ЛКМ начинает рисовать
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.drawing = True

    def mouseMoveEvent(self, event):  # проверка на зажатую ЛКМ
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            self.draw(event.pos())

    def mouseReleaseEvent(self, event):  # отпускаем ЛКМ
        if event.button() == Qt.LeftButton:
            self.draw(event.pos())

    def paintEvent(self, event):  # автовызов функции для рисования
        painter = QPainter(self)
        painter.drawImage(0, 0, self.canvas)

    def draw(self, end_point):  # само рисование
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(self.drawing_color, self.size))
        painter.drawLine(self.lastPoint, end_point)
        self.update()
        self.lastPoint = QPoint(end_point)

    def change_color(self):  # смена цвета кисти
        self.color = QColorDialog.getColor()
        self.drawing_color = self.color

    def clear(self):  # холст заливается белым, цвет стерки тоже белый
        self.bg_color = Qt.white
        self.drawing_color = self.color
        self.canvas.fill(Qt.white)
        self.update()

    def save_file(self):  # сохранение и быстрое сохранение
        if self.sender().text() == 'Быстрое сохранение':
            file_name = 'image.jpg'
        else:
            file_name = QFileDialog.getSaveFileName(self, "Открыть файл", "",
                                                    self.FORMATS)[0]
        self.canvas.save(file_name)

    def open_file(self):  # открытие файла
        file_name = QFileDialog.getOpenFileName(self, "Открыть файл", "",
                                                self.FORMATS)[0]
        if file_name:
            self.canvas = QImage(file_name)
            self.canvas.scaled(QSize(1920, 1080), Qt.KeepAspectRatio)
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    can = Canvas()
    can.show()
    sys.exit(app.exec_())
