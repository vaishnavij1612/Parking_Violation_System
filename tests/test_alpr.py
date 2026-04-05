from backend.alpr import recognize_plate

# path to your test image
image_path = "car.png"

plate, confidence = recognize_plate(image_path)

print("Detected Plate:", plate)
print("Confidence:", confidence)