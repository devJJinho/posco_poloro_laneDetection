import darknet as dn
import numpy as np
import cv2

class detectSign:
    def __init__(self):
        self.CFG='custom/yolov4-custom.cfg'
        self.DATA='custom/obj.data'
        self.WEIGHTS='custom/yolov4-custom_final.weights'
        self.imgChannel=(640,340,3)
        self.net,self.cname,_=dn.load_network(self.CFG,self.DATA,self.WEIGHTS, batch_size=1)

    def detect_sign(self,img):
        darknet_image=dn.make_image(self.imgChannel[0],self.imgChannel[1],self.imgChannel[2])
        dn.copy_image_from_bytes(darknet_image, img.tobytes())
        detected=dn.detect_image(self.net,self.cname,darknet_image)
        # Threshold code required
        return 'A'