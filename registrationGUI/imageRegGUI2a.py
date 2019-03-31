import wx
import scipy as sp
import imreg_dft as ird
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage
import os
from threading import Thread
import skimage

ThumbMaxSize = 360
edges1File = 'image1edges.jpg'
edges2File = 'image2edges.jpg'
image2scaledFile = "image2scaled.jpg"
overlayFile = 'overlay.jpg'
OutputMaxSize = 360
NoFileSelected = "No File Selected"

# Define File Drop Target class
class FileDropTarget(wx.FileDropTarget):

    def __init__(self, obj, imageCtrl, frame):
        """ Initialize the Drop Target, passing in the Object Reference to
          indicate what should receive the dropped files """
        # Initialize the wxFileDropTarget Object
        wx.FileDropTarget.__init__(self)
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
        imgThumb = img.Scale(NewW,NewH)

        # assign image to image control
        self.imageCtrl.SetBitmap(wx.Bitmap(imgThumb))
        self.frame.Refresh()

        return True

class MainWindow(wx.Frame):
    """ This window displays the GUI Widgets. """
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent, wx.ID_ANY, title, size = (800,900), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour(wx.WHITE)

        # define text
        wx.StaticText(self, -1, "Drag and Drop Image File 1", (10, 15))
        wx.StaticText(self, -1, "Drag and Drop Image File 2", (410, 15))
        self.text1 = wx.TextCtrl(self, -1, "", pos=(10,35), size=(360,20), style = wx.TE_READONLY)
        self.text2 = wx.TextCtrl(self, -1, "", pos=(410,35), size=(360,20), style = wx.TE_READONLY)
        self.text1.WriteText(NoFileSelected)
        self.text2.WriteText(NoFileSelected)
        self.alignStatus = wx.StaticText(self, -1, "Aligning...Please Wait", (520,515))
        self.alignStatus.Hide()

        # define images
        img1 = wx.Image(ThumbMaxSize,ThumbMaxSize)
        img2 = wx.Image(ThumbMaxSize,ThumbMaxSize)
        img3 = wx.Image(OutputMaxSize, OutputMaxSize)
        self.imageCtrl1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img1), pos=(10,65))
        self.imageCtrl2 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img2), pos=(410,65))
        self.imageCtrl3 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img3), pos=(10,450))

        # track mouse
        self.imageCtrl1.Bind(wx.EVT_LEFT_UP, self.ImageCtrl_OnMouseMove)
        self.imageCtrl2.Bind(wx.EVT_LEFT_UP, self.ImageCtrl_OnMouseMove)

        # Create a File Drop Target object
        dt1 = FileDropTarget(self.text1, self.imageCtrl1, self)
        dt2 = FileDropTarget(self.text2, self.imageCtrl2, self)

        # define check box and buttons
        self.detectEdges = wx.CheckBox(self, -1, "Detect Edges", pos = (410,450))
        buttonDefineAlignment = wx.Button(self, -1, "Define Alignment", pos=(410,480))
        buttonDefineAlignment.Bind(wx.EVT_BUTTON, self.onDefineAlign)
        buttonAlign = wx.Button(self, -1, "Align", pos=(410,510))
        buttonAlign.Bind(wx.EVT_BUTTON, self.onAlign)
        buttonCopyToClipboard = wx.Button(self, -1, "Copy Image To Clipboard", pos=(410,540))
        buttonCopyToClipboard.Bind(wx.EVT_BUTTON, self.onCopyToClipboard)

        # Link the Drop Target Object to the Image Control
        self.imageCtrl1.SetDropTarget(dt1)
        self.imageCtrl2.SetDropTarget(dt2)

        # Display the Window
        self.Show(True)

    def ImageCtrl_OnMouseMove(self, event):
        ctrl_pos = event.GetPosition()
        print("ctrl_pos: " + str(ctrl_pos.x) + ", " + str(ctrl_pos.y))
        #pos = self.imageCtrl1.ScreenToClient(ctrl_pos)
        #print("pos relative to screen top left = ", pos)
        #screen_pos = self.GetScreenPosition()
        #relative_pos_x = pos[0] + screen_pos[0]
        #relative_pos_y = pos[1] + screen_pos[1]
        #print("pos relative to image top left = ", relative_pos_x, relative_pos_y)

    def onDefineAlign(self, button):
        pass

    def onAlign(self, button):
        # get paths
        path1 = self.text1.GetValue()
        path2 = self.text2.GetValue()
        
        if(path1 != NoFileSelected and path2 != NoFileSelected):
            detectEdges = self.detectEdges.GetValue()
            worker = AlignWorkerThread(self, path1, path2, detectEdges)

    def onCopyToClipboard(self, button):
        # check that im3 exists
        try:
            self.img3
        except:
            return

        # copy overlay image file to clipboard
        app = QtWidgets.QApplication([])
        data = QtCore.QMimeData()
        cwd = os.getcwd()
        overlayFilePath = os.path.join(cwd, overlayFile)
        url = QtCore.QUrl.fromLocalFile(overlayFilePath)
        data.setUrls([url])
        app.clipboard().setMimeData(data)

class AlignWorkerThread(Thread):
    
    def __init__(self, frame, path1, path2, detectEdgesBool):
        Thread.__init__(self)
        self.frame = frame
        self.path1 = path1
        self.path2 = path2
        self.detectEdgesBool = detectEdgesBool
        self.start()

    def detectEdges(self, path):
        img = skimage.io.imread(path)
        img_grey = skimage.color.rgb2grey(img)
        edge_sobel = skimage.filters.sobel(img_grey)
        edge_inverted = skimage.util.invert(edge_sobel)
        return edge_inverted

    def run(self):
        # this needs to be in a thread to not lock up the gui
        self.frame.alignStatus.Show() 

        # apply edge detection to both input images
        if(self.detectEdgesBool):
            skim1edges = self.detectEdges(self.path1)
            skim2edges = self.detectEdges(self.path2)
            skimage.io.imsave(edges1File,skim1edges)
            skimage.io.imsave(edges2File,skim2edges)
            im1wx = wx.Image(edges1File, wx.BITMAP_TYPE_ANY)
            im2wx = wx.Image(edges2File, wx.BITMAP_TYPE_ANY)
        else:
            im1wx = wx.Image(self.path1, wx.BITMAP_TYPE_ANY)
            im2wx = wx.Image(self.path2, wx.BITMAP_TYPE_ANY)

        # scale image 2
        w1 = im1wx.GetWidth()
        h1 = im1wx.GetHeight()
        w2 = im2wx.GetWidth()
        h2 = im2wx.GetHeight()
        im2scaled = im2wx.Scale(w1,h1) # not a good scaling method
        im2scaled.SaveFile(image2scaledFile)

        # read in image 1 and scaled image 2
        if(self.detectEdgesBool):
            im1 = sp.misc.imread(edges1File,True)
        else:
            im1 = sp.misc.imread(self.path1,True)
        im2 = sp.misc.imread(image2scaledFile,True)

        # align image 2
        result = ird.similarity(im1, im2, numiter=3)
        assert "timg" in result
        im2aligned = result['timg']

        # overlay
        overlay = im1 + im2aligned
        sp.misc.imsave(overlayFile,overlay)

        # display overlay
        self.frame.img3 = wx.Image(overlayFile, wx.BITMAP_TYPE_ANY)
        img3thumb = self.frame.img3.Scale(OutputMaxSize,OutputMaxSize)
        self.frame.imageCtrl3.SetBitmap(wx.Bitmap(img3thumb))
        self.frame.Refresh()

        self.frame.alignStatus.Hide()

class MyApp(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, "Image Alignment Tool")
        self.SetTopWindow(frame)
        return True

# Declare the Application and start the Main Loop
app = MyApp(0)
app.MainLoop()