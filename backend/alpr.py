import requests
import cv2

API_TOKEN = "YOUR_API_KEY"
API_URL = "https://api.platerecognizer.com/v1/plate-reader/"


def crop_number_plate(image_path):
    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(blur, 30, 200)

    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    for c in contours:
        approx = cv2.approxPolyDP(c, 0.018 * cv2.arcLength(c, True), True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(c)
            if 2 < w/h < 6:
                return image[y:y+h, x:x+w]

    return None


def recognize_plate(image_path):
    try:
        with open(image_path, "rb") as img:
            response = requests.post(
                API_URL,
                files={"upload": img},
                headers={"Authorization": f"Token {API_TOKEN}"}
            )

        if response.status_code not in [200, 201]:
            return None, 0

        data = response.json()

        if not data.get("results"):
            return None, 0

        result = data["results"][0]

        return result["plate"].upper(), float(result["score"])

    except Exception as e:
        print("ALPR error:", e)
        return None, 0