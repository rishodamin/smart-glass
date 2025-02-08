import pytesseract
from PIL import Image
import cv2
import os
import numpy as np
import threading
import time
from gtts import gTTS

frame_received = None  # Make sure to define this globally

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    os.system("mpg321 output.mp3")  

def img2txt():
    global frame_received  # Access the global variable
    while True:
        if frame_received is None:  # FIX: Use `is None`
            time.sleep(0.5)
            continue
        usr = input("Press Enter to process image or 'q' to quit: ")
        if usr.lower() == 'q':
            break
        frame_rgb = cv2.cvtColor(frame_received, cv2.COLOR_BGR2RGB)    
        pil_image = Image.fromarray(frame_rgb)
        text = pytesseract.image_to_string(pil_image)
        print("Recognized Text:", text)

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
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame (stream end?). Exiting ...")
        break
    frame_received = frame.copy()  # Use `.copy()` to avoid race conditions
    
    cv2.imshow("Live Feed", frame)  # Show the live video feed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
