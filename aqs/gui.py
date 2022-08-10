# fmt: off
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
# fmt: on

import cairo


class TransparentWindow(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect("draw", self._draw)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

    def _draw(self, widget, context):
        context.set_source_rgba(0, 0, 0, 0)
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)
