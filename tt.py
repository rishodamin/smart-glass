import easyocr

reader = easyocr.Reader(['en'])  # Initialize with the required language
result = reader.readtext("image.jpg")

for (bbox, text, prob) in result:
    print(f"Detected text: {text} (Confidence: {prob:.2f})")
