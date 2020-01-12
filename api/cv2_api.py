import cv2

class Image:

    def __init__(self, filename):
        self.filename = filename
        
        self.image = None
        self.backup_image = None

        self.angle = 0
        self.flag_grey = False
        self.flag_rotated = False

        self.openImage()


    def openImage(self):
        self.image = cv2.imread(self.filename)
        self.backup_image = self.image
        
    def getData(self):
        return self.image

    def grayScale(self):
        self.flag_grey = True
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        pass

    def colored(self):
        self.flag_grey = False
        self.image = self.backup_image
        pass

    def rotate(self, angle_inc):
        self.angle += angle_inc
        
        self.image = self.backup_image
        if self.flag_grey:
            self.grayScale()
            
        num_rows, num_cols = self.image.shape[:2]
        
        rot_matrix = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), self.angle, 1)

        self.image = cv2.warpAffine(self.image, rot_matrix, (num_cols, num_rows))
