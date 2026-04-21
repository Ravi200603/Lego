from flask import Flask, request, send_file, Response
import cv2
import numpy as np
import io
import random
from flask_cors import CORS

try:
    from main import run_generator as run_generator
except Exception:
    main = None

app = Flask(__name__)
CORS(app)

@app.route('/lego', methods=['POST'])

#routes to main.py to start the lego pattern generator process
def logo():
    if 'image' not in request.files:
        return {"error": "No image uploaded"}, 400

    file = request.files['image']

    #decode the image
    img_bytes = file.read()
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Invalid image"}, 400

    result = run_generator(img)

    success, buffer = cv2.imencode('.jpg', result)
    print("Buffer size:", len(buffer))
    if not success:
        return {"error": "Encoding failed"}, 500

    return send_file(
      io.BytesIO(buffer.tobytes()),
      mimetype='image/jpeg',
      download_name='result.jpg'
    )

if __name__ == '__main__':
    app.run(debug=True)