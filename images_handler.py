import cv2
import face_recognition
import requests
# import re
import os

from config import BACKEND_BASE_URL


# ==========================================
# FETCHING DOWNLOADED IMAGES AND PERSON IDS
# ==========================================

def fetchImages(imagesPath):
    images = []
    personIds = []
    userTypes = []
    myList = os.listdir(imagesPath)
    for item in myList:
        img = cv2.imread(os.path.join(imagesPath, item))
        if(img is None):
            continue
        images.append(img)
        fileName = os.path.splitext(item)[0].split()
        personIds.append(fileName[0])
        userTypes.append(fileName[1])

    return (images, personIds, userTypes)


# ==========================================
# FUNCTION RETURNING LIST OF ENCODINGS OF ALL IMAGES INSIDE THE GIVEN LIST
# ==========================================

# HOG Algorithm


def faceEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


# ==========================================
# FUNCTIONS TO DOWNLOAD IMAGES FROM DRIVE
# ==========================================

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    # destination = re.search(r'filename\=\"(.*)\"',
    #                         response.headers['Content-Disposition']).group(1)

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def downloadImages(directory):
    r = requests.get(BACKEND_BASE_URL+'/system/images')
    data = r.json()

    for img in data:
        file_id = img['imageUrl'].split('/')[5]
        file_name = f"{img['_id']} {img['type']}.jpg"
        destination = os.path.join(directory, file_name)
        download_file_from_google_drive(file_id, destination)
        # if(not os.path.exists(destination)):
        #     download_file_from_google_drive(file_id, destination)
