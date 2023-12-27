from kivy.app import App
from kivy.clock import Clock
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
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
        super().__init__(orientation='lr-tb', spacing=(1,1), padding=1, size_hint_y=None, **kwargs)
        self.images_list = []
        path = os.path.join(os.path.expanduser('~'), "OneDrive\Images")
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1].lower()
            if ext in VALID_IMG_EXT:
                self.images_list.append(os.path.join(path,f))
                self.add_image(os.path.join(path,f))

    def add_image(self, image_path):
        def update_ui(dt):
            image = AsyncImage(source=image_path, size_hint_y=None, size_hint_x=None, allow_stretch=True, fit_mode='scale-down')
            image.bind(on_touch_down=show_full_image)
            self.add_widget(image)
        Clock.schedule_once(update_ui)

class MyApp(App):
    def build(self):
        Window.bind(on_resize=self.on_window_resize)

        layout = MainWindow()
        layout.bind(minimum_height=layout.setter('height'))
        
        self.root = FloatLayout()
        self.scroll_view_layout = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.scroll_view_layout.add_widget(layout)
        self.root.add_widget(self.scroll_view_layout)


        floating_button = Button(
            text="+",
            size_hint=(None, None),
            size=("48dp", "48dp"),
            pos_hint={"right": 0.95, "top": 0.95}
        )
        floating_button.bind(on_press=self.on_floating_button_press)


        self.root.add_widget(floating_button)
        return self.root
     
    
    def on_window_resize(self, window, width, height):
        self.scroll_view_layout.size = (Window.width, Window.height)
    
    def on_floating_button_press():
        pass
   

if __name__ == "__main__":
    MyApp().run()
