from oCam.oCam_class import *
import cv2
import time
import numpy as np
import math


if __name__ == '__main__':
    cap = myCamCapture()
    if cap.GetConnectedCamNumber() == 0:
        print("oCam not Found...")
    else:
        print(cap.CamGetDeviceInfo(0))
        # print (cap.CamGetDeviceList())
        cap.CamOpen(DevNo=0, Resolution=(960, 1280), FramePerSec=30.0, BytePerPixel=1)

        start_time = time.time()
        cap.CamStart()

        cap.CamSetCtrl(myCamCapture.CTRL_EXPOSURE, -11)
        cap.CamSetCtrl(myCamCapture.CTRL_GAIN, 255)
        count = 0

        data = np.array([[0, 0, 0]])

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

            gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)  # gray

            cv2.imshow('gray test', gray)

            key = cv2.waitKey(1)
            if key == 27:  # Quit with ESC
                break

        # saving the locations
        # np.save('data', data)
        end_time = time.time()

        print('FPS= ', count / (end_time - start_time))
        cv2.destroyAllWindows()
        cap.CamStop()
        cap.CamClose()