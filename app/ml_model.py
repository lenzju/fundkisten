import tensorflow as tf
import numpy as np
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "keras_model.h5")

model = tf.keras.models.load_model(MODEL_PATH, compile=False)

CLASS_NAMES = ["Hose", "Mütze", "Pullover"]


def preprocess_image(image):

    image = image.convert("RGB")
    image = image.resize((224, 224))

    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)

    return image


def predict_category(image):

    processed = preprocess_image(image)

    prediction = model.predict(processed, verbose=0)

    predicted_class = int(np.argmax(prediction))
    confidence = float(np.max(prediction))

    if confidence < 0.6:
        return "Sonstiges"

    return CLASS_NAMES[predicted_class]
