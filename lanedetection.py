import cv2
import numpy as np
import utlis

class getCurveLane:
    def __init__(self):
        self.curveList=[]
        self.avgVal=10
        self.intialTrackBarVals = [106, 144, 55, 235]
        utlis.initializeTrackbars(self.intialTrackBarVals)

    def getLaneCurve(self,img,display=1):
        img = cv2.resize(img, (480, 240))
        imgCopy = img.copy()
        imgResult = img.copy()

        #### step1
        imgThres = utlis.thresholding(img)

        #### step2
        hT, wT, c = img.shape
        points = utlis.valTrackbars()
        # points=None
        imgWarp = utlis.warpImg(imgThres,points,wT,hT)
        imgWarpPoints = utlis.drawPoints(imgCopy,points)

        #### step3
        middlePoint,imgHist, _ = utlis.getHistogram(imgWarp, display=True, minPer=0.5, region=4)
        curveAveragePoint, imgHist, Real_Coor = utlis.getHistogram(imgWarp, display=True, minPer=0.9)
        curveRaw = curveAveragePoint - middlePoint
        #### step4
        self.curveList.append(curveRaw)
        if len(self.curveList)>self.avgVal:
            self.curveList.pop(0)
        curve = int(sum(self.curveList)/len(self.curveList))
        #### step5
        if display != 0:
            imgInvWarp = utlis.warpImg(imgWarp, points, wT, hT, inv=True)
            imgInvWarp = cv2.cvtColor(imgInvWarp, cv2.COLOR_GRAY2BGR)
            imgInvWarp [0:hT // 3, 0:wT] = 0, 0, 0
            imgLaneColor = np.zeros_like(img)
            imgLaneColor[:] = 0, 255, 0
            imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
            imgResult = cv2.addWeighted(imgResult, 1, imgLaneColor, 1, 0)
            midY = 450
            cv2.putText(imgResult, str(curve), (wT // 2 - 80, 85), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
            cv2.line(imgResult, (wT // 2, midY), (wT // 2 + (curve * 3), midY), (255, 0, 255), 5)
            cv2.line(imgResult, ((wT // 2 + (curve * 3)), midY - 25), (wT // 2 + (curve * 3), midY + 25), (0, 255, 0), 5)
            for x in range(-30, 30):
                w = wT // 20
                cv2.line(imgResult, (w * x + int(curve // 50), midY - 10),
                        (w * x + int(curve // 50), midY + 10), (0, 0, 255), 2)
            # fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
            # cv2.putText(imgResult, 'FPS ' + str(int(fps)), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (230, 50, 50), 3);
        if display == 2:
            imgStacked = utlis.stackImages(0.7, ([img, imgWarpPoints, imgWarp],
                                                [imgHist, imgLaneColor, imgResult]))
            cv2.imshow('ImageStack', imgStacked)
        elif display == 1:
            cv2.imshow('Resutlt', imgResult)

        cv2.imshow('Thres', imgThres)
        cv2.imshow('Warp', imgWarp)
        cv2.imshow('Warp Points', imgWarpPoints)
        cv2.imshow('Histogram', imgHist)

        return curve

# def imageProcessing(img):

#     # frameCounter = 0
#     # frameCounter += 1
#     # if cap.get(cv2.CAP_PROP_FRAME_COUNT) == frameCounter:
#     #     cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
#     #     frameCounter = 0
#     # success, img = cap.read()
#     # 프레임
#     # img = cv2.resize(img, (480, 240))
#     # print(getLaneCurve(img))
#     # Mid_point, Real_Coor1 = getLaneCurve(img, display=1)
#     # print('Area     : {}    Mid_Point : {}'.format(Real_Coor1, Mid_point))
#     # cv2.imshow('Vid', img)
#     # cv2.waitKey(1)

