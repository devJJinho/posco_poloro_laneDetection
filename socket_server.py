import numpy
import base64
import socket
import threading
import cv2
import json
import time
# from laneDetection import imageProcessing
# from origin_lane import imageProcessing
from lanedetection import getCurveLane
import sys
import warnings

class updateSteer:
    def __init__(self,def_speed):
        self.steerJson=dict()
        self.steerJson['def_speed']=def_speed
        self.steerJson['dir']='c'
        self.steerJson['speed']=1
  
    def setDefSpeed(self,updated_speed):
        self.steerJson['def_speed']=updated_speed
    
    def setSpeed(self,updated_speed):
        self.steerJson['speed']=updated_speed

    def calDir(self,point):
        if abs(point)<20:
            dir='c'
        elif point>0:
            dir='l'
        else :
            dir='r'
        self.steerJson['dir']=dir

    def getSteerData(self):
        return self.steerJson


class getVideoServer():
    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.socketOpen()
        self.steer=updateSteer(84)
        self.steerData=self.steer.getSteerData()
        self.getLane=getCurveLane()
        self.sendThread=threading.Thread(target=self.sendData)
        self.receiveThread = threading.Thread(target=self.receiveImages)
        self.setSpeedThread = threading.Thread(target=self.setDefSpeed)
        
        self.sendThread.start()
        self.receiveThread.start()
        self.setSpeedThread.start()

    def setDefSpeed(self):
        while True:
            speed=input("Default Speed :")
            self.steer.setDefSpeed(int(speed))

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
            while True:
                # length = self.recvall(self.conn, 64)
                length=self.conn.recv(64)
                length1 = length.decode('utf-8')
                stringData = self.recvall(self.conn, int(length1))
                data = numpy.frombuffer(base64.b64decode(stringData), numpy.uint8)
                decimg = cv2.imdecode(data, 1)
                cv2.resize(decimg,(1280,720))
                res=self.getLane.getLaneCurve(decimg)
                BASE_CENTER=614
                self.steer.calDir(res)
                self.steerData=self.steer.getSteerData()
                # print(self.steerData)
                # cv2.imshow("image", decimg)
                # cv2.waitKey(1)

        except Exception as e:
            print(e)
            self.handleError(e)
            # self.sendThread.
            sys.exit()
            # self.receiveImages()

    def sendData(self):
        # try:
        while True:
            # print(json.dumps(self.steerData).encode('utf-8').ljust(64))
            self.conn.send(json.dumps(self.steerData).encode('utf-8').ljust(64))
            # self.sock.send(str(1234).encode('utf-8').ljust(64))
            time.sleep(0.09)

        # except Exception as e:
        #     print(e)
        #     self.handleError(e)
        #     # self.sendData()

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
    warnings.filterwarnings("ignore")
    HOST_IP="192.168.0.243"
    HOST_PORT=9667
    vs=getVideoServer(HOST_IP,HOST_PORT)

main()