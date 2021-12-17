import cv2
import numpy as np
# import socket_frame_tcp_server

# canny edge detection: 경계선(윤곽선) 검출 방식에서 가장 많이 사용하는 알고리즘
def canny(img):
    if img is None: # 이미지 없음
        # cap.release()
        cv2.destroyAllWindows()
        exit()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # kernel은 window, filter, mask 등 다양한 이름으로 불리고 있음
    kernel = 5

    # 가우시안 블러: 가리기(흐려지게 하기) / 노이즈 제거
    # blur의 기본 원리: 특정한 kernel을 전체 이미지에 convolution을 돌려서,
    # 커널 사이즈에 맞게 픽셀 평균값을 대입하는 것
    # -> 즉, 특정 픽셀의 주변 값의 평균값을 해당 픽셀에 넣는 것
    # 가우시안 분포: 정규분포의 다른 이름(중간값이 가장 많고 극단으로 갈수록 적어짐)

    # GaussianBlur(src, ksize, sigmaX): 이미지에 가우시안 처리까지 한방에 해줌.
    # -> 커널 사이즈와 시그마만 입력하면 자동으로 이미지 or 영상을 변환함.
    # 범위가 넓어질수록 블러링 효과가 넓어지고, 노이즈가 제거됨
    # 과도하게 노이즈를 줄이면 원본 이미지 자체가 너무 흐릿해지는 부작용이 있음
    blur = cv2.GaussianBlur(gray,(kernel, kernel),0)
    # grayscale로 변환하는 이유: (Canny에서) Edge detection이 필요하기 때문
    canny = cv2.Canny(gray, 50, 150)
    return canny

# edge만 딴다고 무엇이 차선인지 구분할 수 있는 건 아님 -> 그래서 관심 영역을 재설정함
# 대개 자동차의 진행 방향 바닥에 존재하는 차선만을 검출하기 위해 관심 영역을 지정함
def region_of_interest(canny):
    height = canny.shape[0]
    width = canny.shape[1]

    # np.zeros_like : 어떤 변수만큼의 사이즈인 0 으로 가득 찬 Array를 배출함
    # 모두 0으로 돼있는 비어있는 영상을 만들고,
    # 그 영상에 4개의 정점으로 정의된 다각형 내부를 fillPoly 함수로 색상을 채움
    # 그러면 다각형 내부만 0이 아닌 수가 되고
    # 이 영상을 원래의 Edge 검출 영상과 bitwise_and 함수를 실행한 결과영상을 반환함
    # 결과 영상은 관심 영역의 Edge만 남게 됨
    mask = np.zeros_like(canny)
    # (관심 영역을) 삼각형 형태로 설정
    # triangle = np.array([[
    # (200, height),
    # (800, 350),
    # (1200, height),]], np.int32)

    # polylines(): 원하는 만큼의 좌표 점을 설정하여 선을 그을 수 있고, 시작점과 끝점을 자동 또는 수동으로 연결하여 다각형을 그릴 수 있음
    # fillpoly(): 다각형 형상을 이미지에 표현함. 다각형 내부를 특정 필터 데이터로 채움.
    # 타겟이미지(매개변수): Mat 형태의 이미지 파일을 소스로 지정.

    # rectangle = np.array([[(100, height), (100, 0), (1180, 0), (1180, height)]], np.int32)
    rectangle = np.array([[(150, height), (200, 500), (1050, 500), (1100, height)]], np.int32)
    cv2.fillPoly(mask, rectangle, 255)

    # 100 / 1100 또는 0 / 1280
    #triangle = np.array([[(150, height), (1100, height), (450, 0)]], np.int32)
    #cv2.fillPoly(mask, triangle, 255)

    # (이미지 비트연산) bitwise_and(): mask 영역에서 서로 공통으로 겹치는 부분 출력
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image

# 영상처리에서 허프 변환을 통해 직선을 검출함. 또한 여기에 확률을 더하여 검출 가능.
# 확률을 이용하여 직선인 것들만 구하므로 속도가 빠르다.
def houghLines(cropped_canny):
    # cropped_canny: canny(윤곽선 검출) 이후에 ROI(관심영역 지정) 처리를 한 이미지

    # HoughLinesP: 확률적용 허프변환 직선검출

    # cropped_canny -> 입력할 이미지 변수. Edge detect된 이미지를 입력해야 함.
    # 2 -> 계산할 픽셀의 해상도. 변환된 그래프에서 선에서 원점까지의 수직 거리.
    # np.pi/180- > 계산할 각도의 해상도, 선 회전 각도. 모든 방향에서 직선을 검출하려면 PI/180을 사용함.
    # minLineLength와 maxLineGap을 통해 찾고자 하는 선분을 두 번 걸러주게 됨.
    # minLineLength: 검출할 직선의 최소 길이, 단위는 픽셀
    # maxLineGap: 검출한 선 위의 점들 사이의 최대 거리, 점 사이의 거리가 이 값보다 크면 다른 선으로 간주함.
    return cv2.HoughLinesP(cropped_canny, 2, np.pi/180, 100,
        np.array([]), minLineLength=40, maxLineGap=5)

# 카메라 해상도 1280, 720
def addWeighted(frame, line_image):
    # cv2.line(line_image, (850, 0), (750, 1250), (0, 255, 0), 5)
    # 2개의 이미지를 하나의 이미지로 배경을 살리면서 합침.
    # 덧셈 연산을 할 시에 많은 부분이 흰색으로 나옴
    # 두 영상의 같은 위치에 존재하는 픽셀 값에 대하여 가중합을 계산하여 결과 영상의 픽셀 값으로 설정

    # cv2.addWeighted(src1, alpha, src2, beta, gamma)
    # -> result = src1 * alpha + src2 * beta + gamma
    # src1: 첫 번째 영상, src2: 두 번째 영상(src1과 같은 크기와 타입임)
    # alpha: 첫 번째 영상 가중치, beta: 두 번째 영상 가중치
    # gamma: 결과 영상에 추가적으로 더할 값
    return cv2.addWeighted(frame, 0.8, line_image, 1, 1)

# 원본.
# def display_lines(img,lines):
#     line_image = np.zeros_like(img)
#     if lines is not None:
#         # copy_line = lines.copy()
#         # print(copy_line[0][0][0], copy_line[0][0][2])
#         #
#         # lines.append([[1, 720, 1, 320]])
#         # print(lines)
#         for line in lines:
#             for x1, y1, x2, y2 in line:
#                 cv2.line(line_image, (x1, y1), (x2, y2),(0, 0, 255), 10)
#
#     return line_image

def display_lines(img,lines):
    line_image = np.zeros_like(img)
    if lines is not None:
        copy_line = lines.copy()
        # print(copy_line[0][0][0] + copy_line[0][0][2])
        # print(copy_line[1][0][0] + copy_line[1][0][2])
        middle_1 = (copy_line[0][0][0] + copy_line[1][0][0]) // 2
        middle_2 = (copy_line[0][0][2] + copy_line[1][0][2]) // 2

        # 720 --> y축 첫 시작 / 250 --> 어디까지 선을 그릴건지.
        copy_line.append([[middle_1, 720, middle_2, 432]])
        for line in copy_line:
            for x1, y1, x2, y2 in line:
                # print(x1, y1, x2, y2)
                # cv2.line(img, start, end, color, thickness)
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 0, 255), 10)
            # print('중앙값 좌표 : {}'.format(list(x for x in copy_line[2][0])))
            # 우리가 가야할 실시간 좌표

            # 사각형 좌측 하단 점 / 우측 하단 점
            # cv2.circle(line_image, ((copy_line[2][0][0] + copy_line[2][0][2]) // 2, 250), 25, (255, 255, 255), 3)

            # 삼각형 좌측 하단 점 / 우측 하단 점
            # 가야할 좌표 (copy_line[0][0][2] + copy_line[1][0][2]) // 2
            cv2.circle(line_image, ((copy_line[0][0][2] + copy_line[1][0][2]) // 2, 600), 25, (0, 255, 0), 3)

    return line_image, ((copy_line[0][0][2] + copy_line[1][0][2]) // 2, 600)

def make_points(image, line):
    try:
        # (1차함수로 생각) slope: 기울기, intercept: y절편
        slope, intercept = line

    # 연산이나 함수가 부적절한 형(type)의 객체에 적용될 때 발생함
    except TypeError:
        slope, intercept = 0, 0

    # image.shape[0]: height, image.shape[1]: width
    y1 = int(image.shape[0])
    y2 = int(y1*3.0/5)
    # print(y1, y2) # 720 432
    # print(intercept, slope) # 둘 다 0은 아님

    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    return [[x1, y1, x2, y2]]

def average_slope_intercept(image, lines):
    left_fit    = []
    right_fit   = []
    if lines is None:
        return None
    for line in lines:
        for x1, y1, x2, y2 in line:
            fit = np.polyfit((x1,x2), (y1,y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                left_fit.append((slope, intercept))
            else:
                right_fit.append((slope, intercept))
    left_fit_average  = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)
    left_line  = make_points(image, left_fit_average)
    right_line = make_points(image, right_fit_average)
    averaged_lines = [left_line, right_line]
    return averaged_lines

# cap = cv2.VideoCapture('Test.mp4')

# 비디오 파일 저장하는 코
# w = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# h = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# fps = cap.get(cv2.CAP_PROP_FPS)
# fourcc = cv2.VideoWriter_fourcc(*'DIVX')
# out = cv2.VideoWriter('output2.avi', fourcc, fps, (w, h))

def imageProcessing(frame):
    preRealCoor=(640,600)
    try:
    # cap = cv2.VideoCapture(0)
        # _, frame = cap.read()
        # print(frame)
        #frame = socket_frame_tcp_server.frame
        canny_image = canny(frame)
        cropped_canny = region_of_interest(canny_image)
    #    cv2.imshow("cropped_canny",cropped_canny)

        lines = houghLines(cropped_canny)
        averaged_lines = average_slope_intercept(frame, lines)
        line_image, Real_Coor = display_lines(frame, averaged_lines)
        combo_image = addWeighted(frame, line_image)

        # print(Real_Coor)
        # cv2.imshow("result", combo_image)

        # out.write(combo_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass
        preRealCoor=Real_Coor
        return Real_Coor
    except Exception as e:
        print("LaneDectection Error\n")
        return preRealCoor
# cap.release()
# cv2.destroyAllWindows()
