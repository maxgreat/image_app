import os
#os.environ['KIVY_IMAGE'] = 'PIL'
from kivy.factory import Factory as F
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.animation import Animation
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.fitimage import FitImage
from kivy.uix.image import AsyncImage, Image

from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivymd.uix.hero import MDHeroFrom
from kivymd.uix.screen import MDScreen


KV = '''
MDScreenManager:
    id: screenManager
    MDScreen:
        name: "Main Screen"
        ScrollView:
            MDGridLayout:
                id: grid
                cols: 3
                spacing: "4dp"
                padding: "4dp"
                adaptive_height: True
        MDSlider:
            id: slider
            pos_hint: {"center_x": .5, "center_y": .1}
            size_hint: .5, .1
            min: 1
            max: 10
            value: 3
            step: 1
            on_value: app.slider_down(*args)

    MDScreen:
        name: "Photo Screen"
        heroes_to: [hero_to]
        MDHeroTo:
            id: hero_to
            size_hint: 1, 1
            pos_hint: {"center_x": 0.5, "center_y":0.5}
        MDRaisedButton:
            text: "Super Resolution"
            pos_hint: {"center_x": .2}
            y: "36dp"
            on_release: app.next_image()
        MDRaisedButton:
            text: "Back"
            pos_hint: {"center_x": .5}
            y: "36dp"
            on_release:
                root.current_heroes = [hero_to.tag]
                root.current = "Main Screen"

<ImageTile>:
    size_hint_y: None
    size_hint_x: 1
    height: "200dp"
    radius: 24
    ClickableImage:
        id: tile
        size_hint: None, None
        size: root.size
        on_release: root.on_release()
        mipmap: True
        opacity : 1
'''



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
    def build(self):
        return Builder.load_string(KV)
    
    def on_start(self):
        self.images_list = []
        if platform == 'android':
            from android.storage import primary_external_storage_path
            SD_CARD = primary_external_storage_path()
            path = '/storage/emulated/0/Pictures/'
        elif platform == 'win':
            path = os.path.join(os.path.expanduser('~'), "OneDrive/Images")
        else:
            path = os.path.join(os.path.expanduser('~'), "/Pictures")

        self.images_list = []
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1].lower()
            if ext in VALID_IMG_EXT:
                self.images_list.append(os.path.join(path,f))
        
        for i, im in enumerate(self.images_list):
            image_item = ImageTile(source=im, manager=self.root, tag=f"{i}")
            self.root.ids.grid.add_widget(image_item)

    def slider_down(self, slider, value):
        self.root.ids.grid.cols = value


    def superresolution(self):
        pass


ImageApp().run()