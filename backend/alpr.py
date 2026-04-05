import requests

# Plate Recognizer API token
API_TOKEN = "d8b405abf7a3838210db75014eedfd9ec752b97e"

API_URL = "https://api.platerecognizer.com/v1/plate-reader/"


def recognize_plate(image_path):
    """
    Sends an image to Plate Recognizer API.

    Parameters
    ----------
    image_path : str
        Path of the vehicle image

    Returns
    -------
    plate : str or None
        Detected license plate

    confidence : float
        Detection confidence score
    """

    try:

        with open(image_path, "rb") as image_file:

            response = requests.post(
                API_URL,
                files={"upload": image_file},
                headers={
                    "Authorization": f"Token {API_TOKEN}"
                }
            )

        # check if request succeeded
        if response.status_code not in [200, 201]:
          print("ALPR API error:", response.status_code)
          return None, 0

        data = response.json()

        if not data.get("results"):
            return None, 0

        result = data["results"][0]

        plate = result["plate"].upper()

        confidence = float(result["score"])

        return plate, confidence

    except Exception as e:

        print("ALPR processing error:", e)

        return None, 0