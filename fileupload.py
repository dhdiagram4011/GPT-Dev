from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from mimetypes import MimeTypes
import fitz #pdf 파일에서 텍스트를 추출해주는 라이브러리
from docx import Document
import nltk
import pytesseract
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from PIL import Image
from io import BytesIO
from collections import Counter
from wordcloud import WordCloud
from pymongo import MongoClient
from datetime import datetime
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
import pandas as pd
import numpy as np
import re

app = FastAPI()

#cors
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_PATH="C:/workspace/storage/uploads/"

#텍스트 분석 데이터 이미지 저장 경로
UPLOAD_PATH_01="C:/workspace/storage/uploads/imgdata"

VALID_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
VALID_PDF_TYPES = ["application/pdf"]
VALID_OFFICE_TYPES = [
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
]


def get_file_extension(file: UploadFile):
    mime = MimeTypes()
    mime_type, encoding = mime.guess_type(file.filename)
    return mime_type

def is_valid_image(file: UploadFile):
    file_extension = get_file_extension(file)
    if file_extension in VALID_IMAGE_TYPES or file_extension in VALID_PDF_TYPES or file_extension in VALID_OFFICE_TYPES:
        return True
    return False

def save_upload_file(file: UploadFile, destination: str):
    with open(destination, "wb") as f:
        f.write(file.file.read())


def extr_txt_from_pdf(pdf_path): #pdf 파일에서 text 추출
    word = ""
    pdf_docu = fitz.open(pdf_path) #fitz : pdf파일에서 이미지만 추출해주는 패키지
    for page_number in range(len(pdf_docu)):
        page = pdf_docu[page_number]
        word += page.get_text() #pdf 파일 내용 화면 출력
        recog1_word = re.findall(r'\b\w+\b', word) #단어빈도수 데이터 추출 전 가공작업
        recog2_word = Counter(recog1_word)
        sorted_word = sorted(recog2_word.items(), key=lambda x:x[1], reverse=True) #카운터 오름차순 정렬
        print(sorted_word) #단어별 카운터 출력


    #mongodb저장
    mongodb_uri = "mongodb://localhost:27017/"
    pdf_path = pdf_path
    database_name = "itt_data"
    collection_name = "export_data"
    client = MongoClient(mongodb_uri)
    db = client[database_name]
    collection = db[collection_name]

    document = {
        "pdf_path" : pdf_path, #pdf 파일 경로 저장
        "word_count" : sorted_word, #단어 카운트 정보 저장
        "extr_txt" : word, #pdf에서 추출한 텍스트 저장 
    }

    collection.insert_one(document)
    client.close()


    #워드클라우드 시각화
    cur_date = datetime.now().timestamp()
    font_path = 'C:/Users/user/anaconda3/envs/itt/Lib/site-packages/matplotlib/mpl-data/fonts/ttf/NanumSquareEB.ttf'
    wc = WordCloud(font_path=font_path,width=1000, height=600, background_color="white", random_state=0)
    plt.imshow(wc.generate_from_text(word))
    plt.axis('off') #가로/세로축 숫자 이미지 제거
    plt.savefig('C:/workspace/1012_ittnew/imagetotext/public/wc_image01.png', format='png')
    plt.show()

    #단어 출력 빈도별 그래프 출력
    plt.rc('font', family='Malgun Gothic')
    #wf = nltk.FreqDist(word)
    wf = FreqDist(word.lower() for word in word_tokenize(word))
    print(word)
    df = pd.DataFrame(list(wf.values()), wf.keys())
    res = df.sort_values([0], ascending=False)
    res = res[:10]
    res.plot(kind='bar', legend=False, figsize=(15,5))
    plt.savefig('C:/workspace/1012_ittnew/imagetotext/public/wc_image02.png', format='png')
    plt.show()
    pdf_docu.close()
    return word


def extr_txt_from_docx(docu_path): #docx 파일에서 text 추출
    word = ""
    docu = Document(docu_path)
    for pgraph in docu.paragraphs:
        word += pgraph.text
    return word


#image파일에서 txt 추출
def extr_txt_from_img(img_path): #pdf 파일에서 text 추출
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img)
    return text


@app.post("/upload")
async def upload_file(file: UploadFile):
    if not is_valid_image(file):
        return JSONResponse(content={"error":"지원되지 않는 파일 형식"}, status_code=422)
    
    destination = os.path.join(UPLOAD_PATH, file.filename)
    save_upload_file(file, destination)


    extr_txt = "" 
    if get_file_extension(file) == "application/pdf":
        extr_txt = extr_txt_from_pdf(destination)
    elif get_file_extension(file) in VALID_OFFICE_TYPES:
        extr_txt =extr_txt_from_docx(destination)
    elif get_file_extension(file) in VALID_IMAGE_TYPES:
        extr_txt = extr_txt_from_img(destination)


    filename = os.path.splitext(file.filename)
    text_file_path = os.path.join(UPLOAD_PATH, f"{filename}.txt")
    with open (text_file_path, "w", encoding="utf-8") as text_file:
        text_file.write(extr_txt)
    
    return {"filename": file.filename, "saved_at": destination, "extr_txt": extr_txt}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)