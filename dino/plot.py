import typing as t
from collections import deque

import matplotlib

matplotlib.rcParams["toolbar"] = "toolmanager"
from matplotlib.backend_tools import ToolToggleBase
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from numpy import diff

from dino.buffer import BUFFER_MINUTES
from dino.openscale_serial.openscale_reader import SAMPLES_PER_SEC

# Look, I don't like having this global either, but if matplotlib is going to do everything as singletons,
# I guess I will too
ANIMATION = None


def pause():
    if ANIMATION is not None:
        ANIMATION.pause()


def resume():
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


class Plotter:
    def __init__(self, n_derivates=1):
        self.figure = plt.figure()
        self.plot = self.figure.add_subplot(1, 1, 1)
        self.series: t.Dict[str, t.Deque[t.Tuple]] = {}
        self.n_derivatives = n_derivates

        tm = self.figure.canvas.manager.toolmanager
        self.figure.canvas.manager.toolmanager.add_tool("Pause", PauseTool)
        self.figure.canvas.manager.toolbar.add_tool(tm.get_tool("Pause"), "toolgroup")

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
            #
            # for x, d in zip(xs[1 :], derivatives[0]):
            #     if d > 10:
            #         self.plot.vlines(x=x, ymin=-500, ymax=500, colors="red")
            #     if d < -10:
            #         self.plot.vlines(x=x, ymin=-500, ymax=500, colors="green")

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

    def pause(self, _event):
        pause()

    def resume(self, _event):
        resume()
