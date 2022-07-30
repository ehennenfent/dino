import typing as t

import matplotlib.animation as animation
import matplotlib.pyplot as plt


class Plotter:
    def __init__(self):
        self.figure = plt.figure()
        self.plot = self.figure.add_subplot(1, 1, 1)
        self.series: t.Dict[str, t.List[t.Tuple]] = {}
        self.animation = None

    def _draw(self, _i):
        """Called once per interval to update the displayed graph"""
        self.plot.clear()
        for label, data in self.series.items():
            xs = [i[0] for i in data]
            ys = [i[1] for i in data]

            self.plot.plot(xs, ys, label=label)

        # Format plot
        plt.xticks(rotation=45, ha="right")
        plt.subplots_adjust(bottom=0.30)
        plt.title("Openscale reading")
        plt.ylabel("Pounds")

    def animate(self, interval=1000):
        self.animation = animation.FuncAnimation(
            self.figure, self._draw, interval=interval
        )
        plt.show()

    def get_series(self, key: str) -> t.List[t.Tuple]:
        return self.series.setdefault(key, list())

    def stop(self):
        plt.close(self.figure)
