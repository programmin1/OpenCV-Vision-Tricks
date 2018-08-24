#!/usr/bin/env python3

'''
VideoCapture sample showcasing  some features of the Video4Linux2 backend

Sample shows how VideoCapture class can be used to control parameters
of a webcam such as focus or framerate.
Also the sample provides an example how to access raw images delivered
by the hardware to get a grayscale image in a very efficient fashion.

Keys:
    ESC    - exit
    g      - toggle optimized grayscale conversion

'''

# Python 2/3 compatibility
from __future__ import print_function
import math
import numpy

import cv2

def decode_fourcc(v):
    v = int(v)
    return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])

font = cv2.FONT_HERSHEY_SIMPLEX
color = (0, 255, 0)

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTOFOCUS, False)  # Known bug: https://github.com/opencv/opencv/pull/5474

cv2.namedWindow("Video")

convert_rgb = True
fps = 30 #int(cap.get(cv2.CAP_PROP_FPS))
focus = int(min(cap.get(cv2.CAP_PROP_FOCUS) * 100, 2**31-1))  # ceil focus to C_LONG as Python3 int can go to +inf

cv2.createTrackbar("FPS", "Video", fps, 10, lambda v: cap.set(cv2.CAP_PROP_FPS, v))
cv2.createTrackbar("Focus", "Video", focus, 100, lambda v: cap.set(cv2.CAP_PROP_FOCUS, v / 100))

cap.set(cv2.CAP_PROP_FPS, 50)
pts = []
while True:
    status, img = cap.read()

    fourcc = decode_fourcc(cap.get(cv2.CAP_PROP_FOURCC))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if not bool(cap.get(cv2.CAP_PROP_CONVERT_RGB)):
        if fourcc == "MJPG":
            img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
        elif fourcc == "YUYV":
            img = cv2.cvtColor(img, cv2.COLOR_YUV2GRAY_YUYV)
        else:
            print("unsupported format")
            break

    #Commence experiment!!!!!!!!!!!!!!!
    #while True:
    #    print( eval(input('>'))) #Here you can test what object is.. dir(img[0]), img[0].size etc.
    # Note that it's BGR as you can see.
    #for row in img:
    #    for pixel in row:
    #        pixel[0] = 255
    #        pixel[1] = 255
    #for row in img: SLOOW
        #for pixel in row:
            #relativeRed = 0
            ##The pixel values are actual byte types apparently, so must sum int() to get normal Python int:
            #sumpx = int(pixel[0])+int(pixel[1])+int(pixel[2])
            #if int(sumpx) > 740 :# bright, maybe laser
                ##print('laser?')
                #relativeRed = pixel[2] / sumpx
                #relativeRed = math.floor( relativeRed *255 )
                #pixel[0] = 0#relativeRed
                #pixel[1] = 0#relativeRed
                #pixel[2] = 0#relativeRed
    
    b,g,r = cv2.split(img)
    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #ret,gray = cv2.threshold(gray,127,255,0)
    #img = gray replace grey with r her for most red:
    #TODO try blur? http://www.pyimagesearch.com/2014/09/29/finding-brightest-spot-image-using-python-opencv/
    
    #Subtract red from green or other channel, so white doesn't set it off.
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc( cv2.subtract(r, g) ) #cv2.minMaxLoc(r)
    
    cv2.circle(img, maxLoc, 10, (250,250,250))
    
    cv2.putText(img, "Position (x,y) = (%d,%d)" % (maxLoc[0], maxLoc[1]), (15, 40), font, 1.0, color)
    x = maxLoc[0]
    if x < 1:
        x = 0.1 #no exception crash
    distance = 1698381938.85711*x**-2.9127182537

    cv2.putText(img, "Approximate distance: %d cm" % (distance,), (15, 80), font, 1.0, color)
    cv2.imshow("Video", img )#numpy.subtract(gray, r))#img)

    k = cv2.waitKey(1)

    if k == 27:
        break
    elif k == ord('c'):
        pts = []
    elif k == ord('g'):
        convert_rgb = not convert_rgb
        cap.set(cv2.CAP_PROP_CONVERT_RGB, convert_rgb)
