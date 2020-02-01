"""
elsell 
github.com/elsell

Mosquito Tracker
Jan 2020 

Simple class to facilitate OpenCV
webcam capture, image processing and 
contour detection. 

"""
from settings import *
from PIL import Image
from PIL import ImageTk
import cv2
import imutils
import sys
import tkinter as tki
import time
from guiManager import GuiManager

class MosquitoTracker:
    def __init__(self, webcamId):
        # Used to quit running when the GUI thread decides 
        self.running = True

        self.settings = Settings()
        self.frameView = None

        self.renderedFrame = None

        self.gui = GuiManager(self)        

        self.webCam = cv2.VideoCapture(webcamId)

        # TODO: Load Saved Settings Here

    def __del__(self):
        print("Tracker Shutdown")
        try:
            self.webCam.release()
        except:
            pass
        

    # Main Capture Loop
    def Capture(self):

        while self.running:
            frame = self.CaptureFrame()

            # Iterate through detection areas and find contours
            self.FindContours(frame)
            
            self.SelectFrameView()
            
            if len(self.settings.detectionAreas) > 0:
                frame = self.OutlineContours(self.frameView)

                frame = self.DrawRegionRectangle(self.frameView)

                self.renderedFrame = frame
            else:
                self.renderedFrame = self.frameView
          
            


        self.gui.Close()
        self.webCam.release()


    # Captures and processes a camera frame.
    # returns camFrame
    def CaptureFrame(self):
        # Capture frame from camera
        ret, self.camFrame = self.webCam.read()

        # Apply a blur to the frame
        self.blurredFrame = cv2.GaussianBlur(
            self.camFrame, 
            (self.settings.blurAmount, self.settings.blurAmount),
            0)

        self.blurredFrame = cv2.cvtColor(self.blurredFrame, cv2.COLOR_BGR2GRAY)

        # Threshold & invert the blurred frame
        th, self.thresholdFrame = cv2.threshold(self.blurredFrame, 
            self.settings.lowerThreshold, self.settings.upperThreshold,
            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        return self.thresholdFrame

    # Returns a list of contours given a camera frame
    # Contours are filtered based upon size limits set in settings
    def FindContours(self, camFrame):
        
        # Find contours (shapes) in the thresholded frame 
        contours = cv2.findContours(camFrame, cv2.RETR_LIST, 
            cv2.CHAIN_APPROX_SIMPLE)[-2]

        for area in self.settings.detectionAreas:

            area.contours = []
            for cont in contours:
                if self.settings.smallestSize < cv2.contourArea(cont) < self.settings.largestSize:
                    M = cv2.moments(cont)
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])

                    if area.ax < cX < area.bx and area.ay < cY < area.by:
                        area.contours.append(cont)

    # Given a list of contours, returns the a list of [x, y] coordinates
    # of the center of each contour
    def FindCenters(self, contours):
        contourCenters = []
        
        for cont in contours:
            M = cv2.moments(cont)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            contourCenters.append([cX, cY])

        return contourCenters

    # Given a image frame, a list of contours,
    # outlines contours. Returns the annotated frame.
    def OutlineContours(self, frame):

        for area in self.settings.detectionAreas:
            centerList = self.FindCenters(area.contours)

            for cont, center in zip(area.contours, centerList):
                cv2.drawContours(frame, cont, -1, (0, 255, 0), 2)
                cv2.circle(frame, (center[0], center[1]), 30, (150,150,150), 1)
        
        return frame

    def DrawRegionRectangle(self, frame):
        textScale = 1
        textThickness = 1
        textBaseline = 0
        textFont = cv2.FONT_HERSHEY_PLAIN
        textBGColor = (0,0,0)
        textOffsetX = 10
        textOffsetY = 20

        for area in self.settings.detectionAreas:
            text = area.id
            (text_width, text_height) = cv2.getTextSize(text, textFont, fontScale=textScale, thickness=textThickness)[0]
            textBGCoords = ((area.ax + textOffsetX - 2, area.ay + textOffsetY + 2), (area.ax + textOffsetX + text_width, area.ay + textOffsetY - text_height - 2))
            
            
            cv2.rectangle(frame, (area.ax, area.ay), (area.bx,area.by), (0,0,255),6)
            cv2.rectangle(frame, textBGCoords[0], textBGCoords[1], textBGColor, cv2.FILLED)
            cv2.putText(frame, area.id,(area.ax + 10, area.ay + 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,255,0), 0)
        
        return frame


    def SelectFrameView(self):
        if self.settings.frameView == FRAME_VIEW_UNPROCESSED:
            self.frameView = self.camFrame
        elif self.settings.frameView == FRAME_VIEW_BLURRED:
            self.frameView = self.blurredFrame
        if self.settings.frameView == FRAME_VIEW_THRESHOLDED:
            self.frameView = self.thresholdFrame 


        



            

            


