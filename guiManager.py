import cv2
import tkinter
from PIL import ImageTk, Image
import threading
from settings import *
import sys

class GuiManager:
    def __init__(self, tracker):
        self.drawing = False
        self.ax,self.ay = -1, -1
        self.bx, self.by = -1,-1
        self.tracker = tracker

        self.mainWindowThread = threading.Thread(target=self._CreateMainWindow)
        self.mainWindowThread.start()

        
    def Close(self):
        self.mainWindow.quit()
        self.mainWindowThread.join()

    def _Stop(self):
        self.tracker.running = False

    # Draw main tkinter window (based on a 12 column x 12 row grid)
    def _CreateMainWindow(self):
        self.mainWindow = tkinter.Tk()
        self.mainWindow.title(self.tracker.settings.mainWindowText)

        # Register Event Handlers
        self.mainWindow.protocol("WM_DELETE_WINDOW", self._Stop)
        self.mainWindow.bind("<KeyPress>", self.HandleKeyDown)

        # Create Controls for Left Frame
        self.previewContainer = tkinter.Label(self.mainWindow, text="Preview", fg="white", bg="black",image=self.tracker.frameView)
        self.previewContainer.grid(row=0, column=0, columnspan=6, rowspan=12)

        # Create Controls for the Right Frame
        tkinter.Label(self.mainWindow, text="Preview View Mode").grid(row=0, column=6, columnspan=6, rowspan=1)
        tkinter.Button(self.mainWindow, text = "Unprocessed", command=self.HandleUnprocBtn).grid(row=1, column=6, columnspan=2, rowspan=1)
        tkinter.Button(self.mainWindow, text = "Blurred", command=self.HandleBlurBtn).grid(row=1, column=8, columnspan=2, rowspan=1)
        tkinter.Button(self.mainWindow, text = "Thresholded", command=self.HandleThresholdedBtn).grid(row=1, column=10, columnspan=2, rowspan=1)

        self.UpdatePreviewFrame()
        self.mainWindow.mainloop()

    def UpdatePreviewFrame(self):
        try:
            rgbFrame = cv2.cvtColor(self.tracker.frameView, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(rgbFrame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.previewContainer.imgtk = imgtk
            self.previewContainer.configure(image=imgtk)
        except:
            pass

        self.previewContainer.after(1, self.UpdatePreviewFrame)


    def HandleUnprocBtn(self):
        self.tracker.frameView = self.tracker.settings.frameView = FRAME_VIEW_UNPROCESSED

    def HandleBlurBtn(self):
        self.tracker.frameView = self.tracker.settings.frameView = FRAME_VIEW_BLURRED

    def HandleThresholdedBtn(self):
        self.tracker.frameView = self.tracker.settings.frameView = FRAME_VIEW_THRESHOLDED

    def MouseRectHandler(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ax, self.ay = x,y
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing == True:
                self.bx, self.by = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            self.bx, self.by = x, y
            self.drawing = False

        cv2.imshow(self.tracker.settings.mainWindowText, self.tracker.frameView)

    def HandleKeyDown(self, e):
        if e.keycode == 27:
            self._Stop()
