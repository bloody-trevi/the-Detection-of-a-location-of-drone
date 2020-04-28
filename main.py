from oCam.oCam_class import *
from hough_circle_transform.Find_Circles import find_circles
from Kalman.Kalman import *
from Kalman.Kalman_Params_class import *
import cv2
import time
import numpy as np


def cam_params():
    """
    카메라 내부 파라미터를 캘리브레이션 프로그램을 이용해 구한 값으로 설정한다.
    마커는 한 변이 187.0mm 인 정사각형으로 가정한다.
    또한 마커의 꼭짓점 저장 순서는
    1 2
    3 4
    로 저장된다.

    참고: https://darkpgmr.tistory.com/32

    :return: 마커 꼭짓점들의 실제 3D 좌표 벡터, camera matrix, distortion coefficient vector
    """
    cameraMtx = np.array([[818.922, 0, 308.576], [0, 818.100, 235.557], [0, 0, 1]])
    distCoff = np.array([ -0.485001, 0.271373, 0.003090, 0.002643])

    # 마커 사이즈. 단위는 [mm]
    marker_width = 187.0  # 174.0
    marker_height = 187.0
    '''
    1 2
    4 3
    '''
    object_points = np.array([[-marker_width / 2, -marker_height / 2, 0], [marker_width / 2, -marker_height / 2, 0],
                              [marker_width / 2, marker_height / 2, 0], [-marker_width / 2, marker_height / 2, 0]])
    return object_points, cameraMtx, distCoff


if __name__ == '__main__':

    # 카메라 내부 파라미터 저장
    object_points, cameraMtx, distCoff = cam_params()

    cap = myCamCapture()
    if cap.GetConnectedCamNumber() == 0:
        print("oCam not Found...")
    else:
        print(cap.CamGetDeviceInfo(0))
        # print (cap.CamGetDeviceList())
        cap.CamOpen(DevNo=0, Resolution=(480, 640), FramePerSec=30.0, BytePerPixel=1)

        start_time = time.time()
        cap.CamStart()

        cap.CamSetCtrl(myCamCapture.CTRL_EXPOSURE, -11)
        cap.CamSetCtrl(myCamCapture.CTRL_GAIN, 255)
        count = 0

        # 좌표 데이터 저장용
        # data = np.array([[0, 0, 0]])

        # 캡처할 이미지 인덱싱
        img_counter = 0

        # Kalman param
        dt = 1
        A = np.array([[1, dt, 0, 0], [0, 1, 0, 0], [0, 0, 1, dt], [0, 0, 0, 1]])
        H = np.array([[1, 0, 0, 0], [0, 0, 1, 0]])
        Q = np.eye(4, k=0, dtype=float)
        R = np.array([[50, 0], [0, 50]])
        x = np.transpose(np.array([0, 0, 0, 0]))
        P = 100 * np.eye(4, k=0, dtype=int)
        param = KalmanParam(A, H, Q, R, x, P)
        Kalman_params = [param, param, param, param]

        while True:
            try:
                ret, frame = cap.CamGetImage()  # frame: Gray
            except:
                print('error')
            if ret is False:
                continue

            count += 1
            # -----------------------------------#
            color = cv2.cvtColor(frame, cv2.COLOR_BAYER_GB2BGR)  # BGR
            # 이미지 밝기 낮추기, b의 크기에 따라 변화(최대 255)
            b = 50
            M = np.ones(color.shape, dtype="uint8") * b
            color = cv2.subtract(color, M)

            # ---------- 알고리즘 추가 ---------- #
            # gray
            gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)

            # blur
            img_blur = cv2.GaussianBlur(gray, (5, 5), 0)

            # threshold, binary
            _, binary = cv2.threshold(img_blur, 25, 255, cv2.THRESH_BINARY)

            # Morphology
            kernel = np.ones((4, 4), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

            # find circles
            color, sorted_pt2 = find_circles(binary, color)

            # Kalman filter
            filtered_pts = np.zeros((4, 2))
            for i in range(0, sorted_pt2.size - 1):
                x_m = sorted_pt2[i][0]
                y_m = sorted_pt2[i][1]
                x_h, y_h, param = Kalman(x_m, y_m, Kalman_params[i])
                Kalman_params[i] = param
                filtered_pts[i, :] = np.array([x_h, y_h])

            # print the location
            retP, rvec, tvec = cv2.solvePnP(object_points, filtered_pts, cameraMtx, distCoff)
            text = 'Location: [' + \
                   str(int(tvec[0][0])) + ', ' + \
                   str(int(tvec[1][0])) + ', ' + \
                   str(int(tvec[2][0])) + ']'
            color = cv2.putText(color, text, (20, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

            # test
            cv2.imshow('test', color)
            key = cv2.waitKey(1)
            if key == 27:
                # Quit with ESC
                break
            elif key % 256 == 32:
                # Capture with SPACE
                img_name = "circle_frame_{}.png".format(img_counter)
                cv2.imwrite(img_name, color)
                print("{} written!".format(img_name))
                img_counter += 1

        # saving the locations
        # np.save('data', data)
        end_time = time.time()

        print('FPS= ', count / (end_time - start_time))
        cv2.destroyAllWindows()
        cap.CamStop()
        cap.CamClose()
