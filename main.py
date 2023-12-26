from kivy.app import App
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import platform
if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_MEDIA_IMAGES, Permission.READ_EXTERNAL_STORAGE])
import os
import sys


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

        # Check for READ_EXTERNAL_STORAGE permission and request it if not granted
        if platform == "android":
            if not permissions.check_permission('android.permission.READ_EXTERNAL_STORAGE'):
                permissions.request_permission('android.permission.READ_EXTERNAL_STORAGE')
                return

        # Access the Android image library using Storage Access Framework
        Intent = activity.Intent
        intent = Intent()
        intent.setAction(Intent.ACTION_OPEN_DOCUMENT)
        intent.setType("image/*")
        activity.bind(on_activity_result=self.on_activity_result)
        activity.startActivityForResult(intent, 1)

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == 1:
            if resultCode == -1:  # Activity.RESULT_OK
                selected_uri = intent.getData()
                image_path = selected_uri.getPath()
                self.add_image(image_path)

    def add_image(self, image_path):
        image = Image(source=image_path, size_hint_y=None, size_hint_x=None,
                      width=(Window.width - 30) / 3, allow_stretch=True, fit_mode="contain")
        image.bind(on_touch_down=show_full_image)
        self.add_widget(image)

class MyApp(App):
    def build(self):
        self.layout = MainWindow()
        self.layout.bind(minimum_height=self.layout.setter('height'))
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        root.add_widget(self.layout)
        return root

if __name__ == "__main__":
    MyApp().run()
