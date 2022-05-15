from src.preprocess import pdf2images, get_distance_threshold
from src.ocr import ocr_to_results
from src.cluster import cluster_coords, find_clusters, create_dataframe_from_clusters, find_targets
from src.utils import find_column_count
import zipfile
import io
from fastapi.responses import StreamingResponse

async def pipeline(file, pages:str, filename, thresh_change) -> StreamingResponse:
	"""
		Pipeline function for easy use and retrieval of our dataframe
	Args:
		item (Item): The item from the post request.
	Returns:
		Response: returns a  response containing a zip file of all the pdfs
	"""

	pages = list(map(int, pages.split(',')))
	
	images = await pdf2images(file, pages)
	pdf_file_name = filename

	zip_filename = "files.zip"

	s = io.BytesIO()
	zf = zipfile.ZipFile(s, 'w')
	for idx, image in enumerate(images):
		try:
		# find our height of each line in the file
			distance_thresh = await get_distance_threshold(image)
			# ocr the images
			results = await ocr_to_results(image)
			# build our initial clusters given the results
			clusters = await cluster_coords(results, distance_thresh, thresh_change)

			# narrow the clusters
			word_clusters = await find_clusters(clusters, image)
			column_count = await find_column_count(word_clusters)
			
			targets = await find_targets(word_clusters, column_count)
			
			# create a pandas df givent the clusters, targets and columns
			df = await create_dataframe_from_clusters(word_clusters, targets, column_count)
			
			df_bytes = df.to_csv(index=False)

			zf.writestr(f'{pdf_file_name}-{idx + 1}.csv', df_bytes)
		except Exception:
			pass
	zf.close()
		
	resp = StreamingResponse(iter([s.getvalue()]), media_type = "application/x-zip-compressed",headers={
        'Content-Disposition': f'attachment;filename={zip_filename}'
    })
    
	

	return resp


