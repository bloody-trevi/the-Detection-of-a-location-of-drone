import platform
import ctypes
import numpy as np


class myCamCapture():
    """
        oCam 1CGN-U-T 카메라를 열어 영상을 불러오는 클래스.
    """

    CTRL_BRIGHTNESS = ctypes.c_int(1)
    CTRL_CONTRAST = ctypes.c_int(2)
    CTRL_HUE = ctypes.c_int(3)
    CTRL_SATURATION = ctypes.c_int(4)
    CTRL_EXPOSURE = ctypes.c_int(5)
    CTRL_GAIN = ctypes.c_int(6)
    CTRL_WB_BLUE = ctypes.c_int(7)
    CTRL_WB_RED = ctypes.c_int(8)

    def __init__(self):
        try:
            if platform.architecture()[0] == '64bit':
                self.mydll = ctypes.cdll.LoadLibrary("./libCamCap-amd64.dll")
                # self.mydll = ctypes.CDLL(".\\libCamCap-amd64.dll")
            else:
                self.mydll = ctypes.cdll.LoadLibrary(".\\libCamCap-x86.dll")
            self.mydll.CamGetDeviceInfo.restype = ctypes.c_char_p
            self.mydll.CamOpen.restype = ctypes.POINTER(ctypes.c_int)
        except WindowsError as Error:
            print(Error)
            raise Exception('libCamCap-amd64.dll or libCamCap-x86.dll not found')

        self.cam = None
        self.resolution = (0, 0)

    def GetConnectedCamNumber(self):
        """
        연결된 캠의 번호를 반환한다.

        :return: 연결된 캠의 번호를 int로 반환
        """
        return int(self.mydll.GetConnectedCamNumber())

    def CamGetDeviceInfo(self, devno):
        """
        디바이스 번호에 해당하는 디바이스의 정보를 출력한다.

        :param devno: 디바이스 번호
        :return: USB 포트 위치, 시리얼 번호, 제품 이름, 펌웨어 버전을 반환
        """
        info = dict()
        for idx, param in enumerate(('USB_Port', 'SerialNo', 'oCamName', 'FWVersion')):
            info[param] = self.mydll.CamGetDeviceInfo(int(devno), idx + 1)
        return info

    def CamGetDeviceList(self):
        """
        디바이스 번호를 이용해 얻은 정보들을 리스트에 저장해 반환한다.

        :return: 디바이스들의 리스트를 반환
        """
        CamCount = self.GetConnectedCamNumber()
        DeviceList = list()
        for idx in range(CamCount):
            dev = self.CamGetDeviceInfo(idx)
            dev['devno'] = idx
            DeviceList.append(dev)
        return DeviceList

    def CamStart(self):
        """
        카메라가 영상을 받을 수 있게 준비한다.

        :return: 열려 있는 카메라가 없으면 None
        """
        if self.cam == None: return
        ret = self.mydll.CamStart(self.cam)

    def CamGetImage(self):
        """
        열려 있는 카메라에서 이미지를 받는다.

        :return: 열려 있는 카메라가 없으면 None. 이미지를 받았다면 (True, 받은 이미지), 읽지 못했다면 (False, None)
        """
        if self.cam == None: return 0, None
        ret = self.mydll.CamGetImage(self.cam, ctypes.c_char_p(self.bayer.ctypes.data))
        if ret == 1:
            return True, self.bayer
        else:
            return False, None

    def CamStop(self):
        """
        카메라를 정지 시킨다.

        :return: 열려 있는 카메라가 없으면 None
        """
        if self.cam == None: return
        ret = self.mydll.CamStop(self.cam)

    def CamClose(self):
        """
        열었던 카메라를 닫는다. 닫은 카메라는 None으로 초기화한다.

        :return: 열려 있는 카메라가 없으면 None
        """
        if self.cam == None: return
        ret = self.mydll.CamClose(ctypes.byref(self.cam))
        self.cam = None

    def CamGetCtrl(self, ctrl):
        """
        카메라 설정을 읽어 온다.

        :param ctrl: 컨트롤
        :return:
        """
        if self.cam == None: return
        val = ctypes.c_int()
        ret = self.mydll.CamGetCtrl(self.cam, ctrl, ctypes.byref(val))
        return val.value

    def CamSetCtrl(self, ctrl, value):
        if self.cam == None: return
        val = ctypes.c_int()
        val.value = value
        ret = self.mydll.CamSetCtrl(self.cam, ctrl, val)

    def CamGetCtrlRange(self, ctrl):
        if self.cam == None: return
        val_min = ctypes.c_int()
        val_max = ctypes.c_int()
        ret = self.mydll.CamGetCtrlRange(self.cam, ctrl, ctypes.byref(val_min), ctypes.byref(val_max))
        return val_min.value, val_max.value

    def CamOpen(self, **options):
        DevNo = options.get('DevNo')
        FramePerSec = options.get('FramePerSec')
        Resolution = options.get('Resolution')
        BytePerPixel = options.get('BytePerPixel')

        try:
            devno = DevNo
            (h, w) = Resolution
            pixelsize = BytePerPixel
            fps = FramePerSec
            self.resolution = (w, h)
            self.cam = self.mydll.CamOpen(ctypes.c_int(devno), ctypes.c_int(w), ctypes.c_int(h), ctypes.c_double(fps),
                                          0, 0)
            self.bayer = np.zeros((h, w, pixelsize), dtype=np.uint8)
            return True
        except WindowsError:
            return False


CTRL_PARAM = {
    'Brightness': myCamCapture.CTRL_BRIGHTNESS,
    'Contrast': myCamCapture.CTRL_CONTRAST,
    'Hue': myCamCapture.CTRL_HUE,
    'Saturation': myCamCapture.CTRL_SATURATION,
    'Exposure': myCamCapture.CTRL_EXPOSURE,
    'Gain': myCamCapture.CTRL_GAIN,
    'WB Blue': myCamCapture.CTRL_WB_BLUE,
    'WB Red': myCamCapture.CTRL_WB_RED
}
