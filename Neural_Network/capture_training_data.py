import numpy
import base64
import socket
import threading
import cv2
import json
import time
from origin_lane import imageProcessing
import sys

def calDir(point,basePoint):
    if abs(basePoint-point)<50:
        dir='c'
    elif point<basePoint:
        dir='r'
    else :
        dir='l'
    steerJson={
        'speed':1,
        'def_speed':93,
    }
    steerJson['dir']=dir
    return steerJson


class getVideoServer():
    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.steerData={
            'dir':'c',
            'def_speed':82,
            'speed':1
        }
        self.socketOpen()
        self.sendThread=threading.Thread(target=self.sendData)
        self.receiveThread = threading.Thread(target=self.receiveImages)
        # self.setSpeedThread = threading.Thread(target=self.setDefSpeed)

        self.sendThread.start()
        self.receiveThread.start()
        # self.setSpeedThread.start()

    def setDefSpeed(self):
        speed=input("Default Speed :")
        self.steerData['def_speed']=float(speed)

    def socketClose(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')

    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen(1)
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')
        self.conn, self.addr = self.sock.accept()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is connected with client')

    def receiveImages(self):
        try:
            preState='s'
            filePath='/home/piai/learningImage'
            i=0
            while True:
                length=self.conn.recv(64)
                length1 = length.decode('utf-8')
                stringData = self.recvall(self.conn, int(length1))
                data = numpy.frombuffer(base64.b64decode(stringData), numpy.uint8)
                decimg = cv2.imdecode(data, 1)
                carState=None
                keyValue=cv2.waitKey(10)
                carState=None
                if keyValue==81:
                    carState='left'
                    print('left')
                elif keyValue==83:
                    carState='right'
                    print('right')
                elif keyValue==82:
                    carState='go'
                    print('go')

                saveImage=decimg[:,:,:]
                saveImage=cv2.cvtColor(saveImage, cv2.COLOR_BGR2HLS)
                saveImage = cv2.GaussianBlur(saveImage, (3,3), 0)
                # saveImage = cv2.resize(saveImage, (640, 360))
                mask = cv2.erode(saveImage, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)

                cv2.imshow('Save Image',mask)

                if carState!=None:
            
                    angle=None
                    if carState=='left':
                        angle=45
                    elif carState=='go':
                        angle=90
                    elif carState=='right':
                        angle=135
                    
                    cv2.imwrite("%s/%05d_%s_%03d.png"%(filePath,i,preState,angle),saveImage)
                    i=i+1


        except Exception as e:
            print(e)
            self.handleError(e)



    def sendData(self):
        # try:
        while True:
            self.conn.send(json.dumps(self.steerData).encode('utf-8').ljust(64))
            time.sleep(0.09)

        # except Exception as e:
        #     print(e)
        #     self.handleError(e)
   

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def handleError(self,e):
        print(e)
        self.socketClose()
        # cv2.destroyAllWindows()
        # self.socketOpen()
        # self.receiveThread = threading.Thread(target=self.receiveImages)
        # self.receiveThread = threading.Thread(target=self.receiveImages)
        # self.receiveThread.start()
        # self.receiveThread.start()

def main():
    HOST_IP="192.168.0.243"
    HOST_PORT=9667
    vs=getVideoServer(HOST_IP,HOST_PORT)

main()
