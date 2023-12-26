from kivy.app import App
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.lang import Builder
import os

VALID_IMG_EXT = [".jpg",".gif",".png",".tga"]


def show_full_image(instance, touch):
    if instance.collide_point(*touch.pos):
        popup = Popup(title='Full Image',
                      content=Image(source=instance.source),
                      size_hint=(None, None),
                      size=(Window.width - 100, Window.height - 100))
        popup.open()

class MainWindow(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='lr-tb', spacing=10, size_hint_y=None, **kwargs)
        self.images_list = []
        path = os.path.join(os.path.expanduser('~'), "OneDrive\Images")
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1].lower()
            if ext in VALID_IMG_EXT:
                self.images_list.append(os.path.join(path,f))
                self.add_image(os.path.join(path,f))

    def add_image(self, image_path):
        image = Image(source=image_path, size_hint_y=None, size_hint_x=None,
                      width=(Window.width - 30) / 3, allow_stretch=True, fit_mode="contain")
        image.bind(on_touch_down=show_full_image)
        self.add_widget(image)

class MyApp(App):
    def build(self):
        Window.bind(on_resize=self.on_window_resize)
        layout = MainWindow()
        layout.bind(minimum_height=layout.setter('height'))
        self.root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.root.add_widget(layout)
        return self.root
     

    def on_window_resize(self, window, width, height):
        for child in self.root.children:
            print(child.pos)

if __name__ == "__main__":
    MyApp().run()
