import cv2
import time
from pathlib import Path
import easyocr

## folder where your pictures are stored
image_folder = Path(r"C:\Users\Jack\Pictures\Jack QR Code Test")


## change only this line to test a different photo
file_name = "QRCodeTest.png"


## expected QR value
expected_text = "This is a tes"

## expected OCR text
expected_ocr_text = "This is a test"


## build image path
image_path = image_folder / file_name


## load imagec
img = cv2.imread(str(image_path))

if img is None:
    print("Image not found")
    print("Tried to load:", image_path)
    exit()


## make a copy to draw on-
img_copy = img.copy()


## create QR code detector
qr_detector = cv2.QRCodeDetector()



## create OCR reader 
ocr_reader = easyocr.Reader(['en'], gpu=False)


## detect and decode QR code
qr_value, qr_points, straight_qrcode = qr_detector.detectAndDecode(img)


## check if QR was found
qr_found = qr_points is not None and qr_value != ""


if qr_found:
    ## convert QR points to integer points
    qr_points = qr_points[0].astype(int)

        ## get QR bounding box
    qr_x, qr_y, qr_w, qr_h = cv2.boundingRect(qr_points)

    ## create text box based on QR location
    text_x1 = qr_x + qr_w + int(qr_w * 0.12)

    text_w = int(qr_w * 2.80)
    text_h = int(qr_h * 0.42)

    ## center the text box vertically with the lower-middle of the QR code
    text_center_y = qr_y + int(qr_h * 0.93)

    text_y1 = text_center_y - text_h // 2

    text_x2 = text_x1 + text_w
    text_y2 = text_y1 + text_h

    ## keep text box inside image
    text_x1 = max(0, text_x1)
    text_y1 = max(0, text_y1)
    text_x2 = min(img.shape[1], text_x2)
    text_y2 = min(img.shape[0], text_y2)

    ## draw text box
    cv2.rectangle(img_copy, (text_x1, text_y1), (text_x2, text_y2), (255, 0, 0), 2)

    ## label text box
    cv2.putText(img_copy, "Text ROI", (text_x1, text_y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)

    print("Text ROI:", (text_x1, text_y1), (text_x2, text_y2))
    
    ## crop text ROI
    text_roi = img[text_y1:text_y2, text_x1:text_x2]

    ## make the text ROI bigger for OCR 
    text_roi_big = cv2.resize(text_roi, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    startTime = time.time()

    ## read the text inside the blue box only
    ocr_results = ocr_reader.readtext(text_roi_big)

    endTime = time.time()

    print("Time to do OCR: ", float(endTime-startTime))

    ## combine OCR results into one text string
    ocr_text = ""

    if len(ocr_results) > 0:
        ocr_text = " ".join([results[1] for results in ocr_results])

    ## print what ocr read
    print("OCR text", ocr_text)    

    ## draw OCR result under the text box
    cv2.putText(img_copy, "OCR: " + ocr_text, (text_x1, text_y2 + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1 )


    ## clean OCR text
    ocr_text_clean = ocr_text.strip().lower()
    expected_ocr_text_clean = expected_ocr_text.strip().lower()


    ## Check OCR Value
    ocr_value_pass = ocr_text_clean == expected_ocr_text_clean

    if ocr_value_pass:
        print("OCR Value: PASS")
    else:
        print("OCR Value: Fail")


    ## draw QR outline
    for i in range(4):
        pt1 = tuple(qr_points[i])
        pt2 = tuple(qr_points[(i + 1) % 4])
        cv2.line(img_copy, pt1, pt2, (255, 0, 0), 2)

    ## check QR value
    qr_value_pass = qr_value == expected_text

    if qr_value_pass and ocr_value_pass:
        print("PASS DETECTED")
        print("QR Finder: PASS")
        print("QR Value: PASS")
        cv2.putText(img_copy, "PASS", (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        print("FAIL DETECTED")
        print("QR Finder: PASS")
        print("QR Value: FAIL")
        cv2.putText(img_copy, "FAIL", (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    print("QR value:", qr_value)
    print("Expected:", expected_text)
    print("QR value length:", len(qr_value))
    print("Expected length:", len(expected_text))

else:
    print("FAIL DETECTED")
    print("QR Finder: FAIL")
    print("QR Value: FAIL")

    cv2.putText(img_copy, "FAIL", (50, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


## show final image
cv2.imshow("QR Inspection", img_copy)

cv2.waitKey(0)
cv2.destroyAllWindows()