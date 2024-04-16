import os
from PIL import Image
import cv2
import insightface
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
import uuid
import tqdm


app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0)

if not os.path.exists("inswapper_128.onnx"):
    import wget
    url = 'https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx?download=true'
    wget.download(url)    

swapper = insightface.model_zoo.get_model('inswapper_128.onnx')

def get_faces(img: Image.Image):
    if not os.path.exists('temp/'):
        os.mkdir('temp')
    new_file_name = f'temp/{uuid.uuid4()}.png'
    img.save(new_file_name)
    img_png = cv2.imread(new_file_name)
    return app.get(img)

def swap_face(frame, faces, reference_face):
    for face in faces:
        frame = swapper.get(frame, face, reference_face, paste_back=True)
    return frame


def swapfaces(img : Image.Image, reference_face) -> Image.Image:
    output_image_path = str(uuid.uuid4().bytes) + ".gif"
    duration = []
    list_image = []
    if not hasattr(img, 'n_frames'):
        n_frames = 1
    else:
        n_frames = img.n_frames
    for i in tqdm.tqdm(range(n_frames)):
        img.seek(i)
        try:
            duration.append(img.info['duration'])
        except Exception:
            duration.append(0)
        if not os.path.exists('temp/'):
            os.mkdir('temp')
        new_file_name = f'temp/{output_image_path}_{i}.png'
        img.save(new_file_name)
        img_png = cv2.imread(new_file_name)
        faces = app.get(img_png)
        frame = swap_face(img_png, faces, reference_face)
        cv2.imwrite(new_file_name, frame)
        list_image.append(new_file_name)
    image_output = Image.open(list_image[0])
    image_output.save(output_image_path, save_all=True, append_images=[Image.open(i) for i in list_image[1:]], duration=duration, loop=0)
    [os.remove(i) for i in list_image]
    return image_output
                
