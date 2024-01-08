import os
import yaml

from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore


from kivymd.app import MDApp
from kivymd.uix.hero import MDHeroFrom
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp


VALID_IMG_EXT = [".jpg",".png",".tga"]

class ClickableImage(RectangularRippleBehavior, ButtonBehavior, AsyncImage):
    pass


class ImageTile(MDHeroFrom):
    def __init__(self, source, manager, **kwargs):
        super().__init__(**kwargs)
        self.ids.tile.source = source
        self.manager = manager

    def on_release(self):
        def switch_screen(*args):
            self.manager.current_heroes = [self.tag]
            self.manager.ids.hero_to.tag = self.tag
            self.manager.current = "Photo Screen"

        Clock.schedule_once(switch_screen, 0.2)


class ImageApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('data.json')
        if 'photos' in self.store:
            self.images_list = self.store['photos']
        else:
            self.images_list = {}

        self.models = yaml.safe_load("model_config.yml")

    def build(self):
        Window.bind(on_request_close=self.exit)

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
                self.images_list[image_path] = False
        
        for i, (im, drawn) in enumerate(self.images_list.items()):
            if(not drawn):
                image_item = ImageTile(source=im, manager=self.root, tag=im)
                self.root.ids.grid.add_widget(image_item)

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


    def clearimages(self):
        self.images_list = {}
        self.root.ids.grid.clear_widgets()

    def superresolution(self):
        pass

    def objectremoval(self):
        pass

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