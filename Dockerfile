FROM python:3.9       

WORKDIR /app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install -y tesseract-ocr 

COPY . .

RUN pip3 install pipenv && pipenv install --system --deploy --ignore-pipfile


CMD ["pipenv", "run", "uvicorn", "src.main:app",  "--host", "0.0.0.0", "--port", "80"]

EXPOSE 80 443 22