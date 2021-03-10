# Author: Yash Dalmia
# Date: March 10 2021
# -------------------
# This program finds the rotated rectangle that bounds the inputted image. 
# It assumes that everything outside the area of interest is black. It then
# crops out everything but the rotated rectangle, and writes the newly-
# cropped image to a file. 

import cv2 as cv
import numpy as np

def get_non_black_bounding_rect(img):
    # get the indices of the non-black pixels, black is (0,0,0) in BGR
    non_black = np.argwhere(img > 0)  
    # find the top and bottom-most pixels (arg where sorts by 'row' already)
    top, bottom  = non_black[0], non_black[-1]
    # find left and right-most pixels
    sorted_y = non_black[non_black[:,1].argsort()] # sort by column
    left, right = sorted_y[0], sorted_y[-1]
    # make bounding rectangle
    points = np.array([top, bottom, left, right])
    points[:, [1, 0]] = points[:, [0, 1]] # swap bc numpy does (x,y) but opencv (y,x)
    rect = cv.minAreaRect(points)
    return rect

def get_sub_img(rect, src):
    # get center, size, and angle from rect
    center, size, theta = rect
    # convert to int 
    center, size = tuple(map(int, center)), tuple(map(int, size))
    # get rotation matrix for rectangle
    M = cv.getRotationMatrix2D(center, theta, 1)
    # perform rotation on src image
    dst = cv.warpAffine(src, M, src.shape[:2])
    # crop the resulting image
    out = cv.getRectSubPix(dst, size, center)
    return out

# read in img
img = cv.imread("data/sample.TIF")
# do the processing in gray scale to speed up
gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# get rotated bounding rectangle for non_black portion
rect = get_non_black_bounding_rect(gray_img)
# crop the rotated rectangle out of the original img 
cropped = get_sub_img(rect, img)
# write the img
cv.imwrite("data/processed_sample.TIF", cropped)
