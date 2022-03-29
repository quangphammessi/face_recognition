import os
import sys
import base64
import cv2
import numpy as np

from fastapi import FastAPI, Request, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

sys.path.append('src')

from apps.demo import Demo



# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
camera_address = 0


app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# @app.route('/', methods=['GET'])
@app.get('/', tags=['root'], response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request, 'image_name': 'nothing', 'result': None})


# @app.post('/upload-image')
# async def upload_image(file: bytes = File(...)):
#     content = await file.read()
#     return {'file-size': file}


@app.post('/predict')
async def predict(request: Request, file: UploadFile = File(...)):
    try:
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, '../uploads', file.filename)

        content = await file.read()

        image = np.asarray(bytearray(content), dtype='uint8')
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        demo = Demo(camera_address=image)
        demo.run()

        retval, buffer = cv2.imencode('.jpg', demo.detected_face)
        encoded_string = base64.b64encode(buffer)
        bs64 = encoded_string.decode('utf-8')
        result = {
            'image_data': f'data:image/jpeg;base64,{bs64}'
        }

            # f.save(file_path)

            # test(file_path)

            # out_name = f.filename.split('.')[0]
    except Exception as e:
        print(e)

    return templates.TemplateResponse('index.html', context={'request': request, 'image_name': 'nothing', 'result': result})


# @app.post('/predict')
# async def predict():
#     if request.method == 'POST':
#         f = request.files['file']

#         basepath = os.path.dirname(__file__)
#         file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
#         f.save(file_path)

#         test(file_path)

#         out_name = f.filename.split('.')[0]

#         # return 'Done'
#     # return render_template('index.html', image_name='0.jpg')
#     return jsonify(image_name=out_name)


if __name__ == '__main__':
    app.run(debug=True)