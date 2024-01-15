import os
import yaml
import requests
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.image import AsyncImage, Image
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp
from kivy.uix.popup import Popup


from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar

from kivy.logger import Logger

DELAY_LOADING = 1


VALID_IMG_EXT = [".jpg",".png",".tga"]

class ClickableImage(RectangularRippleBehavior, ButtonBehavior, AsyncImage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tag = self.source
        self.app = MDApp.get_running_app()
        Clock.schedule_interval(self.handle_load_failure, DELAY_LOADING)

    def handle_load_failure(self, warning):
        if not self.texture:
            self.app.root.ids.grid.remove_widget(self)

    def on_release(self):
        self.app.root.ids.photoshown.source = self.source
        self.app.currentphoto = self.tag
        self.app.root.current = "Photo Screen"
    

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
        self.currentphoto = None
        
        with open("model_config.yml", 'r') as file:
            self.models = yaml.safe_load(file)

        menu_items = [
                    {
                        "viewclass": "OneLineListItem",
                        "text": "Sync Library",
                        "height": dp(56),
                        "on_release": lambda : self.synclib(),
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
                        "text": name,
                        "height": dp(56),
                        "on_release": lambda : self.call_url(self.models[name]['url']),
                    } for name in self.models
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
        
    def add_images(self, path: str):
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1].lower()
            image_path = os.path.join(path,f)
            if ext in VALID_IMG_EXT and not(image_path in self.images_list) :
                self.images_list[image_path] = -1
        
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

    def synclib(self, *args):
        """
            Upload images to the server
        """
        print("Checking missing images on server")
        pass

    def mainmenu(self, button):
        self.menu.caller = button
        self.menu.open()

    def photomenu(self, button):
        self.singlemenu.caller = button
        self.singlemenu.open()

    def clearimages(self):
        self.images_list = {}
        self.root.ids.grid.clear_widgets()

    def call_url(self, url):
        image_path = self.currentphoto
        with open(image_path, 'rb') as image:
            files = {'image': (image_path, image, 'multipart/form-data')}
            try:
                print("Reaching :", url)
                response = requests.post(url, files=files)
            except Exception as e:
                Snackbar(
                    text="Cannot access model :" + str(e),
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(
                        Window.width - (dp(10) * 2)
                    ) / Window.width
                ).open()
                return
        if response.status_code == 200:
            print("Received 200")
            with open('tmp.jpg', 'wb') as f:
                f.write(response.content)
            Popup(title='Test popup',
                content=Image(source='tmp.jpg', size_hint=(1,1)),
                size_hint=(None, None), size=(400, 400))
            '''
            from plyer import filechooser
            path = filechooser.save_file()
            with open(path, 'wb') as f:
                f.write(response.content)
            Snackbar(
                    text="Saved file :" + path,
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(
                        Window.width - (dp(10) * 2)
                    ) / Window.width
                ).open()
            '''
        else:
            Snackbar(
                    text=f"Failed. Status code: {response.status_code} - Message: {response.text}",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(
                        Window.width - (dp(10) * 2)
                    ) / Window.width
                ).open()

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