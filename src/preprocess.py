from pdf2image import convert_from_bytes
import cv2
import numpy as np
from scipy import stats
from typing import List
from src.utils import wrap

@wrap
def pdf2images(pdf, pages) -> List[np.ndarray]:
	"""
		Function to convert pdfs to images from buffers, given a list of pages.

	"""
	images = convert_from_bytes(pdf)

	if len(images) == 1:
		return [np.array(images[0])]

	return_images:List[np.array] = []
	for page in pages:
		try:
			return_images.append(np.array(images[page - 1]))
		except IndexError:
			pass
	
	return return_images

@wrap
def get_distance_threshold(image:np.ndarray):
	"""Function to calculate distance threshold for an image given a table.
	Args:
		image (_type_): _description_

	Returns:
		_type_: _description_
	"""
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (51, 11))

	# perform gaussian blur on image
	gray = cv2.GaussianBlur(gray, (3, 3), 0)
	blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
	
	grad = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
	grad = np.absolute(grad)

	(minVal, maxVal) = (np.min(grad), np.max(grad))
	grad = (grad - minVal) / (maxVal - minVal)
	grad = (grad * 255).astype('uint8')


	grad = cv2.morphologyEx(grad, cv2.MORPH_CLOSE, kernel)
	thresh = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	thresh = cv2.dilate(thresh, None, iterations=3)

	contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

	# compute the bounding box coordinates of the stats table and extract
	# the table from the input image

	heights = []
	for cnt in contours[::-1]:
		h = cv2.boundingRect(cnt)[3]
		heights.append(h)

	dist_thresh = stats.mode(heights)[0][0]

	return dist_thresh
