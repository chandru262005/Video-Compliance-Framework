import cv2
import pytesseract
import easyocr

# 🔴 Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize EasyOCR ONCE (important for performance)
reader = easyocr.Reader(['en'], gpu=False)


# -------------------------------
# 1. Light Preprocessing
# -------------------------------
def preprocess(image_path):
    img = cv2.imread(image_path)

    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Light upscale (helps OCR slightly)
    img = cv2.resize(img, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    return gray


# -------------------------------
# 2. Tesseract OCR
# -------------------------------
def tesseract_ocr(img):
    config = r'--oem 3 --psm 11'  # sparse text mode
    text = pytesseract.image_to_string(img, config=config)
    return text


# -------------------------------
# 3. EasyOCR fallback
# -------------------------------
def easyocr_ocr(image_path):
    results = reader.readtext(image_path)

    text = " ".join([res[1] for res in results])
    return text


# -------------------------------
# 4. Garbage Detection
# -------------------------------
def is_garbage(text):
    text = text.strip()

    if len(text) < 10:
        return True

    bad_chars = sum(1 for c in text if not c.isalnum() and c != ' ')
    ratio = bad_chars / max(len(text), 1)

    return ratio > 0.3


# -------------------------------
# 5. Clean Text
# -------------------------------
def clean_text(text):
    text = text.replace('\n', ' ')
    text = " ".join(text.split())
    return text


# -------------------------------
# 6. Main OCR Pipeline
# -------------------------------
def run_ocr(image_path):
    print("[INFO] Running Tesseract...")

    processed = preprocess(image_path)
    t_text = tesseract_ocr(processed)
    t_text = clean_text(t_text)

    print(f"[Tesseract Output]: {t_text}")

    # Check quality
    if is_garbage(t_text):
        print("[INFO] Tesseract output poor → switching to EasyOCR...")

        e_text = easyocr_ocr(image_path)
        e_text = clean_text(e_text)

        print(f"[EasyOCR Output]: {e_text}")
        return e_text

    return t_text


# -------------------------------
# 7. Run
# -------------------------------
if __name__ == "__main__":
    image_path = r"C:\Users\ELCOT\Desktop\ocr\Video-Compliance-Framework\ad.webp"

    final_text = run_ocr(image_path)

    print("\n✅ FINAL OUTPUT:")
    print(final_text)