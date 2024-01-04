import os
from kivy.factory import Factory as F
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.animation import Animation

from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivymd.uix.hero import MDHeroFrom

KV = '''
MDScreenManager:
    MDScreen:
        name: "Main Screen"
        ScrollView:
            MDGridLayout:
                id: grid
                cols: 3
                spacing: "4dp"
                padding: "4dp"
                adaptive_height: True

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
            on_release:
                root.current_heroes = [hero_to.tag]
                root.current = "Main Screen"
        MDRaisedButton:
            text: "Back"
            pos_hint: {"center_x": .5}
            y: "36dp"
            on_release:
                root.current_heroes = [hero_to.tag]
                root.current = "Main Screen"

<ImageTile>:
    size_hint_y: None
    height: "200dp"
    radius: 24

    MDSmartTile:
        id: tile
        radius: 24
        box_radius: 0, 0, 24, 24
        box_color: 0, 0, 0, .5
        size_hint: None, None
        size: root.size
        mipmap: True
        on_release: root.on_release()
'''



VALID_IMG_EXT = [".jpg",".gif",".png",".tga"]


class ImageTile(MDHeroFrom):
    def __init__(self, source, manager, **kwargs):
        super().__init__(**kwargs)
        self.ids.tile.source = source
        self.manager = manager
        self.ids.tile.ids.image.ripple_duration_in_fast = 0.05

    def on_transform_in(self, instance_hero_widget, duration):
        Animation(
            radius=[0, 0, 0, 0],
            box_radius=[0, 0, 0, 0],
            duration=duration,
        ).start(instance_hero_widget)

    def on_transform_out(self, instance_hero_widget, duration):
        Animation(
            radius=[24, 24, 24, 24],
            box_radius=[0, 0, 24, 24],
            duration=duration,
        ).start(instance_hero_widget)

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
            path = os.path.join(os.path.expanduser('~'), "OneDrive\Images")
        else:
            path = os.path.join(os.path.expanduser('~'), "/Pictures")

        self.images_list = []
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1].lower()
            if ext in VALID_IMG_EXT:
                self.images_list.append(os.path.join(path,f))
        
        for i in self.images_list:
            image_item = ImageTile(source=i, manager=self.root, tag=f"Tag {i}")
            self.root.ids.grid.add_widget(image_item)


ImageApp().run()