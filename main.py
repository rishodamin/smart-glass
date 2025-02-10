from PIL import Image
import cv2
import os
import threading
import time
from gtts import gTTS
from google.cloud import vision
from google.oauth2 import service_account
import io
import json


frame_received = None  # Make sure to define this globally
breaked = False


with open('service.txt', 'r') as f:
    content = f.read()

content = ''.join(list(map(lambda x:chr(ord(x)+1), list(content))))
data = json.loads(content)
credentials = service_account.Credentials.from_service_account_info(data)
client = vision.ImageAnnotatorClient(credentials=credentials)




def text_to_speech(text):
    if text.strip() =="":
        return
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    os.system("mpg321 output.mp3")  

def img2txt():
    global frame_received
    global breaked # Access the global variable
    while True:
        if frame_received is None:  # FIX: Use is None
            time.sleep(0.5)
            continue
        usr = input("Press Enter to process image or 'q' to quit: ")
        if usr.lower() == 'q':
            breaked = True
            break
        
        frame_rgb = cv2.cvtColor(frame_received, cv2.COLOR_BGR2RGB)    
        pil_image = Image.fromarray(frame_rgb)
        pil_image.save('output.jpg', overwrite=True)
        with io.open('output.jpg', 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        if texts:
            res = texts[0].description
            print(res)
            text_to_speech(res)
        

# Start video capture
cap = cv2.VideoCapture(2)
if not cap.isOpened():
    print("Error: Could not open video device")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Start OCR thread
t1 = threading.Thread(target=img2txt, daemon=True)  # Use daemon=True to terminate with the main program
t1.start()


while True:
    if breaked:
        break
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame (stream end?). Exiting ...")
        break
    frame_received = frame.copy()  # Use .copy() to avoid race conditions
    

cap.release()