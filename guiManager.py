import cv2
import tkinter
from tkinter import simpledialog
from PIL import ImageTk, Image
import threading
import settings
import sys

class DetectionArea:
    def __init__(self, id):
        self.id = id
        self.ax, self.ay = -1, -1
        self.bx, self.by = -1,-1

        self.contours = []

class GuiManager:
    def __init__(self, tracker):
        self.drawing = False

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
        
        # Create Preview Pane
        self.previewContainer = tkinter.Label(self.mainWindow, text="Loading Preview...", fg="white", bg="black",image=self.tracker.renderedFrame)

        # Register Event Handlers
        self.mainWindow.protocol("WM_DELETE_WINDOW", self._Stop)
        self.mainWindow.bind("<KeyPress>", self.HandleKeyDown)

        self.previewContainer.bind('<Motion>', self.HandleMouseMovePreview)
        self.previewContainer.bind('<Button>', self.HandleMouseClickPreview)
        self.previewContainer.bind('<ButtonRelease>', self.HandleMouseButtonUpPreview)

        # Create Controls for Left Frame
        self.previewContainer.grid(row=0, column=0, columnspan=6, rowspan=12)

        # Create Controls for the Right Frame

        # View Modes
        modesVar = tkinter.IntVar()
        modesVar.set(self.tracker.settings.frameView)

        previewModesFrame = tkinter.LabelFrame(self.mainWindow, text="Preview View Mode")
        previewModesFrame.grid(padx = 15, pady = 15,row=0, column=6, columnspan=6, rowspan=1,sticky=(tkinter.W+tkinter.E))
        tkinter.Radiobutton(previewModesFrame, value = 0, variable=modesVar, indicatoron=False, text = "Unprocessed", command=self.HandleUnprocBtn).pack(expand=True, side=tkinter.LEFT,padx=(0,10))
        tkinter.Radiobutton(previewModesFrame, value = 1, variable=modesVar, indicatoron=False, text = "Blurred", command=self.HandleBlurBtn).pack(expand=True, side=tkinter.LEFT,padx=(0,10))
        tkinter.Radiobutton(previewModesFrame, value = 2, variable=modesVar, indicatoron=False, text = "Thresholded", command=self.HandleThresholdedBtn).pack(expand=True, side=tkinter.LEFT)

        # Selection Tools
        selectionToolsFrame = tkinter.LabelFrame(self.mainWindow, text="Selection Tools")
        selectionToolsFrame.grid(padx = 15, pady = 15, row=2, column=6, columnspan=6, rowspan=1,sticky=(tkinter.W+tkinter.E))
        tkinter.Button(selectionToolsFrame, text = "+ Add Area", command=self.HandleAddAreaBtn).pack(expand=True, side=tkinter.LEFT,padx=(0,10))
        tkinter.Button(selectionToolsFrame, text = "- Undo Add Area", command=self.HandleUndoAreaBtn).pack(expand=True, side=tkinter.LEFT,padx=(0,10))
        tkinter.Button(selectionToolsFrame, text = "Delete All Areas", command=self.HandleDeleteAreasBtn).pack(expand=True, side=tkinter.LEFT,padx=(0,10))

        # Detection Refinement Tools
        detectionToolsFrame = tkinter.LabelFrame(self.mainWindow, text="Detection Tools")
        detectionToolsFrame.grid(padx = 15, pady = 15,row=4, column=6, columnspan=6, rowspan=1,sticky=(tkinter.W+tkinter.E))
        
        # Area Refinement
        tkinter.Label(detectionToolsFrame, text="Smallest Area").grid(row=5, column=6, columnspan=3, rowspan=1)
        tkinter.Label(detectionToolsFrame, text="Largest Area").grid(row=5, column=9, columnspan=3, rowspan=1)
        self.smallestAreaScale = tkinter.Scale(detectionToolsFrame, tickinterval=1500, from_=0, to=3000,command=self.HandleSmallestAreaSlider, orient=tkinter.HORIZONTAL)
        self.smallestAreaScale.grid(row=6, column=6, columnspan=3, rowspan=1)
        self.smallestAreaScale.set(self.tracker.settings.smallestSize)

        self.largestAreaScale = tkinter.Scale(detectionToolsFrame, tickinterval=1500, from_=0, to=3000,command=self.HandleLargestAreaSlider, orient=tkinter.HORIZONTAL)
        self.largestAreaScale.grid(row=6, column=9, columnspan=3, rowspan=1)
        self.largestAreaScale.set(self.tracker.settings.largestSize)

        # Blur Refinement
        tkinter.Label(detectionToolsFrame, text="Blur Amount").grid(row=7, column=6, columnspan=6, rowspan=1)
        
        self.blurLevelScale = tkinter.Scale(detectionToolsFrame, tickinterval=50, from_=0, to=100,command=self.HandleBlurSlider, orient=tkinter.HORIZONTAL)
        self.blurLevelScale.grid(row=8, column=6, columnspan=6, rowspan=1)
        self.blurLevelScale.set(self.tracker.settings.blurAmount)

    
        self.UpdatePreviewFrame()
        self.mainWindow.mainloop()

    def UpdatePreviewFrame(self):
        try:
            rgbFrame = cv2.cvtColor(self.tracker.renderedFrame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(rgbFrame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.previewContainer.imgtk = imgtk
            self.previewContainer.configure(image=imgtk)
        except:
            pass

        self.previewContainer.after(25, self.UpdatePreviewFrame)

    def HandleBlurSlider(self, value):
        value = int(value)
        self.tracker.settings.SetBlurAmount(value)

    def HandleSmallestAreaSlider(self, value):
        value = int(value)
        self.tracker.settings.SetSmallestSize(value)

        if value >= self.tracker.settings.largestSize:
            self.largestAreaScale.set(value)

    def HandleLargestAreaSlider(self, value):
        value = int(value)
        self.tracker.settings.SetLargestSize(value)

        if value <= self.tracker.settings.smallestSize:
            self.smallestAreaScale.set(value)

    def HandleDeleteAreasBtn(self):
        self.tracker.settings.detectionAreas = []

    def HandleUndoAreaBtn(self):
        if len(self.tracker.settings.detectionAreas) > 0:
            self.tracker.settings.detectionAreas.pop()

    def HandleAddAreaBtn(self):
        id = simpledialog.askstring(title="Add Detection Area", prompt="Area Name:")
        self.tracker.settings.detectionAreas.append(DetectionArea(id))

    def HandleUnprocBtn(self):
         self.tracker.settings.frameView = settings.FRAME_VIEW_UNPROCESSED

    def HandleBlurBtn(self):
        self.tracker.settings.frameView = settings.FRAME_VIEW_BLURRED

    def HandleThresholdedBtn(self):
        self.tracker.settings.frameView = settings.FRAME_VIEW_THRESHOLDED

    def HandleMouseMovePreview(self, event):
        if self.drawing:
            self.tracker.settings.detectionAreas[-1].bx = event.x
            self.tracker.settings.detectionAreas[-1].by = event.y

    def HandleMouseClickPreview(self, event):
        if len(self.tracker.settings.detectionAreas) < 1:
            self.HandleAddAreaBtn()
            return

        self.tracker.settings.detectionAreas[-1].ax = event.x
        self.tracker.settings.detectionAreas[-1].ay = event.y
        self.drawing = True

    def HandleMouseButtonUpPreview(self, event):
        if self.drawing == True:
            self.drawing = False
            self.tracker.settings.detectionAreas[-1].bx = event.x
            self.tracker.settings.detectionAreas[-1].by = event.y            



    def HandleKeyDown(self, e):
        if e.keycode == 27:
            self._Stop()
