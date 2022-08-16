from functools import partial

from dino.buffer import Buffer
from dino.openscale_serial.openscale_reader import SAMPLES_PER_SEC
from dino.util import extract_tail

TARE_THRESHOLD = 15.0


class PhysicsSolver:
    def __init__(self, buffer: Buffer):
        self.position = Buffer()
        self.velocity = Buffer()
        self.force = buffer

        self.tare_weight = None
        self.steady_weight = None

        self.force.register_callback(
            partial(Buffer.call_with_last_item, self.receive_force_data)
        )

    @property
    def last_second_average(self):
        return (
            sum(i[1] for i in extract_tail(self.force.buffer, SAMPLES_PER_SEC))
            / SAMPLES_PER_SEC
        )

    def calibrate_steady_state(self):
        self.velocity.clear()
        if self.tare_weight is None:
            maybe_tare = self.last_second_average
            if abs(maybe_tare) > TARE_THRESHOLD:
                raise RuntimeError(
                    f"Scale hasn't been tared, but we're reading {maybe_tare} lbs on average"
                )
            self.tare_weight = maybe_tare
        else:
            last_average = self.last_second_average
            if abs(last_average) < TARE_THRESHOLD:
                self.tare_weight = last_average
                self.steady_weight = None
            else:
                self.steady_weight = self.correct_for_tare(last_average)

    def correct_for_tare(self, force: float):
        if self.tare_weight is None:
            return force
        return force - self.tare_weight

    def deviation_from_steady(self, force: float):
        if self.steady_weight is None:
            return self.correct_for_tare(force)
        return self.correct_for_tare(force) - self.steady_weight

    def receive_force_data(self, last_item):
        def add_entry(old_entry, new_entry):
            ts, new = new_entry
            _, old = old_entry
            return ts, old + new

        if self.steady_weight is not None:
            ts, y = last_item

            if self.velocity.is_empty():
                last_velocity = (ts, 0)
            else:
                last_velocity = self.velocity.last_item
            if self.position.is_empty():
                last_position = (ts, 0)
            else:
                last_position = self.position.last_item

            self.velocity.append(
                *add_entry(last_velocity, (ts, self.deviation_from_steady(y)))
            )
            self.position.append(*add_entry(last_position, self.velocity.last_item))
