import requests

# Your Plate Recognizer API token
API_TOKEN = "d8b405abf7a3838210db75014eedfd9ec752b97e"


def recognize_plate(image_path):
    """
    Sends an image to Plate Recognizer API
    Returns detected plate and confidence score
    """

    url = "https://api.platerecognizer.com/v1/plate-reader/"

    with open(image_path, "rb") as image_file:

        response = requests.post(
            url,
            files={"upload": image_file},
            headers={"Authorization": "Token " + API_TOKEN}
        )

    data = response.json()

    if data["results"]:

        plate = data["results"][0]["plate"]
        confidence = data["results"][0]["score"]

        return plate.upper(), confidence

    return None, 0