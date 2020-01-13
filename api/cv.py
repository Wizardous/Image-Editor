import cv2

class Image:

    def __init__(self, filename):
        self.filename = filename
        
        self.image = None
        self.backup_image = None

        self.angle = 0
        self.current_border = 0
        self.border_sides = {'left':False, 'right':False, 'top':False, 'bottom':False}

        self.flag_grey = False
        self.flag_saved = False

        self.openImage()


    def openImage(self):
        self.image = cv2.imread(self.filename)
        self.backup_image = self.image.copy()

    def saveImage(self, path):
        cv2.imwrite(path, self.image)
        self.flag_saved = True
        
    def getData(self):
        return self.image
    
    def showImage(self):
        cv2.imshow('Image', self.image)

    def grayScale(self):
        self.flag_grey = True
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        self.rotate(0)
        self.createBorder(self.current_border)
        self.flag_saved = False

    def colored(self):
        self.flag_grey = False
        self.image = self.backup_image.copy()

        self.rotate(0)
        self.createBorder(self.current_border)
        self.flag_saved = False
        pass

    def rotate(self, angle_inc):
        self.angle += angle_inc
        
        self.image = self.backup_image.copy()
        if self.flag_grey:
            self.grayScale()
        

        num_rows, num_cols = self.image.shape[:2]
        rot_matrix = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), self.angle, 1)
        self.image = cv2.warpAffine(self.image, rot_matrix, (num_cols, num_rows))
        self.flag_saved = False

    def resetImage(self):
        self.angle = 0
        self.flag_grey = False
        self.flag_rotated = False
        self.image = self.backup_image.copy()
        self.flag_saved = False

    def createBorder(self, border_width, color=255):
        self.image = self.backup_image.copy()
        if self.flag_grey:
            self.grayScale()

        self.rotate(0)
        
        self.current_border = border_width
        width, height= len(self.image[0]), len(self.image)

        for i in range(height):
            if (i < self.current_border and self.border_sides['top']) or (i > height-self.current_border and self.border_sides['bottom']):
                for j in range(width):
                    self.image[i][j] = color
            else:
                for j in range(self.current_border):
                    if self.border_sides['left']:
                        self.image[i][j] = color
                    if self.border_sides['right']:
                        self.image[i][j + width - self.current_border] = color
                        
        self.flag_saved = False

if __name__ == "__main__":
    img = Image("E:\Python\Image Edit\Test_images\Cat_small.jpg")

    img.grayScale()    
    # img.rotate(10)

    img.showImage()
    cv2.waitKey()

