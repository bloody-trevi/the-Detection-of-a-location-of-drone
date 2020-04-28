import numpy as np
import cv2
import math


def find_circles(img_binary, img_color):
    """


    :param img_binary: threshold를 거친 binary 이미지
    :param img_color: 찾은 원을 표시할 BGR 이미지
    :return: 위치를 표시한 img_color, 찾은 원의 좌표 벡터 sorted_pts
    """
    circles = cv2.HoughCircles(img_binary, cv2.HOUGH_GRADIENT,
                               1, 10, param1=5, param2=10, minRadius=0, maxRadius=0)

    marker_pts = np.zeros((4, 2))
    count = 0
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for c in circles[0, :]:
            center = (c[0], c[1])

            if count == 4:
                break
            marker_pts[count] = center
            count = count + 1

    cx = (marker_pts[0][0] + marker_pts[1][0] + marker_pts[2][0] + marker_pts[3][0]) / 4
    cy = (marker_pts[0][1] + marker_pts[1][1] + marker_pts[2][1] + marker_pts[3][1]) / 4
    angle = []
    for pt in marker_pts:
        angle.append((math.atan2(pt[1] - cy, pt[0] - cx), pt))

    angle = sorted(angle, key=lambda x: x[0])
    sorted_pt2 = np.array([angle[0][1], angle[1][1], angle[2][1], angle[3][1]])

    v = np.zeros((4, 2))
    v[0] = sorted_pt2[1] - sorted_pt2[0]
    v[1] = sorted_pt2[2] - sorted_pt2[1]
    v[2] = sorted_pt2[3] - sorted_pt2[2]
    v[3] = sorted_pt2[0] - sorted_pt2[3]

    a = np.zeros(4)
    a[0] = np.arccos(np.inner(v[0], v[1]) / (np.linalg.norm(v[0]) * np.linalg.norm(v[1])))
    a[1] = np.arccos(np.inner(v[1], v[2]) / (np.linalg.norm(v[1]) * np.linalg.norm(v[2])))
    a[2] = np.arccos(np.inner(v[2], v[3]) / (np.linalg.norm(v[2]) * np.linalg.norm(v[3])))
    a[3] = np.arccos(np.inner(v[3], v[0]) / (np.linalg.norm(v[3]) * np.linalg.norm(v[0])))

    angle_sum = np.sum(a) * 180 / np.pi
    good = True

    if np.linalg.norm(v[1]) / np.linalg.norm(v[0]) > 2:
        good = False
    if np.linalg.norm(v[2]) / np.linalg.norm(v[1]) > 2:
        good = False
    if np.linalg.norm(v[3]) / np.linalg.norm(v[2]) > 2:
        good = False
    if np.linalg.norm(v[0]) / np.linalg.norm(v[3]) > 2:
        good = False

    good = True
    if good is True:
        c = 0
        for pt in sorted_pt2:
            c = c + 1
            text = str(int(angle[c - 1][0] * 57.295))
            img_color = cv2.putText(img_color, text, (int(pt[0]) + 20, int(pt[1])), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
            if c == 1:
                img_color = cv2.circle(img_color, (int(pt[0]), int(pt[1])),
                                       10, (0, 0, 255), -1)  # 마커 꼭지점 표시
            elif c == 2:
                img_color = cv2.circle(img_color, (int(pt[0]), int(pt[1])),
                                       10, (0, 255, 0), -1)  # 마커 꼭지점 표시
            elif c == 3:
                img_color = cv2.circle(img_color, (int(pt[0]), int(pt[1])),
                                       10, (255, 0, 0), -1)  # 마커 꼭지점 표시
            elif c == 4:
                img_color = cv2.circle(img_color, (int(pt[0]), int(pt[1])),
                                       10, (0, 255, 255), -1)  # 마커 꼭지점 표시

    return img_color, sorted_pt2
