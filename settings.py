"""
elsell
github.com/elsell

Simple settings class to handle storage and
modification of settings. 
Jan 2020

Persistance should be added. 

""" 
FRAME_VIEW_UNPROCESSED = 0
FRAME_VIEW_BLURRED     = 1
FRAME_VIEW_THRESHOLDED = 2

class Settings:
    def __init__(self):
        # Determines which version of the frame is displayed (unprocessed, blurred, etc)
        self.frameView = 0

        self.mainWindowText = "Preview"
        self.controlsWindowText = "Controls"
        self.blurAmount = 25

        self.smallestSize = 30
        self.largestSize  = 3000

        self.lowerThreshold = 100
        self.upperThreshold = 255

    def SetBlurAmount(self, blurAmount):
        if blurAmount % 2 == 0:
            blurAmount = blurAmount + 1
        self.blurAmount = blurAmount

    def SetSmallestSize(self, smallestSize):
        self.smallestSize = smallestSize

    def SetLargestSize(self, largestSize):
        self.largestSize = largestSize

    def SetLowerThreshold(self, lowerThreshold):
        self.lowerThreshold = lowerThreshold

    def SetUpperThreshold(self, upperThreshold):
        self.upperThreshold = upperThreshold

    def SetFrameView(self, frameView):
        self.frameView = frameView