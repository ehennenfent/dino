import typing as t
from collections import deque

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from numpy import diff

from dino.openscale_serial.openscale_reader import SAMPLES_PER_SEC, BUFFER_MINUTES


class Plotter:
    def __init__(self):
        self.figure = plt.figure()
        self.plot = self.figure.add_subplot(1, 1, 1)
        self.series: t.Dict[str, t.Deque[t.Tuple]] = {}
        self.animation = None

        axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
        axnext = plt.axes([0.81, 0.05, 0.1, 0.075])

        # axcalib = plt.axes([0.81, 0.05, 0.1, 0.075])

        self.bnext = Button(axnext, "Pause")
        self.bnext.on_clicked(self.pause)
        self.bprev = Button(axprev, "Resume")
        self.bprev.on_clicked(self.resume)
        # self.b = Button(axprev, "Resume")
        # self.bprev.on_clicked(self.resume)

    def _draw(self, _i):
        """Called once per interval to update the displayed graph"""
        self.plot.clear()
        for label, data in self.series.items():
            xs = [i[0] for i in data]
            ys = [i[1] for i in data]

            self.plot.plot(xs, ys, label=label)

            derivatives = []
            for nth in range(2):
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
        self.animation = animation.FuncAnimation(
            self.figure, self._draw, interval=interval
        )
        plt.show()

    def get_differentiable_series(self, key: str) -> t.Deque[t.Tuple]:
        return self.series.setdefault(
            key, deque(maxlen=SAMPLES_PER_SEC * 60 * BUFFER_MINUTES)
        )

    def stop(self):
        plt.close(self.figure)

    def pause(self, _event):
        if self.animation is not None:
            self.animation.pause()

    def resume(self, _event):
        if self.animation is not None:
            self.animation.resume()
