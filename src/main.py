from fastapi import FastAPI, File, UploadFile, Form
from src.pipeline import pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/table-files/')
async def create_csv_file(file: UploadFile = File(), pages:str = Form(), threshold:str = Form()):
	file_content = await file.read()
	try:
		threshold = int(threshold)
	except ValueError:
		threshold = 0
	res = await pipeline(file_content, pages, file.filename, threshold)
	return res


