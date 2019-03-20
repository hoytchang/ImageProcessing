import os
import matplotlib.pyplot as plt
import skimage
from skimage import feature

# Read in CT scan from 
# https://www.yxlon.com/Yxlon/media/Content/Applications/Aerospace/Turbine%20blades/CT-feanbeame_Aerospace_Turbine_blade_001_144.jpg?ext=.jpg
filename = 'CT-feanbeame_Aerospace_Turbine_blade_001_144.jpg'
img = skimage.io.imread(filename)

# Convert to greyscale
img_grey = skimage.color.rgb2grey(img)

# Compute contours
contours = skimage.measure.find_contours(img_grey, 0.8)

# Compute Canny filter
edges1 = feature.canny(img_grey, sigma = 1)
edges2 = feature.canny(img_grey, sigma = 3)

# Compute Edge Operators
edge_roberts = skimage.filters.roberts(img_grey)
edge_sobel = skimage.filters.sobel(img_grey)

# Show original
fig, ax = plt.subplots(nrows = 3, ncols = 2)
ax[0,0].imshow(img)
ax[0,0].set_title('Original')

# Show contour
ax[0,1].imshow(img)
ax[0,1].set_title('With Contours')
for n, contour in enumerate(contours):
	ax[0,1].plot(contour[:,1], contour[:,0], linewidth = 2)

# Show canny filter
ax[1,0].imshow(edges1, cmap=plt.cm.gray)
ax[1,0].set_title('Canny Filter, $\sigma=1$')
ax[1,1].imshow(edges2, cmap=plt.cm.gray)
ax[1,1].set_title('Canny Filter, $\sigma=3$')

# Show edge detection
ax[2,0].imshow(edge_roberts, cmap=plt.cm.gray)
ax[2,0].set_title('Roberts Edge Detection')
ax[2,1].imshow(edge_sobel, cmap=plt.cm.gray)
ax[2,1].set_title('Sobel Edge Detection')

for i in ax:
	for j in i:
		j.axis('off')
plt.show()