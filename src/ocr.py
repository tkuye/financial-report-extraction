import pytesseract
import numpy as np
import cv2
from src.utils import wrap

@wrap
def ocr_to_results(image: np.ndarray):
	options = '--psm 11'
	results = pytesseract.image_to_data(
    cv2.cvtColor(image, cv2.COLOR_BGR2RGB), 
    config=options, 
    output_type=pytesseract.Output.DICT
	)

	coordText = []

	for i in range(0, len(results['text'])):
		x = results['left'][i]
		y = results['top'][i]
		w = results['width'][i]
		h = results['height'][i]

		text = results['text'][i]
		conf = int(results['conf'][i])
		if conf > 0:
			coordText.append({
				'coords':(x, y, w, h),
				'text':text
			})
	return coordText


