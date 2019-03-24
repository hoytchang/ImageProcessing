import wx

ThumbMaxSize = 240

# Define File Drop Target class
class FileDropTarget(wx.FileDropTarget):
    """ This object implements Drop Target functionality for Files """
    def __init__(self, obj, imageCtrl, frame):
        """ Initialize the Drop Target, passing in the Object Reference to
          indicate what should receive the dropped files """
        # Initialize the wxFileDropTarget Object
        wx.FileDropTarget.__init__(self)
        # Store the Object Reference for dropped files
        self.obj = obj
        self.imageCtrl = imageCtrl
        self.frame = frame

    def OnDropFiles(self, x, y, filenames):
        # display filename to gui
        self.obj.Clear()
        file = filenames[0]
        self.obj.WriteText(file)
        
        # read in image file
        img = wx.Image(file, wx.BITMAP_TYPE_ANY)

        # scale down image into a thumbnail
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = ThumbMaxSize
            NewH = ThumbMaxSize * H / W
        else:
            NewH = ThumbMaxSize
            NewW = ThumbMaxSize * W / H
        img = img.Scale(NewW,NewH)

        # assign image to image control
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.frame.Refresh()

        return True

class MainWindow(wx.Frame):
    """ This window displays the GUI Widgets. """
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent, wx.ID_ANY, title, size = (800,600), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour(wx.WHITE)

        # GUI Widgets
        wx.StaticText(self, -1, "Drag and Drop Image 1", (10, 15))
        wx.StaticText(self, -1, "Drag and Drop Image 2", (410, 15))
        self.text1 = wx.TextCtrl(self, -1, "", pos=(10,35), size=(360,20), style = wx.TE_READONLY)
        self.text2 = wx.TextCtrl(self, -1, "", pos=(410,35), size=(360,20), style = wx.TE_READONLY)

        # define images
        img1 = wx.Image(ThumbMaxSize,ThumbMaxSize)
        img2 = wx.Image(ThumbMaxSize,ThumbMaxSize)
        self.imageCtrl1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img1), pos=(10,65))
        self.imageCtrl2 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img2), pos=(410,65))

        # Create a File Drop Target object
        dt1 = FileDropTarget(self.text1, self.imageCtrl1, self)
        dt2 = FileDropTarget(self.text2, self.imageCtrl2, self)

        # Link the Drop Target Object to the Text Control
        self.text1.SetDropTarget(dt1)
        self.text2.SetDropTarget(dt2)

        # Display the Window
        self.Show(True)



class MyApp(wx.App):
    """ Define the Drag and Drop Example Application """
    def OnInit(self):
        """ Initialize the Application """
        # Declare the Main Application Window
        frame = MainWindow(None, -1, "Image Alignment Tool")
        # Show the Application as the top window
        self.SetTopWindow(frame)
        return True

# Declare the Application and start the Main Loop
app = MyApp(0)
app.MainLoop()