import numpy as np
import cv2

#image should be numpy array in RGB with int values in [0,255]
#returns rotated numpy array and transformation matrix
def rotate_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    max_contour = max(contours, key=len)
    rect = cv2.minAreaRect(max_contour)
    box = cv2.boxPoints(rect)

    width = int(rect[1][0])
    height = int(rect[1][1])

    src = box.astype("float32")
    dest = np.array([[width-1, height-1],
                        [0, height-1],
                        [0, 0],
                        [width-1, 0]], dtype="float32")

    Mat = cv2.getPerspectiveTransform(src, dest)
    rotated = cv2.warpPerspective(img, Mat, (width, height))
    return rotated, Mat
