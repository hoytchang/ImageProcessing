import os
import scipy as sp
import scipy.misc
import imreg_dft as ird
import matplotlib.pyplot as plt

im0 = sp.misc.imread("IbeamStype.jpg",True)
im1 = sp.misc.imread("steel-beam.jpg",True)

result = ird.similarity(im0,im1,numiter=3)

assert "timg" in result

#ird.imshow(im0,im1,result['timg'])
#plt.show()

fig, ax = plt.subplots(nrows = 2, ncols = 2)
ax[0,0].imshow(im0, cmap=plt.cm.gray)
ax[0,0].set_title('Image 1')

ax[0,1].imshow(im1, cmap=plt.cm.gray)
ax[0,1].set_title('Image 2')

ax[1,1].imshow(result['timg'], cmap=plt.cm.gray)
ax[1,1].set_title("Image 2 Transformed")

overlay = im0 + result['timg']

ax[1,0].imshow(overlay, cmap=plt.cm.gray)
ax[1,0].set_title("Overlay")

for i in ax:
	for j in i:
		j.get_xaxis().set_ticks([])
		j.get_yaxis().set_ticks([])
		#j.axis('off')
		#j.spines['bottom'].set_visible(True)
		#j.spines['top'].set_visible(True)
		#j.spines['right'].set_visible(True)
		#j.spines['left'].set_visible(True)
plt.show()