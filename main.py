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
        self.perspective = 0
        self.save_path = None

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
        self.cv_api.setFormatGrey()
        image = self.cv_api.getData()
        image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)#.rgbSwapped()

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0

        self.colorAct.setChecked(False)
        self.greyAct.setChecked(True)

    def coloredFormat(self):
        self.cv_api.setFormatColor()
        image = self.cv_api.getData()
        image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0
        
        self.colorAct.setChecked(True)
        self.greyAct.setChecked(False)

    def discardChanges(self):

        actionsList = [self.horizontalAct, self.verticalAct, 
                       self.px_10, self.px_20, self.px_50, 
                       self.px_100, self.leftAct,self.rightAct, 
                       self.topAct, self.bottomAct
                       ]
        for action in actionsList:
            action.setChecked(False)
        self.cv_api.discardData()
        
        image = self.cv_api.getData()
        if not self.cv_api.flag_grey:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        else:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0

    def rotateImage(self, direction):
        if direction == 'anti':
            self.cv_api.addRotation(10)
        elif direction == "clock":
            self.cv_api.addRotation(-10)

        image = self.cv_api.getData()
        if not self.cv_api.flag_grey:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        else:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0

    def changeBorderSide(self):
        sides = {'left':self.leftAct.isChecked(), 
                 'right':self.rightAct.isChecked(),
                 'top': self.topAct.isChecked(),
                 'bottom': self.bottomAct.isChecked()
                }
        self.cv_api.addBorderSides(sides)
        self.cv_api.addBorders()

        image = self.cv_api.getData()
        if not self.cv_api.flag_grey:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        else:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0
        
    def changePerspectiveOrient(self, orient):
        if orient == 'horizontal':
            self.verticalAct.setChecked(False)
        if orient == 'vertical':
            self.horizontalAct.setChecked(False)
        self.increaseAct.setEnabled(True)
        self.cv_api.setPerspective(orient=orient, percentage=self.perspective)

        image = self.cv_api.getData()
        if not self.cv_api.flag_grey:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        else:
            image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.scaleFactor = 1.0

    def changePerspectiveDepth(self, option):
        if option == 'increase':
            self.perspective += 5
            self.decreaseAct.setEnabled(True)
            print("inc: ", self.perspective)
            if self.perspective >= 40:
                self.increaseAct.setEnabled(False)
                print("over-flow")
        
        elif option == 'decrease':
            self.perspective -= 5
            self.increaseAct.setEnabled(True)
            print("dec: ", self.perspective)
            if self.perspective <= 0:
                print('underflow')
                self.decreaseAct.setEnabled(False)
        
        if self.verticalAct.isChecked():
            self.changePerspectiveOrient(orient='vertical')
        elif self.horizontalAct.isChecked():
            self.changePerspectiveOrient(orient='horizontal')

    def createBorder(self, action, border_width):
        if border_width != self.cv_api.border_size:
            borderactions = [self.px_10, self.px_20, self.px_50, self.px_100]
            for act in borderactions:
                if act == action:
                    act.setChecked(True)
                else:
                    act.setChecked(False)
            
            self.cv_api.addBorderSides()
            self.cv_api.changeBorderSize(border_width)

            sides_list = [self.leftAct, self.rightAct, self.topAct, self.bottomAct]
            for sideAct in sides_list:
                sideAct.setChecked(True)

            self.cv_api.addBorders()

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
        # self.link = fileName
        if fileName:
            image = self.getImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return

            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.scrollArea.setVisible(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            self.fitToWindow()

            edit_menu_list = [self.saveAct, self.discardAct, self.colorMenu, self.rotateMenu, self.perspectiveMenu, self.borderMenu, self.scaleMenu]
            for menu in edit_menu_list:
                menu.setEnabled(True)


            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def save(self):
        if self.save_path == None:
            options = QFileDialog.Options()
            filter = 'JPEG (*.jpg);;PNG (*.png);;Bitmap (*.bmp)'
            self.save_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '',
                                                            filter, options=options)

        if self.save_path:
            self.cv_api.saveImage(self.save_path)

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
        self.saveAct = QAction("&Save", self, shortcut='Ctrl+s', enabled=False, triggered=self.save)
        self.discardAct = QAction("&Discard", self, shortcut='Ctrl+d', enabled=False, triggered=self.discardChanges)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+q", triggered=self.close)

        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, checked=True, shortcut="Ctrl+F", triggered=self.fitToWindow)
        
        self.greyAct = QAction("GreyScale", self, checkable=True, triggered=self.greyFormat)
        self.colorAct = QAction("Colored", self, checkable=True, checked=True, triggered=self.coloredFormat)
        self.clockAct = QAction("Clockwise 10 Degree", self, triggered=lambda:self.rotateImage("clock"))
        self.antiClockAct = QAction("Anti-Clockwise 10 Degree", self, triggered=lambda:self.rotateImage("anti"))
        self.verticalAct = QAction("Vertical", self, checkable=True, checked=False, triggered=lambda:self.changePerspectiveOrient('vertical'))
        self.horizontalAct = QAction("Horizontal", self, checkable=True, checked=False, triggered=lambda:self.changePerspectiveOrient('horizontal'))
        self.increaseAct = QAction("Increase", self, enabled=False, triggered=lambda:self.changePerspectiveDepth('increase'))
        self.decreaseAct = QAction("Decrease", self, enabled=False, triggered=lambda:self.changePerspectiveDepth('decrease'))
        self.px_10 = QAction("10 px", self, checkable=True, checked=False, triggered=lambda:self.createBorder(self.px_10, 10))
        self.px_20 = QAction("20 px", self, checkable=True, checked=False, triggered=lambda:self.createBorder(self.px_20, 20))
        self.px_50 = QAction("50 px", self, checkable=True, checked=False, triggered=lambda:self.createBorder(self.px_50, 50))
        self.px_100 = QAction("100 px", self, checkable=True, checked=False, triggered=lambda:self.createBorder(self.px_100, 100))
        self.leftAct = QAction("Left", self, checkable=True, checked=False, triggered=self.changeBorderSide)
        self.rightAct = QAction("Right", self, checkable=True, checked=False, triggered=self.changeBorderSide)
        self.topAct = QAction("Top", self, checkable=True, checked=False, triggered=self.changeBorderSide)
        self.bottomAct = QAction("Buttom", self, checkable=True, checked=False, triggered=self.changeBorderSide)
        self.scaleUpAct = QAction("Scale Up", self)
        self.scaleDownAct = QAction("Scale Down", self)

        self.blurAct = QAction("Blur", self, checkable=True, checked=False, enabled=False)
        self.motionBlurAct = QAction("Motion Blur", self, checkable=True, checked=False, enabled=False)
        self.sharpAct = QAction("Sharpen", self, checkable=True, checked=False, enabled=False)
        

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
        self.sizeMenu = QMenu("Size", self.borderMenu)
        self.sizeMenu.addAction(self.px_10)
        self.sizeMenu.addAction(self.px_20)
        self.sizeMenu.addAction(self.px_50)
        self.sizeMenu.addAction(self.px_100)
        self.borderMenu.addMenu(self.sizeMenu)
        self.borderMenu.addAction(self.leftAct)
        self.borderMenu.addAction(self.rightAct)
        self.borderMenu.addAction(self.topAct)
        self.borderMenu.addAction(self.bottomAct)
        self.scaleMenu.addAction(self.scaleUpAct)
        self.scaleMenu.addAction(self.scaleDownAct)

        self.filterMenu = QMenu("&Filters", self)
        self.filterMenu.addAction(self.blurAct)
        self.filterMenu.addAction(self.motionBlurAct)
        self.filterMenu.addAction(self.sharpAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.filterMenu)
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