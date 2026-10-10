import logging
from pathlib import Path
import imgui
import moderngl_window as mglw

from in3d.imgui import ImguiModernglWindowRenderer
from imgui.integrations import compute_fb_scale


class WindowEvents(mglw.WindowConfig):
    gl_version = (3, 3)
    title = None
    resource_dir = (Path(__file__).parent / "resources").resolve()
    aspect_ratio = None
    samples = 4
    log_level = logging.INFO

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.wnd.ctx.error

        # io.ConfigWindowsMoveFromTitleBarOnly
        self.imgui = ImguiModernglWindowRenderer(self.wnd)
        # io = imgui.get_io()
        # io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
        # io.font_global_scale = 2.0

        # io.config_windows_move_from_title_bar_only = True
        # self.font = io.fonts.add_font_from_file_ttf(
        #     "resources/fonts/DroidSans.ttf",
        #     14,
        # )
        # self.imgui.refresh_font_texture()

        self.ctx.front_face = "ccw"

    def render(self, t: float, ft: float):
        pass

    def resize(self, width: int, height: int):
        self.imgui.resize(width, height)

    def key_event(self, key, action, modifiers):
        self.imgui.key_event(key, action, modifiers)

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)

    # moderngl-window >= 3 only binds the on_* callbacks; forward them to the 2.x names above, which subclasses override
    def on_render(self, time: float, frame_time: float):
        self.render(time, frame_time)

    def on_resize(self, width: int, height: int):
        self.resize(width, height)

    def on_key_event(self, key, action, modifiers):
        self.key_event(key, action, modifiers)

    def on_mouse_position_event(self, x, y, dx, dy):
        self.mouse_position_event(x, y, dx, dy)

    def on_mouse_drag_event(self, x, y, dx, dy):
        self.mouse_drag_event(x, y, dx, dy)

    def on_mouse_scroll_event(self, x_offset, y_offset):
        self.mouse_scroll_event(x_offset, y_offset)

    def on_mouse_press_event(self, x, y, button):
        self.mouse_press_event(x, y, button)

    def on_mouse_release_event(self, x: int, y: int, button: int):
        self.mouse_release_event(x, y, button)

    def on_unicode_char_entered(self, char):
        self.unicode_char_entered(char)

    def set_font_scale(self, scale, font_size=15):
        # TODO: Only tested on ubuntu
        io = imgui.get_io()
        io.config_windows_move_from_title_bar_only = True
        io.fonts.clear()
        self.font = io.fonts.add_font_from_file_ttf(
            (self.resource_dir / "fonts/Cousine-Regular.ttf").as_posix(),
            font_size * scale,
        )
        self.imgui.refresh_font_texture()

        # !required for ubuntu
        self.wnd._width = self.wnd.buffer_width
        self.wnd._height = self.wnd._buffer_height
        # io.font_global_scale = scale

        io.display_size = self.wnd.size
        io.display_fb_scale = compute_fb_scale(self.wnd.size, self.wnd.buffer_size)
