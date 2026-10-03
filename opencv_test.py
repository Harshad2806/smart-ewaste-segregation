import cv2
from ultralytics import YOLO


MODEL_PATH = "backend/models/ewaste_classifier.pt"

# Minimum confidence for accepting a prediction.
# We start at 0.55 because this worked better in our testing.
CONFIDENCE_THRESHOLD = 0.55


print("Loading e-waste classification model...")

model = YOLO(MODEL_PATH)

print("Model loaded successfully.")
print("Classes:", model.names)


camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise RuntimeError("Could not open webcam.")

print("Webcam opened.")
print("Press Q to quit.")


while True:

    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        break


    result = model.predict(
        source=frame,
        verbose=False
    )[0]

    class_id = int(result.probs.top1)
    confidence = float(result.probs.top1conf)

    predicted_class = result.names[class_id]


    if confidence >= CONFIDENCE_THRESHOLD:

        status = "E-WASTE"
        display_class = predicted_class

    else:

        status = "UNCERTAIN"
        display_class = "Unknown"


    display = frame.copy()

    # Title
    cv2.putText(
        display,
        "SMART E-WASTE AI",
        (25, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    # Prediction
    cv2.putText(
        display,
        f"Detected: {display_class}",
        (25, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 255, 0),
        2
    )

    # Confidence
    cv2.putText(
        display,
        f"Confidence: {confidence:.1%}",
        (25, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 0),
        2
    )

    # Status
    cv2.putText(
        display,
        f"Status: {status}",
        (25, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 255, 255),
        2
    )

    # Recommended stream
    if status == "E-WASTE":

        streams = {
            "electrical_cables":
                "Cable / Electronics Recycling",

            "electronic_chips":
                "Electronic Component Recycling",

            "laptops":
                "Computer / Electronics Recycling",

            "small_appliances":
                "Small Appliance Recycling",

            "smartphones":
                "Mobile / Electronics Recycling"
        }

        stream = streams.get(
            predicted_class,
            "E-Waste Recycling"
        )

        cv2.putText(
            display,
            f"Stream: {stream}",
            (25, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

    else:

        cv2.putText(
            display,
            "Place e-waste clearly in front of camera",
            (25, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )


    cv2.imshow(
        "Smart E-Waste AI",
        display
    )

    # Q = quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()

print("Application closed.")