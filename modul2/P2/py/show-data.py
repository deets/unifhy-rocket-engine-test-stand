#!python3
# Copyright: 2021, Diez B. Roggisch, Berlin . All rights reserved.
import sys
import pathlib
from collections import defaultdict

import plotly.graph_objects as go
import numpy as np


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


def main():
    clock = PropClockTracker(300_000_000)
    data = defaultdict(list)
    for line in pathlib.Path(sys.argv[1]).open("r"):
        line = line.strip()
        if not line:
            continue
        line = line.split(":")
        if line[0] != "D":
            continue
        #timestamp, mux, value = (int(p, 16) for p in line.split(":"))
        #D:5A9C9D9C:08:2FE7BC
        timestamp, mux, value = (int(p, 16) for p in [line[1], line[2], line[3]])
        seconds = clock.feed(timestamp)
        data[mux].append((seconds, value))

    fig = go.Figure()
    print(clock.min_diff, clock.max_diff)
    for mux, values in data.items():
        values = np.array(values)
        fig.add_trace(go.Scatter(x=values[:, 0], y=values[:, 1], name=f"Mux {hex(mux)}"))

    fig.show()


if __name__ == '__main__':
    main()
