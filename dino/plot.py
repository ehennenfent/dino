import platform
import typing as t
from collections import deque

import matplotlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.backend_tools import ToolToggleBase
from numpy import diff

from dino.buffer import BUFFER_MINUTES
from dino.openscale_serial.openscale_reader import SAMPLES_PER_SEC

if platform.system().lower() == "windows":
    matplotlib.rcParams["toolbar"] = "toolmanager"

# Look, I don't like having this global either, but if matplotlib is going to do everything as singletons,
# I guess I will too
ANIMATION = None
paused = False


def pause():
    global paused
    paused = True
    if ANIMATION is not None:
        ANIMATION.pause()


def resume():
    global paused
    paused = False
    if ANIMATION is not None:
        ANIMATION.resume()


class PauseTool(ToolToggleBase):
    """Temporarily stop the data from scrolling"""

    default_keymap = " "
    description = "Pause autoscroll"
    default_toggled = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def enable(self, *args):
        pause()

    def disable(self, *args):
        resume()


def on_press(event):
    if event.key == " ":
        if not paused:
            pause()
        else:
            resume()


class Plotter:
    def __init__(self, n_derivates=1):
        self.figure = plt.figure()
        self.plot = self.figure.add_subplot(1, 1, 1)
        self.series: t.Dict[str, t.Deque[t.Tuple]] = {}
        self.n_derivatives = n_derivates
        self.vertical_lines = []

        if platform.system().lower() == "windows":
            try:
                tm = self.figure.canvas.manager.toolmanager
                self.figure.canvas.manager.toolmanager.add_tool("Pause", PauseTool)
                self.figure.canvas.manager.toolbar.add_tool(
                    tm.get_tool("Pause"), "toolgroup"
                )
            except AttributeError:
                print("Toolbar modification not supported on this platform")
        elif platform.system().lower() == "darwin":
            self.figure.canvas.mpl_connect("key_press_event", on_press)

    def _draw(self, _i):
        """Called once per interval to update the displayed graph"""
        self.plot.clear()
        for label, data in self.series.items():
            xs = [i[0] for i in data]
            ys = [i[1] for i in data]

            self.plot.plot(xs, ys, label=label)

            derivatives = []
            for nth in range(self.n_derivatives):
                derivatives.append(diff(ys, nth + 1))
                self.plot.plot(
                    xs[nth + 1 :], derivatives[nth], label=label + "_prime" * (nth + 1)
                )

        for x, color in self.vertical_lines:
            self._render_vertical_line(x, color)

        # Format plot
        plt.xticks(rotation=45, ha="right")
        plt.subplots_adjust(bottom=0.30)
        plt.title("Openscale reading")
        plt.ylabel("Pounds")
        if self.series:
            self.plot.legend()

    def animate(self, interval=1000):
        global ANIMATION
        ANIMATION = animation.FuncAnimation(self.figure, self._draw, interval=interval)
        plt.show()

    def get_differentiable_series(self, key: str) -> t.Deque[t.Tuple]:
        return self.series.setdefault(
            key, deque(maxlen=SAMPLES_PER_SEC * 60 * BUFFER_MINUTES)
        )

    def stop(self):
        plt.close(self.figure)

    @staticmethod
    def pause(_event):
        pause()

    @staticmethod
    def resume(_event):
        resume()

    def draw_vertical_line(self, x, color="red"):
        self.vertical_lines.append((x, color))

    def _render_vertical_line(self, x, color="red"):
        self.plot.vlines(x=x, ymin=-50, ymax=50, colors=color)
