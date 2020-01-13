import cv2
import numpy as np

class Image:
    def __init__(self, file):
        self.filename = file
        
        self.image = cv2.imread(self.filename)
        self.backup_image = cv2.imread(self.filename)

        self.angle = 0
        self.border_size = 0
        self.border_color = 255
        self.border_sides = {'left':False, 'right':False, 'top':False, 'bottom':False}

        self.flag_grey = False

    def saveImage(self, path):
        cv2.imwrite(path, self.image)
        self.flag_saved = True
        
    def getData(self):
        return self.image

    def discardData(self):
        self.angle = 0
        self.border_size = 0,
        self.border_color = 255,
        self.border_sides = {'left':False, 'right':False, 'top':False, 'bottom':False}
        self.__remake()

    def showImage(self):
        cv2.imshow('Image', self.image)
        cv2.waitKey()

    def __grey(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

    def __color(self):
        self.image = self.backup_image

    def __rotate(self):
        num_rows, num_cols = self.image.shape[:2]
        rot_matrix = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), self.angle, 1)
        self.image = cv2.warpAffine(self.image, rot_matrix, (num_cols, num_rows))

    def __remake(self):
        del self.image
        self.image = self.backup_image.copy()

        if self.flag_grey:
            self.__grey()
        if self.angle:
            self.__rotate()
        

    def __border(self):
        self.__remake()
        width, height= len(self.image[0]), len(self.image)

        for row in range(height):
            if (row < self.border_size and self.border_sides['top']) or (row > height-self.border_size and self.border_sides['bottom']):
                for col in range(width):
                    self.image[row][col] = self.border_color
            else:
                for col in range(self.border_size):
                    if self.border_sides['left']:
                        self.image[row][col] = self.border_color
                    if self.border_sides['right']:
                        self.image[row][width - col - 1] = self.border_color

    def setFormatGrey(self):
        self.__remake()
        if not self.flag_grey:
            self.__grey()
            self.flag_grey = True

    def setFormatColor(self):
        if self.flag_grey:
            self.__color()
            self.flag_grey = False
        self.__remake()
        self.addBorders()
    
    def addRotation(self, inc_angle):
        self.angle += inc_angle
        self.__remake()
        self.addBorders()

    def changeBorderSize(self, new_size):
        if new_size != self.border_size:
            self.border_size = new_size

    def addBorderSides(self, new_sides):
        self.border_sides = new_sides.copy()

    def setBorderColor(self, color):
        self.border_color = color

    def addBorders(self):
        self.__border()


if __name__ == "__main__":
    img = Image("E:\Python\Image Edit\Test_images\Cat_small.jpg")
    img.showImage()
   
    img.addRotation(-10)
    img.showImage()

    img.addRotation(10)
    img.showImage()

    img.addBorderSides({'left':True, 'right':True, 'top':True, 'bottom':True})
    img.changeBorderSize(20)
    img.addBorders()
    img.showImage()

    img.addRotation(180)
    img.showImage()

    img.discardData()
    img.showImage()

    img.setFormatGrey()
    img.showImage()
    '''  
    img.addRotation(10)
    img.showImage()


    img.addRotation(20)
    img.showImage()

    img.setFormatColor()
    img.showImage()

    img.addBorderSides({'left':True, 'right':False, 'top':False, 'bottom':True})
    img.changeBorderSize(20)
    img.addBorders()
    img.showImage()
    '''
