import cv2

class GuiManager:
    def __init__(self, tracker):
        self.drawing = False
        self.ax,self.ay = -1, -1
        self.bx, self.by = -1,-1
        self.tracker = tracker
        print(tracker.settings.mainWindowText)


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