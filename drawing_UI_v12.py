import os
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QMenuBar, QColorDialog, QFileDialog, QDockWidget, QListWidget, QVBoxLayout, QPushButton, QInputDialog

class PaintWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.drawing = False
        self.last_point = QPoint()

        self.brush_color = Qt.black
        self.brush_size = 10

        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("File")
        brush_menu = main_menu.addMenu("Brush")

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.save)

        clear_action = QAction("Clear", self)
        clear_action.setShortcut("Ctrl+C")
        file_menu.addAction(clear_action)
        clear_action.triggered.connect(self.clear)

        color_action = QAction("Color", self)
        brush_menu.addAction(color_action)
        color_action.triggered.connect(self.choose_color)

        size_menu = QMenu("Size", self)
        brush_menu.addMenu(size_menu)

        small_action = QAction("Small", self)
        size_menu.addAction(small_action)
        small_action.triggered.connect(lambda: self.set_brush_size(5))

        medium_action = QAction("Medium", self)
        size_menu.addAction(medium_action)
        medium_action.triggered.connect(lambda: self.set_brush_size(10))

        large_action = QAction("Large", self)
        size_menu.addAction(large_action)
        large_action.triggered.connect(lambda: self.set_brush_size(20))

        # Create layer toolbox
        self.layer_list = QListWidget()
        
        add_layer_button = QPushButton("Add Layer")
        add_layer_button.clicked.connect(self.add_layer)

        delete_layer_button = QPushButton("Delete Layer")
        delete_layer_button.clicked.connect(self.delete_layer)

        move_layer_up_button = QPushButton("Move Layer Up")
        move_layer_up_button.clicked.connect(self.move_layer_up)

        move_layer_down_button = QPushButton("Move Layer Down")
        move_layer_down_button.clicked.connect(self.move_layer_down)

layer_toolbox=QDockWidget("Layers")
layer_toolbox.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

layer_layout=QVBoxLayout()
layer_layout.addWidget(self.layer_list)
layer_layout.addWidget(add_layer_button)
layer_layout.addWidget(delete_layer_button)
layer_layout.addWidget(move_layer_up_button)
layer_layout.addWidget(move_layer_down_button)

layer_toolbox.setLayout(layer_layout)

self.addDockWidget(Qt.RightDockWidgetArea, layer_toolbox)

    def save(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        
        if file_path == "":
            return
          
        self.image.save(file_path)

    def clear(self):
      self.image.fill(Qt.white)
      self.update()

    def choose_color(self):
      color = QColorDialog.getColor()
      
      if color.isValid():
          self.brush_color = color

    def set_brush_size(self, size):
      self.brush_size = size

    def mousePressEvent(self, event):
      if event.button() == Qt.LeftButton:
          self.drawing = True
          self.last_point = event.pos()

    def mouseMoveEvent(self, event):
      if event.buttons() and Qt.LeftButton and self.drawing:
          painter = QPainter(self.image)
          painter.setPen(QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap))
          painter.drawLine(self.last_point, event.pos())
          self.last_point = event.pos()
          self.update()

    def mouseReleaseEvent(self,event):
      if event.button()==Qt.LeftButton:
          self.drawing=False

    def paintEvent(self,event):
      canvas_painter=QPainter(self)
      canvas_painter.drawImage(self.rect(),self.image,self.image.rect())

    def resizeEvent(self,event):
      new_image=QImage(event.size(),QImage.Format_RGB32)
      new_image.fill(Qt.white)

      painter=QPainter(new_image)
      painter.drawImage(QPoint(0,0),self.image)

      self.image=new_image

    # Layer toolbox methods
    def add_layer(self):
      layer_name, ok = QInputDialog.getText(self, "Add Layer", "Enter layer name:")
      if ok and layer_name:
        self.layer_list.addItem(layer_name)

    def delete_layer(self):
      current_row = self.layer_list.currentRow()
      if current_row >= 0:
        self.layer_list.takeItem(current_row)

    def move_layer_up(self):
      current_row = self.layer_list.currentRow()
      if current_row > 0:
        current_item = self.layer_list.takeItem(current_row)
        self.layer_list.insertItem(current_row - 1, current_item)
        self.layer_list.setCurrentRow(current_row - 1)

    def move_layer_down(self):
      current_row = self.layer_list.currentRow()
      if current_row >= 0 and current_row < self.layer_list.count() - 1:
        current_item = self.layer_list.takeItem(current_row)
        self.layer_list.insertItem(current_row + 1, current_item)
        self.layer_list.setCurrentRow(current_row + 1)

app=QApplication(sys.argv)
window=PaintWindow()
window.show()
app.exec_()
