import numpy
import base64
import socket
import threading
import cv2
import json
import time
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

    def goCenterByPoint(self,point,basePoint):
        if abs(point-basePoint)<3:
            dir='c'
        elif basePoint-point>0:
            dir='l'
        else :
            dir='r'
        return dir

    def goCenterByCurve(self,curve):
        if abs(curve)>5:
            dir='c'
        elif curve>0:
            dir='l'
        else :
            dir='r'
        return dir

    def calDir(self,point,curve,basePoint):
        # #커브는 없지만 센터가 안맞을 때
        # if abs(curve)>5:
        #     dir=self.goCenterByPoint(point,basePoint)
        # else:
        #     if abs(point-basePoint)>5:
        #         dir=self.goCenterByPoint(point,basePoint)
        #     else:
        #         dir=self.goCenterByCurve(curve)

        # self.steerJson['dir']=dir
        dir=self.goCenterByPoint(point,basePoint)
        self.steerJson['dir']=dir

    def getSteerData(self):
        return self.steerJson


class getVideoServer():
    def __init__(self, ip, port):
        self.UDP_IP = ip
        self.UDP_PORT = port
        self.socketOpen()
        self.steer=updateSteer(84)
        self.steerData=self.steer.getSteerData()
        self.getLane=getCurveLane()
        self.sendThread=threading.Thread(target=self.sendData)
        self.receiveThread = threading.Thread(target=self.receiveImages)
        self.setSpeedThread = threading.Thread(target=self.setDefSpeed)
        self.client_addr=None
        self.sendThread.start()
        self.receiveThread.start()
        self.setSpeedThread.start()

    def setDefSpeed(self):
        while True:
            speed=input("Default Speed :")
            self.steer.setDefSpeed(int(speed))
            time.sleep(0.1)

    def socketClose(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')

    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        
    def receiveImages(self):
        # try:
        s = [b'\xff' * 46080 for x in range(15)]
        isGet=[False for x in range(15)]
        while True:
            picture=b''
            data,addr=self.sock.recvfrom(46081)
            self.client_addr=addr
            s[data[0]] = data[1:46081]
            isGet[data[0]]=True

            if data[0]==14:
                for i in range(15):
                    picture+=s[i]
                frame=numpy.fromstring(picture,dtype=numpy.uint8)
                frame=frame.reshape(360,640,3)
                middle,curve=self.getLane.getLaneCurve(frame)
                BASE_CENTER=320
                self.steer.calDir(middle,curve,BASE_CENTER)
                self.steerData=self.steer.getSteerData()
                cv2.imshow('window',frame)
                cv2.waitKey(1)

        # except Exception as e:
        #     print(e)
        #     self.handleError(e)


    def sendData(self):
        # try:
        while True:
            if self.client_addr==None:
                continue
            self.sock.sendto(json.dumps(self.steerData).encode('utf-8').ljust(64),self.client_addr)
            time.sleep(0.1)

        # except Exception as e:
        #     print(e)
        #     self.handleError(e)

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
    HOST_IP="141.223.140.53"
    HOST_PORT=9667
    vs=getVideoServer(HOST_IP,HOST_PORT)

main()
