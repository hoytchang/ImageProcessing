import wx
#import scipy as sp
#import imreg_dft as ird
#import PyQt5
#from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt5.QtGui import QImage
import os
from threading import Thread
import skimage
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt

#ThumbMaxSize = 360
#edges1File = 'image1edges.jpg'
#edges2File = 'image2edges.jpg'
#image2scaledFile = "image2scaled.jpg"
#overlayFile = 'overlay.jpg'
#OutputMaxSize = 360
NoFileSelected = "No File Selected"

# Define File Drop Target class
class FileDropTarget(wx.FileDropTarget):

    def __init__(self, textCtrl, frame):
        """ Initialize the Drop Target, passing in the Object Reference to
          indicate what should receive the dropped files """
        # Initialize the wxFileDropTarget Object
        wx.FileDropTarget.__init__(self)
        self.textCtrl = textCtrl
        self.frame = frame

    def OnDropFiles(self, x, y, filenames):
        # display filename to gui
        self.textCtrl.Clear()
        file = filenames[0]
        self.textCtrl.WriteText(file)
        return True

class MainWindow(wx.Frame):
    """ This window displays the GUI Widgets. """
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent, wx.ID_ANY, title, size = (400,220), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour(wx.WHITE)

        # define text
        wx.StaticText(self, -1, "Drag and Drop Reference Image File", (10, 15))
        self.text1 = wx.TextCtrl(self, -1, "", pos=(10,35), size=(360,20), style = wx.TE_READONLY)
        wx.StaticText(self, -1, "Drag and Drop Moving Image File", (10, 60))
        self.text2 = wx.TextCtrl(self, -1, "", pos=(10,80), size=(360,20), style = wx.TE_READONLY)
        self.text1.WriteText(NoFileSelected)
        self.text2.WriteText(NoFileSelected)

        # Create a File Drop Target object
        dt1 = FileDropTarget(self.text1, self)
        dt2 = FileDropTarget(self.text2, self)

        # define check box and buttons
        self.detectEdgesBool = wx.CheckBox(self, -1, "Detect Edges", pos = (10,120))
        buttonAlign = wx.Button(self, -1, "Align", pos=(10,140))
        buttonAlign.Bind(wx.EVT_BUTTON, self.onAlign)

        # Link the Drop Target Object to the Image Control
        self.text1.SetDropTarget(dt1)
        self.text2.SetDropTarget(dt2)

        # Display the Window
        self.Show(True)

    def onAlign(self, button):
        # get paths
        path1 = self.text1.GetValue()
        path2 = self.text2.GetValue()
        
        if(path1 != NoFileSelected and path2 != NoFileSelected):
            detectEdgesBool = self.detectEdgesBool.GetValue()
            worker = AlignWorkerThread(self, path1, path2, detectEdgesBool)

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

    def choose_corresponding_points(self, img0, img1):
        """Utility function for finding corresponding features in images.
        Alternately click on image 0 and 1, indicating the same feature.
        """
        f, (ax0, ax1) = plt.subplots(1, 2)
        ax0.imshow(img0)
        ax1.imshow(img1)
        coords = plt.ginput(8, timeout=0)
        np.savez('_reg_coords.npz', source=coords[::2], target=coords[1::2])
        plt.close()

    def toRGB(self, img):
        # convert png to jgp
        if(img.shape[2] == 4):
            return skimage.color.rgba2rgb(img)
        else:
            return img

    def run(self):
        # this needs to be in a thread to not lock up the gui

        # apply edge detection to both input images
        if(self.detectEdgesBool):
            pass
        else:
            pass

        img0 = io.imread(self.path1)
        img1 = io.imread(self.path2)

        # have user select reference points to define transformation
        self.choose_corresponding_points(img0, img1)
        coords = np.load('_reg_coords.npz')

        # transform image
        tf = transform.estimate_transform('similarity', coords['source'], coords['target'])
        offset = transform.SimilarityTransform(translation=(0, 0))
        h0 = img0.shape[0]
        w0 = img0.shape[1]
        #h1 = img1.shape[0]
        #w1 = img1.shape[1]
        #maxSize = max(h0,w0,h1,w1)
        img0_warped = transform.warp(img0, inverse_map=offset, output_shape=(h0, w0))
        img1_warped = transform.warp(img1, inverse_map= tf, output_shape=(h0, w0))

        # check for different numpy shapes
        # png has shape (height, width, 4)
        # jpg has shape (height, width, 3)
        img0_warped = self.toRGB(img0_warped)
        img1_warped = self.toRGB(img1_warped)

        # Find where both images overlap; in that region average their values
        mask = (img0_warped != 0) & (img1_warped != 0)

        # overlay
        overlay = img0_warped + img1_warped  # works with jpg, but not with png
        overlay[mask] /= 2

        # display
        plt.imshow(overlay)
        plt.show()


class MyApp(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, "Image Alignment Tool")
        self.SetTopWindow(frame)
        return True

# Declare the Application and start the Main Loop
app = MyApp(0)
app.MainLoop()