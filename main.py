import os
import yaml
import requests
from PIL import Image as PILImage

from utils.faces import get_faces

from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color



from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.behaviors import RectangularRippleBehavior

from kivy.logger import Logger

DELAY_LOADING = 4
VALID_IMG_EXT = [".jpg",".png",".tga", ".gif"]

class ClickableImage(RectangularRippleBehavior, ButtonBehavior, AsyncImage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tag = self.source
        self.app = MDApp.get_running_app()
        self.rects =  [(100, 100, 150, 150), (300, 200, 100, 50)]
        self.rectangles = []
        self.bind(pos=self.update_rects, size=self.update_rects)
        Clock.schedule_interval(self.handle_load_failure, DELAY_LOADING)

    def handle_load_failure(self, warning):
        if not self.texture:
            self.app.root.ids.grid.remove_widget(self)

    def on_release(self):
        self.app.root.ids.photoshown.source = self.source
        self.app.currentphoto = self.tag
        self.app.root.current = "Photo Screen"
    
    def on_kv_post(self, base_widget):
        if hasattr(self, 'rect'):
            with self.canvas.after:
                Color(1, 0, 0, 0.5)  # Red color with 50% opacity
                for rect in self.rects:
                    print("Drawing rect", rect)
                    x, y, w, h = rect
                    rectangle = Rectangle(pos=(self.x + x, self.y + y), size=(w, h))
                    self.rectangles.append(rectangle)

    def update_rects(self, *args):
        for rectangle, rect in zip(self.rectangles, self.rects):
            x, y, w, h = rect
            rectangle.pos = (self.x + x, self.y + y)
            rectangle.size = (w, h)
    


class ImageResultPopup(Popup):
    def save_image(self, *args):
        from plyer import filechooser
        filechooser.save_file(MDApp.get_running_app().currentphoto)


class SupperResolutionOptions(BoxLayout):
    def __init__(self, image_size, **kwargs):
        super().__init__(**kwargs)
        self.keepratio = True
        self.ratio = image_size[0]/image_size[1]
        self.ids.width_slider.max = image_size[0]
        self.ids.width_slider.value = image_size[0]
        self.ids.height_slider.max = image_size[1]
        self.ids.height_slider.value = image_size[1]
        self.ids.width_slider.bind(value=self.onWidthChange)
        self.ids.height_slider.bind(value=self.onHeightChange)

    def onWidthChange(self, slider, value):
        if self.ids.switch.value:
            new_height = int(value / self.ratio)
            self.ids.height_slider.value = new_height

    def onHeightChange(self, slider, value):
        if self.ids.switch.value:
            new_width = int(value * self.ratio)
            self.ids.width_slider.value = new_width

    def checkboxChange(self, checkbox, value):
        self.keepratio = value


class ImageGenerationOptions(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ImageToVidOptions(BoxLayout):
    def __init__(self, image_size, **kwargs):
        super().__init__(**kwargs)
        self.keepratio = True
        self.ratio = image_size[0]/image_size[1]
        self.ids.width_slider.max = image_size[0]
        self.ids.width_slider.value = image_size[0]
        self.ids.height_slider.max = image_size[1]
        self.ids.height_slider.value = image_size[1]
        self.ids.width_slider.bind(value=self.onWidthChange)
        self.ids.height_slider.bind(value=self.onHeightChange)
    
    def onWidthChange(self, slider, value):
        if self.ids.switch.value:
            new_height = int(value / self.ratio)
            self.ids.height_slider.value = new_height

    def onHeightChange(self, slider, value):
        if self.ids.switch.value:
            new_width = int(value * self.ratio)
            self.ids.width_slider.value = new_width

    def checkboxChange(self, checkbox, value):
        self.keepratio = value


class AsyncNotLoadedImage(AsyncImage):
    '''
        Handle the loading of the image from the server, waiting for the task to be done
    '''
    def poll_image_availability(self, url):
        def get_result(*args):
                response = requests.get(url)
                data = response.json()

                if data['state'] == 'SUCCESS':
                    self.source = data['result']
                elif data['state'] == 'PENDING':
                    Clock.schedule_once(get_result, 1)
                else:
                    pass #see what to do if generation fail

        # Assuming 'task_id' is received from the initial prediction request
        Clock.schedule_once(get_result, 1)


class ImageApp(MDApp):
    def build_config(self, config):
        config.setdefaults('kivy', {
            'log_level': 'warning'
        })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('data.json')
        if 'photos' in self.store:
            self.images_list = {im:-1 for im in self.store['photos']}
        else:
            self.images_list = {}
            self.store['photos'] = {}
        self.currentphoto: str = None
        
        with open("model_config.yml", 'r') as file:
            self.models = yaml.safe_load(file)

        menu_items = [
                    {
                        "viewclass": "OneLineListItem",
                        "text": "Generate Image",
                        "height": dp(56),
                        "on_release": lambda : self.generate_image(),
                    },
                    {
                        "viewclass": "OneLineListItem",
                        "text": "Clear Images",
                        "height": dp(56),
                        "on_release": lambda : self.clearimages(),
                    },
                    {
                        "viewclass": "OneLineListItem",
                        "text": "Exit",
                        "height": dp(56),
                        "on_release": lambda : self.exit(),
                    }
                ]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        )

        singles_items = [
                    {
                        "viewclass": "OneLineListItem",
                        'text': 'Detect Faces',
                        "height": dp(56),
                        "on_release": lambda : self.detect_faces(),
                    },
                    {
                        "viewclass": "OneLineListItem",
                        "text": "Super Resolution",
                        "height": dp(56),
                        "on_release": lambda : self.call_superresolution(),
                    },
                    {
                        "viewclass": "OneLineListItem",
                        "text": 'Image to Video',
                        "height": dp(56),
                        "on_release": lambda : self.call_image2vid(),
                    },
                ]
        self.singlemenu = MDDropdownMenu(
            items=singles_items,
            width_mult=4,
        )
        



    def build(self):
        Window.bind(on_request_close=self.exit)
        return Builder.load_file('main.kv')
    
    def on_start(self):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            from android.storage import app_storage_path
            self.settings_path = app_storage_path()
            SD_CARD = primary_external_storage_path()
            path = '/storage/emulated/0/Pictures/'
        elif platform == 'win':
            self.settings_path = self.user_data_dir
            path = os.path.join(os.path.expanduser('~'))
        else:
            path = os.path.join(os.path.expanduser('~'), "/Pictures")
        self.add_images(path)
        self.root.ids.faces_container.opacity = 0  # Hide ScrollView if no faces
        
    def add_images(self, path: str):
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1].lower()
            image_path = os.path.join(path,f)
            if ext in VALID_IMG_EXT and not(image_path in self.images_list) :
                self.images_list[image_path] = -1
        self.store['photos'] = self.images_list
                
        
        for i, im in enumerate(self.images_list):
            if(self.images_list[im] == -1):
                print("Adding image :", im)
                image_item = ClickableImage(source=im)
                self.images_list[im] = i
                self.root.ids.grid.add_widget(image_item)
            else:
                print("Already drawn")

    def slider_down(self, slider, value):
        self.root.ids.grid.cols = value
        for child in self.root.ids.grid.children:
            child.height = str(int(200*3/value)) + 'dp'

    def mainmenu(self, button):
        self.menu.caller = button
        self.menu.open()

    def photomenu(self, button):
        self.singlemenu.caller = button
        self.singlemenu.open()

    def clearimages(self):
        self.images_list = {}
        self.root.ids.grid.clear_widgets()

    def call_url(self, url, data=None, files=None):
        try:
            print("Reaching :", url)
            response = requests.post(url, data=data, files=files)
        except Exception as e:
            Snackbar(
                text="Cannot access server :" + str(e),
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(
                    Window.width - (dp(10) * 2)
                ) / Window.width
            ).open()
            return
        if response.status_code == 200:
            image_url = response.json()['image_url']
            p = ImageResultPopup(title='Result')
            p.ids.image.poll_image_availability(image_url)
            p.open()
        else:
            Snackbar(
                    text=f"Failed. Status code: {response.status_code} - Message: {response.text}",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(
                        Window.width - (dp(10) * 2)
                    ) / Window.width
                ).open()

    def detect_faces(self):
        pil_image = PILImage.open(self.currentphoto)
        self.faces = get_faces(pil_image)
        for i, face in enumerate(self.faces):
            bbox = face['bbox']
            crop_box = (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))
            face_image = pil_image.crop(crop_box)
            face_image.save(f'face{i}.jpg')
        #self.add_images_face()


    def call_superresolution(self):
        if(self.currentphoto is None):
            return    

        width, height = PILImage.open(self.currentphoto).size
        if width > 1024 or height > 1024:
            if width > height:
                new_width = 1024
                new_height = int(new_width * height / width)
            else:
                new_height = 1024
                new_width = int(new_height * width / height)
        else:
            new_width, new_height = width, height
        self.dialog = MDDialog(
                text="Send Image to Server",
                type="custom",
                content_cls=SupperResolutionOptions((new_width, new_height)),
                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.dissmiss_dialog,
                    ),
                    MDFlatButton(
                        text="Send",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.send_superresolution_image,
                    ),
                ],
            )
        self.dialog.open()
    
    def call_image2vid(self):
        if(self.currentphoto is None):
            return
        image_size = PILImage.open(self.currentphoto).size
        self.dialog = MDDialog(
                text="Send Image to Server",
                type="custom",
                content_cls=ImageToVidOptions(image_size),
                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.dissmiss_dialog,
                    ),
                    MDFlatButton(
                        text="Send",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press= self.send_image2vid
                    ),
                ],
            )
        self.dialog.open()

    def generate_image(self, *args):
        self.dialog = MDDialog(
                title="Image Generation Options",
                type="custom",
                content_cls=ImageGenerationOptions(),
                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.dissmiss_dialog,
                    ),
                    MDFlatButton(
                        text="Send",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.send_generate_image,
                    ),
                ],
            )
        self.dialog.update_height()
        self.dialog.open()

    
    def dissmiss_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def send_superresolution_image(self, *args):
        print('Sending Image to the server with options :', self.dialog)
        image_path = self.currentphoto
        files = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        self.dialog.dismiss()
        self.call_url(self.models['superresolution']['url'], files=files)

    def send_generate_image(self, *args):
        print('Sending Image to the server with options :', self.dialog.content_cls.ids)
        data = {'prompt': self.dialog.content_cls.ids.prompt.text, 'neg_prompt':self.dialog.content_cls.ids.neg_prompt.text, 
                'width': self.dialog.content_cls.ids.width_slider.value, 'height': self.dialog.content_cls.ids.height_slider.value,
                'num_interation': self.dialog.content_cls.ids.it_slider.value}
        self.dialog.dismiss()
        self.call_url(self.models['imagegeneration']['url'], data=data)
    
    def send_image2vid(self, *args):
        print('Sending Image to the server with options :', self.dialog)
        self.dialog.dismiss()
        image_path = self.currentphoto
        files = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        self.call_url(self.models['image2vid']['url'], files=files)

    def save_image(self):
        from plyer import filechooser
        path = filechooser.save_file(self.currentphoto)
        

    def add_repo(self):
        from plyer import filechooser
        path = filechooser.choose_dir()
        if(len(path) > 0):
            print(path)
            self.add_images(path[0])

    def exit(self, *args):
        self.store['photos'] = self.images_list
        self.stop()


ImageApp().run()