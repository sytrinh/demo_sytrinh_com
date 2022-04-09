import base64
import io
import os
import re
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import (
    Blueprint, render_template, request, jsonify
)


bp = Blueprint('digit_recognizer', __name__)

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
ml_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mlmodels/mist_cnn_augmentation_2.keras')
ml_model = tf.keras.models.load_model(ml_name)


@bp.route('/digit_recognizer')
def load():
    data = {
    'title': 'Digit Recognizer'
    }
    return render_template('digit_recognition.html', data=data)


def preprocess_image(image):
    # convert image to gray scale mode
    image = image.convert("L")

    # Crop to content area
    image = np.array(image)
    image = np.pad(image, (image.shape,image.shape), 'constant', constant_values=255) # avoid negative numbers (x0-delta) or (y0-delta)
    coords = np.argwhere(image < 255)
    if len(coords) == 0:
        return None
    x0, y0 = coords.min(axis=0)
    x1, y1 = coords.max(axis=0)+1 # # slices are exclusive at the top
    if (y1-y0) > (x1-x0):
        delta = int(((y1-y0) - (x1-x0))/2)
        x0 = max(0, x0-delta)
        x1 = min(image.shape[1]-1, x1+delta)
    elif (y1-y0) < (x1-x0):
        delta = int(((x1-x0) - (y1-y0))/2)
        y0 = max(0, y0-delta)
        y1 = min(image.shape[0]-1, y1+delta)
    cropped = image[x0:x1, y0:y1]

    image = Image.fromarray(cropped)
    image = image.resize((28, 28))
    image = np.array(image)
    # invert image
    image = 255 - image
    return image

@bp.route('/digit_recognizer/predict', methods=["POST"])
def predict():
    data = request.get_json(force=True)
    encoded = data["image"]
    imgstr = re.search(r"base64,(.*)", encoded).group(1)
    decoded = base64.b64decode(imgstr)
    image = Image.open(io.BytesIO(decoded))
    image = preprocess_image(image)
    if image is None:
        result = {'label': 'unidentified',
                    'confidence': 'unidentified',
                    'label_size': 1}
        return jsonify(result)
    image = image.reshape(1, 28, 28, 1)
    # make prediction with the model
    prediction = ml_model.predict(image).reshape(-1)
    prob = prediction.tolist()
    prob = [format(num, ".4f") for num in prob]
    label = np.argmax(prob).tolist()
    confidence = prob[label]
    result = {
    'label': label,
    'confidence': confidence
    }
    return jsonify(result)
