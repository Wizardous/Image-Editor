import cv2
import numpy as np

class Image:
    def __init__(self, file):
        self.filename = file
        
        self.image = cv2.imread(self.filename)
        self.backup_image = cv2.imread(self.filename)

        self.flag_grey = False

        self.angle = 0
        self.border_size = 0
        self.border_color = 255
        self.border_sides = {'left':False, 'right':False, 'top':False, 'bottom':False}

        self.perspectivePercentage = 0
        self.perspectiveOrientation = 0
        self.corner_points = None
        self.perspectivePoints = None
        self.transform_matrix = None

    def saveImage(self, path):
        cv2.imwrite(path, self.image)
        self.flag_saved = True
        
    def getData(self):
        return self.image

    def discardData(self):
        self.angle = 0
        self.flag_grey = False
        self.border_size = 0,
        self.border_color = 255,
        self.border_sides = {'left':False, 'right':False, 'top':False, 'bottom':False}
        self.perspectiveOrientation = None
        self.perspectivePercentage = 0
        self.perspectivePoints = None
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

    def __makePerspectiveMatrix(self):

        num_rows, num_cols = self.image.shape[:2]

        self.corner_points = np.float32([[0,0],
                                        [num_cols-1, 0],
                                        [0, num_rows-1],
                                        [num_cols-1, num_rows-1]]
                                    )

        per = self.perspectivePercentage
        
        if self.perspectiveOrientation == "vertical":
            self.perspectivePoints = np.float32([[per*num_cols-1, 0],
                                                 [(1-per)*num_cols-1 , 0], 
                                                 [0, num_rows-1], 
                                                 [num_cols-1, num_rows-1]]
                                                )

        elif self.perspectiveOrientation == "horizontal":
            self.perspectivePoints = np.float32([[0, 0],
                                                 [num_cols-1 , per*num_rows-1], 
                                                 [0, num_rows-1], 
                                                 [num_cols-1, (1-per)*num_rows-1]]
                                                )
        
        self.transform_matrix = cv2.getPerspectiveTransform(self.corner_points, self.perspectivePoints)


    def __addPerspective(self):
        if self.perspectiveOrientation:
            num_rows, num_cols = self.image.shape[:2]
            self.image = cv2.warpPerspective(self.image, self.transform_matrix, (num_cols, num_rows))

    def setPerspective(self, orient='vertical', percentage=10):
        self.perspectiveOrientation = orient
        self.perspectivePercentage = percentage/100
        
        self.__makePerspectiveMatrix()
        self.__remake()
        self.addBorders()

        
    def __remake(self):
        del self.image
        self.image = self.backup_image.copy()

        if self.flag_grey:
            self.__grey()
        if self.angle:
            self.__rotate()
        self.__addPerspective()

    def setFormatGrey(self):
        self.__remake()
        if not self.flag_grey:
            self.__grey()
            self.flag_grey = True

        self.addBorders()

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

    def addBorderSides(self, new_sides={'left':True, 'right':True, 'top':True, 'bottom':True}):
        self.border_sides = new_sides.copy()

    def setBorderColor(self, color):
        self.border_color = color

    def addBorders(self):
        self.__border()


if __name__ == "__main__":
    img = Image("E:\Python\Image Edit\Test_images\Cat_small.jpg")
    img.showImage()

    img.setFormatGrey()
    img.showImage()

    img.addRotation(10)
    img.showImage()

    img.discardData()
    img.showImage()
   


'''


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