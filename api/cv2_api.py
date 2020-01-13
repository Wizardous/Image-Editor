import cv2

class Image:

    def __init__(self, filename):
        self.filename = filename
        
        self.image = None
        self.backup_image = None

        self.angle = 0
        self.flag_grey = False
        self.flag_rotated = False
        self.flag_saved = False

        self.openImage()


    def openImage(self):
        self.image = cv2.imread(self.filename)
        self.backup_image = self.image

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
        self.flag_saved = False

    def colored(self):
        self.flag_grey = False
        self.image = self.backup_image
        self.flag_saved = False
        pass

    def rotate(self, angle_inc):
        self.angle += angle_inc
        
        self.image = self.backup_image
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
        self.image = self.backup_image
        self.flag_saved = False

    def createBorder(self, border_width, sides, color=255):
        width = len(self.image[0])
        height = len(self.image)
        for i in range(height):
            if (i < border_width and sides['top']) or (i > height-border_width and sides['bottom']):
                for j in range(width):
                    self.image[i][j] = color
            else:
                for j in range(border_width):
                    if sides['left']:
                        self.image[i][j] = color
                    if sides['right']:
                        self.image[i][j + width - border_width] = color
        
        self.flag_saved = False

if __name__ == "__main__":
    img = Image("E:\Python\Image Edit\Test_images\Cat_small.jpg")
    side = {}
    side['left'] = False
    side['right'] = True
    side['top'] = True
    side['bottom'] = False

    img.createBorder(10, side)
    img.showImage()
    cv2.waitKey()
