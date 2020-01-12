#!/usr/bin/python3
# -*- coding: utf-8 -*-

from api.cv2_api import Image

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog
from PyQt5.QtWidgets import QMessageBox


def swish_activation(x):
    return (K.sigmoid(x) * x)

class QImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scaleFactor = 0.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)

        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Image Editor")
        self.resize(800, 600)

    def getImage(self, filename=None):
        if filename:
            self.cv_api = Image(filename)

        image = self.cv_api.getData()
        image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        return image

    def greyFormat(self):
        self.cv_api.grayScale()
        image = self.cv_api.getData()
        image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)#.rgbSwapped()

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0

        self.colorAct.setChecked(False)
        self.greyAct.setChecked(True)

    def coloredFormat(self):
        self.cv_api.colored()
        image = self.cv_api.getData()
        image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0
        
        self.colorAct.setChecked(True)
        self.greyAct.setChecked(False)

    def rotateImage(self, direction):
        if direction == 'anti':
            self.cv_api.rotate(10)
        elif direction == "clock":
            self.cv_api.rotate(-10)

        image = self.cv_api.getData()
        if not self.cv_api.flag_grey:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        else:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0


    def open(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
                                                  'Images (*.png *.jpeg *.jpg *.bmp)', options=options)
        self.link = fileName

        if fileName:
            image = self.getImage(fileName)
            # image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return


            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.scrollArea.setVisible(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            edit_menu_list = [self.colorMenu, self.rotateMenu, self.perspectiveMenu, self.borderMenu, self.scaleMenu]
            for menu in edit_menu_list:
                menu.setEnabled(True)


            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()


    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                          "<p>The <b>Image Viewer</b> example shows how to combine "
                          "QLabel and QScrollArea to display an image. QLabel is "
                          "typically used for displaying text, but it can also display "
                          "an image. QScrollArea provides a scrolling view around "
                          "another widget. If the child widget exceeds the size of the "
                          "frame, QScrollArea automatically provides scroll bars.</p>"
                          "<p>The example demonstrates how QLabel's ability to scale "
                          "its contents (QLabel.scaledContents), and QScrollArea's "
                          "ability to automatically resize its contents "
                          "(QScrollArea.widgetResizable), can be used to implement "
                          "zooming and scaling features.</p>"
                          "<p>In addition the example shows how to use QPainter to "
                          "print an image.</p>")

    def createActions(self):
        self.openAct = QAction("&Open", self, shortcut="Ctrl+O", triggered=self.open)
        self.saveAct = QAction("&Save", self, shortcut='Ctrl+s', enabled=False)
        self.discardAct = QAction("&Discard", self, shortcut='Ctrl+d', enabled=False)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+q", triggered=self.close)

        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)
        
        self.greyAct = QAction("GreyScale", self, checkable=True, triggered=self.greyFormat)
        self.colorAct = QAction("Colored", self, checkable=True, checked=True, triggered=self.coloredFormat)
        self.clockAct = QAction("Clockwise 10 Degree", self, triggered=lambda:self.rotateImage("clock"))
        self.antiClockAct = QAction("Anti-Clockwise 10 Degree", self, triggered=lambda:self.rotateImage("anti"))
        self.verticalAct = QAction("Vertical", self, checkable=True, checked=True)
        self.horizontalAct = QAction("Horizontal", self, checkable=True, checked=False)
        self.increaseAct = QAction("Increase", self)
        self.decreaseAct = QAction("Decrease", self)
        self.px_10 = QAction("10 px", self, checkable=True, checked=False)
        self.px_20 = QAction("20 px", self, checkable=True, checked=False)
        self.px_50 = QAction("50 px", self, checkable=True, checked=False)
        self.px_100 = QAction("100 px", self, checkable=True, checked=False)
        self.leftAct = QAction("Left", self, checkable=True, checked=False)
        self.rightAct = QAction("Right", self, checkable=True, checked=False)
        self.topAct = QAction("Top", self, checkable=True, checked=False)
        self.buttomAct = QAction("Buttom", self, checkable=True, checked=False)
        self.scaleUpAct = QAction("Scale Up", self)
        self.scaleDownAct = QAction("Scale Down", self)
        

        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.discardAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.editMenu = QMenu("&Edit", self)
        self.colorMenu = QMenu("Color", self.editMenu, enabled=False)
        self.rotateMenu = QMenu("Rotate", self.editMenu, enabled=False)
        self.perspectiveMenu = QMenu("Perspective", self.editMenu, enabled=False)
        self.borderMenu = QMenu("Border", self.editMenu, enabled=False)
        self.scaleMenu = QMenu("Scale", self.editMenu, enabled=False)
        self.editMenu.addMenu(self.colorMenu)
        self.editMenu.addMenu(self.rotateMenu)
        self.editMenu.addMenu(self.perspectiveMenu)
        self.editMenu.addMenu(self.borderMenu)
        self.editMenu.addMenu(self.scaleMenu)
        self.colorMenu.addAction(self.greyAct)
        self.colorMenu.addAction(self.colorAct)
        self.rotateMenu.addAction(self.clockAct)
        self.rotateMenu.addAction(self.antiClockAct)
        self.perspectiveMenu.addAction(self.verticalAct)
        self.perspectiveMenu.addAction(self.horizontalAct)
        self.perspectiveMenu.addSeparator()
        self.perspectiveMenu.addAction(self.increaseAct)
        self.perspectiveMenu.addAction(self.decreaseAct)
        self.sizeMenu = QMenu("Color", self.borderMenu)
        self.sizeMenu.addAction(self.px_10)
        self.sizeMenu.addAction(self.px_20)
        self.sizeMenu.addAction(self.px_50)
        self.sizeMenu.addAction(self.px_100)
        self.borderMenu.addMenu(self.sizeMenu)
        self.borderMenu.addAction(self.leftAct)
        self.borderMenu.addAction(self.rightAct)
        self.borderMenu.addAction(self.topAct)
        self.borderMenu.addAction(self.buttomAct)
        self.scaleMenu.addAction(self.scaleUpAct)
        self.scaleMenu.addAction(self.scaleDownAct)


        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    imageViewer = QImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())