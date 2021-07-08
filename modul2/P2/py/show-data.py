#!python3
# Copyright: 2021, Diez B. Roggisch, Berlin . All rights reserved.
import sys
import pathlib
from collections import defaultdict
from itertools import count

import plotly.graph_objects as go
import numpy as np

PROP_FREQ = 300_000_000

biggest_diff = 0
last_value = None


class PropClockTracker:

    def __init__(self, clkfreq):
        self._clkfreq = clkfreq
        self._last_timestamp = None
        self._clock = 0.0
        self.min_diff = 2**32
        self.max_diff = -2**32
        self._counter = 0

    def feed(self, timestamp):
        #timestamp <<= 8
        if self._last_timestamp is not None:
            diff = (timestamp + 2**32 - self._last_timestamp) % 2**32
            self.min_diff = min(diff, self.min_diff)
            self.max_diff = max(diff, self.max_diff)
            self._clock += diff / self._clkfreq
            if diff == self.max_diff:
                print(self._counter, diff, self._clock)

        self._last_timestamp = timestamp
        self._counter += 1
        return self._clock


def stats(value):
    global last_value, biggest_diff
    if last_value is not None:
        biggest_diff = max(biggest_diff, abs(value - last_value))
    last_value = value


class LinearClock:

    def __init__(self):
        self._count = count()
        self._pclock = PropClockTracker(PROP_FREQ)

    def feed(self, timestamp):
        self._pclock.feed(timestamp)
        return next(self._count)

    @property
    def min_diff(self):
        return self._pclock.min_diff

    @property
    def max_diff(self):
        return self._pclock.max_diff


def main():
    clock = LinearClock() #PropClockTracker()
    data = defaultdict(list)
    for line in pathlib.Path(sys.argv[1]).open("r"):
        line = line.strip()
        if not line:
            continue
        line = line.split(":")
        if line[0] != "D":
            continue
        # timestamp, mux, value = (int(p, 16) for p in line.split(":"))
        # D:5A9C9D9C:08:2FE7BC
        timestamp, mux, value = (int(p, 16) for p in [line[1], line[2], line[3]])
        seconds = clock.feed(timestamp)
        data[mux].append((seconds, value))
        stats(value)

    print("biggest_diff", biggest_diff)
    fig = go.Figure()
    print(clock.min_diff, clock.max_diff)
    for mux, values in data.items():
        values = np.array(values)
        fig.add_trace(go.Scatter(x=values[:, 0], y=values[:, 1], name=f"Mux {hex(mux)}"))

    fig.show()


if __name__ == '__main__':
    main()
