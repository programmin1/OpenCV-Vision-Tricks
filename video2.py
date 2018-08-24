#!/usr/bin/env python3

'''
VideoCapture sample showcasing  some features of the Video4Linux2 backend

This now combines two identical webcam images!

Keys:
    ESC    - exit
    s - show mode
    l - show left
    r = show right
    3 - 3d-capture
    
Be sure left looks left, right looks right or may be all messed up.
Rightmost things should show more in the rightmost camera.
'''

# Python 2/3 compatibility
from __future__ import print_function
from __future__ import division
import math
import numpy
from time import sleep
import os

import cv2

class VideoModule:
    
    #Functions allowing live setting 
    def setWin( self, val ):
        self.window_size = val
    def setDisp( self, val ):
        self.min_disp = val
    def setSpeckle( self, val ):
        self.speckleRange = val
    def setWinSpeckle( self, val ):
        self.speckleWindowSize = val
    def setBlockSize( self, val ):
        self.blockSize = val
    
    @staticmethod    
    def write_ply(fn, verts, colors):
        """ Just like the one in the opencv demo. As a static method the first arg is not "self". """
        ply_header = '''ply
format ascii 1.0
element vertex %(vert_num)d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
'''
        verts = verts.reshape(-1, 3)
        colors = colors.reshape(-1, 3)
        verts = numpy.hstack([verts, colors])
        with open(fn, 'wb') as f:
            f.write((ply_header % dict(vert_num=len(verts))).encode('utf-8'))
            numpy.savetxt(f, verts, fmt='%f %f %f %d %d %d ')
            
    def __init__(self):
        self.showMode = False
        self.showImg = ''
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (0, 255, 0)

        cap = cv2.VideoCapture(1) #second
        cap2 = cv2.VideoCapture(2) #third webcam connected.
        cap.set(cv2.CAP_PROP_AUTOFOCUS, False)  # Known bug: https://github.com/opencv/opencv/pull/5474
        cap2.set(cv2.CAP_PROP_AUTOFOCUS, False)

        cv2.namedWindow("Video", cv2.WINDOW_NORMAL) #resizable window
        cv2.resizeWindow("Video", 800, 800)

        convert_rgb = True
        fps = 30 #int(cap.get(cv2.CAP_PROP_FPS))
        focus = int(min(cap.get(cv2.CAP_PROP_FOCUS) * 100, 2**31-1))  # ceil focus to C_LONG as Python3 int can go to +inf
        
        self.speckleWindowSize = 100
        self.speckleRange = 32
        self.window_size = 1
        self.min_disp = 16
        self.blockSize = 11
        num_disp = 160-self.min_disp

        cv2.createTrackbar("WindowSize", "Video", self.window_size, 100, self.setWin)
        cv2.createTrackbar("MinDisp", "Video", num_disp, 100, self.setDisp )
        cv2.createTrackbar("SpeckleWindowSize", "Video", num_disp, 1000, self.setWinSpeckle )
        cv2.createTrackbar("SpeckleRange", "Video", num_disp, 320, self.setSpeckle )
        cv2.createTrackbar("BlockSize", "Video", self.blockSize, 20, self.setBlockSize )

        cap.set(cv2.CAP_PROP_FPS, 20)
        cap2.set(cv2.CAP_PROP_FPS, 20)
        pts = []
        exiting = False
        while not exiting:
            status, imgL = cap.read()
            status, imgR = cap2.read()
            if len(self.showImg):
                if self.showImg == 'l':
                    cv2.imshow("Video", imgL)
                elif self.showImg == 'r':
                    cv2.imshow("Video", imgR)
                    
            elif self.showMode:
                cv2.imshow("Video", cv2.subtract( imgL, imgR ) )
            else:
                
                stereo = cv2.StereoSGBM_create(minDisparity = self.min_disp,
                    numDisparities = num_disp,
                    blockSize = self.blockSize,
                    P1 = 8*3*self.window_size**2,
                    P2 = 32*3*self.window_size**2,
                    disp12MaxDiff = 1,
                    uniquenessRatio = 10,
                    speckleWindowSize = self.speckleWindowSize,
                    speckleRange = self.speckleRange
                )
                disp = stereo.compute(imgL, imgR).astype(numpy.float32) / 16.0

                cv2.imshow("Video", (disp-self.min_disp)/num_disp )
                #cv2.imshow("Video", cv2.subtract( imgL, imgR ) )

            k = cv2.waitKey(1)

            if k == 27:
                exiting = True #See loop top
            elif k == ord('s'):
                self.showMode = not self.showMode
                self.showImg = ''
            elif k == ord('l'):
                self.showImg = 'l'
            elif k == ord('r'):
                self.showImg = 'r'
            elif k == ord('3'):
                print('generating 3d point cloud...',)
                h, w = imgL.shape[:2]
                f = 0.8*w                          # guess for focal length
                Q = numpy.float32([[1, 0, 0, -0.5*w],
                                [0,-1, 0,  0.5*h], # turn points 180 deg around x-axis,
                                [0, 0, 0,     -f], # so that y-axis looks up
                                [0, 0, 1,      0]])
                points = cv2.reprojectImageTo3D(disp, Q)
                colors = cv2.cvtColor(imgL, cv2.COLOR_BGR2RGB)
                mask = disp > disp.min()
                out_points = points[mask]
                out_colors = colors[mask]
                out_fn = 'out.ply'
                self.write_ply('out.ply', out_points, out_colors)
                os.system('xdg-open out.ply')
                print('%s saved' % 'out.ply')


VideoModule()
