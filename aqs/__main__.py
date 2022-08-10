import click
import os
import pulsectl
import pathlib
import typing

from enum import Enum

from aqs.gui import Gtk, Gdk, TransparentWindow


GTK_DEBUG = os.getenv("GTK_DEBUG") is not None


Node = typing.Union[pulsectl.PulseSinkInfo, pulsectl.PulseSourceInfo]


class NodeType(str, Enum):
    SOURCE = "source"
    SINK = "sink"


class AudioNodeOption(Gtk.ListBoxRow):
    def __init__(self, node: Node):
        super().__init__(name=node.name)
        self.label = Gtk.Label(label=node.description)
        self.add(self.label)
        self.get_style_context().add_class("aqs-node")
        self.node = node

    @property
    def node_type(self) -> NodeType:
        if isinstance(self.node, pulsectl.PulseSinkInfo):
            return NodeType.SINK
        return NodeType.SOURCE

    @property
    def name(self) -> str:
        return self.node.name

    def set_is_default(self, is_default: bool):
        if is_default:
            self.get_style_context().add_class("is-default")
        else:
            self.get_style_context().remove_class("is-default")


class AQSWindow(TransparentWindow):
    def __init__(self, node_type: NodeType):
        super().__init__(
            title="aqs",
            decorated=False,
            modal=True,
            resizable=False,
            window_position=3,
            icon_name="audio-headset",
            urgency_hint=True,
            type_hint=1,
        )
        self.get_style_context().add_class("aqs")

        if not GTK_DEBUG:
            # Disable auto-close on blur, since it triggers when the interactive GTK
            # inspector window comes up
            self.connect("focus-out-event", self.on_blur)
        self.connect("key-press-event", self.on_key_press)

        container = Gtk.ListBox(
            activate_on_single_click=True,
            selection_mode=2,
            can_focus=True,
            has_focus=True,
            is_focus=True,
        )
        container.connect("row-selected", self.switch_default)
        self.pa = pulsectl.Pulse()
        si = self.pa.server_info()

        if node_type == NodeType.SINK:
            nodes = self.pa.sink_list()
            default_node = si.default_sink_name
        else:
            nodes = self.pa.source_list()
            default_node = si.default_source_name
        for node in nodes:
            opt = AudioNodeOption(node)
            if opt.name == default_node:
                self.default_node_opt = opt
                opt.set_is_default(True)
            container.add(opt)
        container.select_row(self.default_node_opt)
        self.add(container)

    def on_blur(self, *args):
        self.close()

    def on_key_press(self, widget, event: Gdk.EventKey):
        if event.keyval in (Gdk.KEY_Escape, Gdk.KEY_Return):
            self.close()

    def switch_default(self, widget, target: AudioNodeOption):
        if target.node_type == NodeType.SINK:
            self.pa.sink_default_set(target.name)
        else:
            self.pa.source_default_set(target.name)
        self.default_node_opt.set_is_default(False)
        target.set_is_default(True)
        self.default_node_opt = target


def init():
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    p = pathlib.Path(__file__).parent
    styles = p / "styles.css"
    provider.load_from_path(styles.as_posix())
    Gtk.StyleContext.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )


@click.command("snamemods")
@click.option("--node-type", "-n", type=click.Choice(NodeType), default=NodeType.SINK)
def main(node_type: NodeType):
    init()
    win = AQSWindow(node_type)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
