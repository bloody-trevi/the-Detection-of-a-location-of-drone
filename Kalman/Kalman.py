import numpy as np
from .Kalman_Params_class import KalmanParam


def Kalman(xm, ym, param):
    """
    영상 처리로 얻은 x, y 값으로 칼만 필터를 거쳐 추정한 x, y값을 구한다.

    :param xm: 영상 처리로 얻은 위치의 x 좌표
    :param ym: 영상 처리로 얻은 위치의 y 좌표
    :param param: 칼만 필터 계산에 필요한 행렬들
    :return: 추정 위치 (x, y), 추정 속도(vx, vy), 갱신된 param
    """

    # 시스템 모델 행렬
    A, H, Q, R = param.get_mats()
    x = param.get_x()
    P = param.get_P()

    #
    x_p = np.dot(A, x)
    P_p = A * P * np.transpose(A) + Q

    # 칼만 이득
    K_1 = np.dot(P_p, np.transpose(H))
    K_2 = np.linalg.inv(H.dot(np.dot(P_p, np.transpose(H))) + R) # inv(H*P_p*H' + R)
    K = np.dot(K_1, K_2)

    #
    z = np.transpose(np.array([xm, ym]))
    x_ = z - np.dot(H, x_p)
    x = x_p + np.dot(K, x_)
    P = P_p - K.dot(np.dot(H, P_p))

    # [위치 x, 속도 x, 위치 y, 속도 y]
    xh = x[0]   # 위치 x
    vx = x[1]   # 속도 x
    yh = x[2]   # 위치 y
    vy = x[3]   # 속도 y
    param.set_x_P(x, P)
    return xh, yh, vx, vy, param
