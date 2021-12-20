import cv2
import numpy as np

# 1) 색 변환: BRG -> HSV
# 2) 이진(black/white) 변환: maskWhite 변수에 저장
def thresholding(img):
    imgHsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    # lowerWhite = np.array([30,0,0])
    # upperWhite = np.array([140,255,255])
    # HSV 컬러 공간
    # lowerWhite = np.array([80,0,0])
    # upperWhite = np.array([255,160,255])
    # lowerWhite보다 낮으면 black으로 변환 / 높으면 white로 변환

    # BGR 컬러 공간
    #lowerWhite = np.array([100,100,100])
    #upperWhite = np.array([220,220,255])
    # cam 교체 전
    # lowerWhite = np.array([110,110,130])
    # upperWhite = np.array([225,225,240])
    # 1차
    # lowerWhite = np.array([110,120,100])
    # upperWhite = np.array([230,240,220])
    # 2차
    # lowerWhite = np.array([192,192,192])
    # upperWhite = np.array([255,255,255])

    # 3차
    # lowerWhite = np.array([150,150,140])
    # upperWhite = np.array([215,215,195])
    # 4차
    # lowerWhite = np.array([180,180,170])
    # upperWhite = np.array([225,225,215])
    # lowerWhite = np.array([195,162,160])
    # upperWhite = np.array([240,220,205])
    # lowerWhite = np.array([200,167,165])
    # upperWhite = np.array([240,220,205])

    lowerWhite = np.array([155,155,155])
    upperWhite = np.array([255,255,255])
    

    #lowerWhite = np.array([190,185,185])
    #upperWhite = np.array([230,220,215])
    # 5차

    maskWhite = cv2.inRange(img,lowerWhite,upperWhite)
    return maskWhite

# bird eye view로 전환
# w, h에 hT, wT 보냄 / hT, wT, c = img.shape
def warpImg(img,points,w,h,inv = False):
    # points = utlis.valTrackbars()
    # : Width Top, Height Top, Width Bottom, Height Bottom
    pts1 = np.float32(points)
    # 좌표 순서: 상단왼쪽 끝, 상단오른쪽 끝, 하단왼쪽 끝, 하단오른쪽 끝
    pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]]) # 이미지 전체 영역을 4가지 좌표로 지정
    
    if inv: # inverse가 True
        matrix = cv2.getPerspectiveTransform(pts2,pts1)
    else: # inv=False
        matrix = cv2.getPerspectiveTransform(pts1,pts2)
    
    imgWarp = cv2.warpPerspective(img,matrix,(w,h))
    return imgWarp

def nothing(a):
    pass


## 성민 요청으로 트랙바 관련 코드를 전체 주석 처리함

# ROI 값 초기화/ROI 수정하는 트랙바 생성
# Width Top, Height Top, Width Bottom, Height Bottom
# wT: width Target / hT: height Target
# def initializeTrackbars(intialTracbarVals,wT=480, hT=240):
#     cv2.namedWindow("Trackbars")
#     cv2.resizeWindow("Trackbars", 360, 240)
#     cv2.createTrackbar("Width Top", "Trackbars", intialTracbarVals[0],wT//2, nothing)
#     cv2.createTrackbar("Height Top", "Trackbars", intialTracbarVals[1], hT, nothing)
#     cv2.createTrackbar("Width Bottom", "Trackbars", intialTracbarVals[2],wT//2, nothing)
#     cv2.createTrackbar("Height Bottom", "Trackbars", intialTracbarVals[3], hT, nothing)

# intialTrackBarVals = [106, 144, 55, 235]
# Trackbars의 값 받아와서 points 변수에 저장하기
# wT: width Target / hT: height Target
def valTrackbars(wT=640, hT=360):
    # widthTop = cv2.getTrackbarPos("Width Top", "Trackbars")
    # heightTop = cv2.getTrackbarPos("Height Top", "Trackbars")
    # widthBottom = cv2.getTrackbarPos("Width Bottom", "Trackbars")
    # heightBottom = cv2.getTrackbarPos("Height Bottom", "Trackbars")

    # 103, 178, 63, 240
    # 원본 70 200 10 360
    widthTop = 70
    heightTop = 250
    widthBottom = 10 # 55
    heightBottom = 360

    # pts2 = np.float([[0,0],[w,0],[0,h],[w,h]]) -> 이거 같은 느낌
    points = np.float32([(widthTop, heightTop), (wT-widthTop, heightTop),
                      (widthBottom , heightBottom ), (wT-widthBottom, heightBottom)])
    return points

def drawPoints(img,points):
    # 아래는 points 변수의 인덱싱 예시
    # points = np.float32([(480,320), (160,320), (480,150), (400,150)])
    # points[0] -> array([480., 320.])
    # points[0][0] -> 480.0 / points[0][1] -> 320.0

    for x in range(4): # 4개의 원 그리기
        # 15: 사이즈, (0,0,255): red 색상
        cv2.circle(img,(int(points[x][0]),int(points[x][1])),15,(0,0,255),cv2.FILLED)
    return img

def getHistogram(img,minPer=0.1, display=False,region=1): # minimum percentage
    # axis=0 -> x축을 기준으로 합을 구하는 방식. x축 row를 합산함.
    # : 가장 외각의 괄호를 제거하는 이미지로 생각하면 이해하기 편함.
    # ex) (4, 2, 3) => (2, 3)
    # axis=1 -> y축을 기준으로 합을 구하는 방식. y축 column을 합산함.
    # : 가장 외각에서 두 번째 괄호를 제거하는 이미지로 생각하면 편리함.
    # ex) (4,2,3) => (4,3) / 각 row의 2개의 칼럼이 1개로 축소됨.

    # img.shape -> height, width, channel
    # sum all the columns(여기서는 height)
    if region ==1:
        histValues = np.sum(img,axis=0)
    else:
        histValues = np.sum(img[img.shape[0]//region:,:], axis=0)

    # print(histValues)
    maxValue = np.max(histValues)
    minValue = minPer*maxValue
    indexArray = np.where(histValues >= minValue)
    basePoint = int(np.average(indexArray))      #나중에 float
    # print(basePoint)

    if display:
        # 3 -> 3 channels
        imgHist = np.zeros((img.shape[0],img.shape[1],3),np.uint8)
        # print(imgHist.shape)
        for x,intensity in enumerate(histValues):
            # print(x//2, img.shape[0]-int(intensity//255//region))
            cv2.line(imgHist,(x,img.shape[0]),(x,img.shape[0]-int(intensity//255//region)),(255,0,255),1) # 1 -> thickness
            cv2.circle(imgHist,(basePoint,img.shape[0]),20,(0,255,255),cv2.FILLED)
        return basePoint, imgHist, [x//2, img.shape[0]-int(intensity//255//region)]
    return basePoint

def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver
