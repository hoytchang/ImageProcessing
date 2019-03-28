import wx
import scipy as sp
import imreg_dft as ird
import PyQt5
from PyQt5 import QtCore, QtGui

ThumbMaxSize = 360
image2scaledFile = "image2scaled.jpg"
overlayFile = 'overlay.jpg'
OutputMaxSize = 360
NoFileSelected = "No File Selected"

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
        wx.Frame.__init__(self,parent, wx.ID_ANY, title, size = (800,900), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour(wx.WHITE)

        # GUI Widgets
        wx.StaticText(self, -1, "Drag and Drop Image File 1", (10, 15))
        wx.StaticText(self, -1, "Drag and Drop Image File 2", (410, 15))
        self.text1 = wx.TextCtrl(self, -1, "", pos=(10,35), size=(360,20), style = wx.TE_READONLY)
        self.text2 = wx.TextCtrl(self, -1, "", pos=(410,35), size=(360,20), style = wx.TE_READONLY)
        self.text1.WriteText(NoFileSelected)
        self.text2.WriteText(NoFileSelected)

        # define images
        img1 = wx.Image(ThumbMaxSize,ThumbMaxSize)
        img2 = wx.Image(ThumbMaxSize,ThumbMaxSize)
        img3 = wx.Image(OutputMaxSize, OutputMaxSize)
        self.imageCtrl1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img1), pos=(10,65))
        self.imageCtrl2 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img2), pos=(410,65))
        self.imageCtrl3 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img3), pos=(10,480))

        # Create a File Drop Target object
        dt1 = FileDropTarget(self.text1, self.imageCtrl1, self)
        dt2 = FileDropTarget(self.text2, self.imageCtrl2, self)

        # define buttons
        buttonAlign = wx.Button(self, -1, "Align", pos=(10,450))
        buttonAlign.Bind(wx.EVT_BUTTON, self.onAlign)
        buttonCopyToClipboard = wx.Button(self, -1, "Copy Image To Clipboard", pos=(120,450))
        buttonCopyToClipboard.Bind(wx.EVT_BUTTON, self.onCopyToClipboard)

        # Link the Drop Target Object to the Image Control
        self.imageCtrl1.SetDropTarget(dt1)
        self.imageCtrl2.SetDropTarget(dt2)

        # Display the Window
        self.Show(True)

    def onAlign(self, button):
        # get paths
        path1 = self.text1.GetValue()
        path2 = self.text2.GetValue()
        
        if(path1 != NoFileSelected and path2 != NoFileSelected):
            # scale image 2
            im1wx = wx.Image(path1, wx.BITMAP_TYPE_ANY)
            im2wx = wx.Image(path2, wx.BITMAP_TYPE_ANY)
            w1 = im1wx.GetWidth()
            h1 = im1wx.GetHeight()
            w2 = im2wx.GetWidth()
            h2 = im2wx.GetHeight()
            im2scaled = im2wx.Scale(w1,h1) # not a good scaling method
            im2scaled.SaveFile(image2scaledFile)

            # read in image 1 and scaled image 2
            im1 = sp.misc.imread(path1,True)
            im2 = sp.misc.imread(image2scaledFile,True)

            # align image 2
            result = ird.similarity(im1, im2, numiter=3)
            assert "timg" in result
            im2aligned = result['timg']

            # overlay
            overlay = im1 + im2aligned
            sp.misc.imsave(overlayFile,overlay)

            # display overlay
            self.img3 = wx.Image(overlayFile, wx.BITMAP_TYPE_ANY)
            img3resized = self.img3.Scale(OutputMaxSize,OutputMaxSize)
            self.imageCtrl3.SetBitmap(wx.Bitmap(img3resized))
            self.Refresh()

    def onCopyToClipboard(self, button):
        try:
            self.img3
        except:
            return

        temp_variable = self.img3
        # TODO




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