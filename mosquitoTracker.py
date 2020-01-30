"""
elsell 
github.com/elsell

Mosquito Tracker
Jan 2020 

Simple class to facilitate OpenCV
webcam capture, image processing and 
contour detection. 

"""
from settings import Settings
from PIL import Image
from PIL import ImageTk
import cv2
import imutils
import tkinter as tki
from guiManager import GuiManager

class MosquitoTracker:
    def __init__(self, webcamId):
        self.settings = Settings()
        self.frameView = None

        self.gui = GuiManager(self)
        self.InitWindow()
        

        self.webCam = cv2.VideoCapture(webcamId)

        # TODO: Load Saved Settings Here

    def __del__(self):
        try:
            self.webCam.release()
        except:
            pass
        cv2.destroyAllWindows()
        

    def InitWindow(self):
        cv2.setMouseCallback(self.settings.mainWindowText,self.gui.MouseRectHandler)

    def ShowFrame(self):
        cv2.imshow(self.settings.mainWindowText, self.frameView)


    def Capture(self):
        cv2.namedWindow(self.settings.mainWindowText)
        cv2.namedWindow(self.settings.controlsWindowText)
        self.InitWindow()

        while True:
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break       

            self.AddControls()

            frame = self.CaptureFrame()

            self.SelectFrameView()

            contours = self.FindContours(frame)

            frame = self.OutlineContours(self.frameView, contours)

            frame = self.DrawRegionRectangle(self.frameView)

            self.ShowFrame()
            # if self.panel is None:
            #     self.panel = tki.Label(self.mainWindow,text=self.settings.mainWindowText)
            #     self.panel.image = img
            #     self.panel.pack(side="left", padx = 10, pady = 10)
            # else:
            #     self.panel.configure(image=img)
            #     self.panel.image = img

            # self.panel.pack()
            # self.mainWindow.mainloop()

        

    def AddControls(self):
        cv2.createTrackbar('BLUR', "Controls", self.settings.blurAmount, 150, self.settings.SetBlurAmount)
        cv2.createTrackbar('Smallest', "Controls", self.settings.smallestSize, 200, self.settings.SetSmallestSize)
        cv2.createTrackbar('Largest', "Controls", self.settings.largestSize, 4000, self.settings.SetLargestSize)
        cv2.createTrackbar('Lower Threshold', "Controls", self.settings.lowerThreshold, 255, self.settings.SetLowerThreshold)
        cv2.createTrackbar('Upper Threshold', "Controls", self.settings.upperThreshold, 255, self.settings.SetUpperThreshold)
        cv2.createTrackbar('Frame View', "Controls", self.settings.frameView, 2, self.settings.SetFrameView)

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

        validContours = []

        for cont in contours:
            if self.settings.smallestSize < cv2.contourArea(cont) < self.settings.largestSize:
                M = cv2.moments(cont)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                if self.gui.ax < cX < self.gui.bx and self.gui.ay < cY < self.gui.by:
                    validContours.append(cont)

        return validContours

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
    def OutlineContours(self, frame, contours):
        centerList = self.FindCenters(contours)

        for cont, center in zip(contours, centerList):
            cv2.drawContours(frame, cont, -1, (0, 255, 0), 2)
            cv2.circle(frame, (center[0], center[1]), 30, (150,150,150), 1)
        
        return frame

    def DrawRegionRectangle(self, frame):
        cv2.rectangle(frame, (self.gui.ax, self.gui.ay), (self.gui.bx,self.gui.by), (0,0,255),6)
        return frame


    def SelectFrameView(self):
        if self.settings.frameView == 0:
            self.frameView = self.camFrame
        elif self.settings.frameView == 1:
            self.frameView = self.blurredFrame
        if self.settings.frameView == 2:
            self.frameView = self.thresholdFrame 


        



            

            


