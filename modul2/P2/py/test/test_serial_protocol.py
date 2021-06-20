# Copyright: 2021, Diez B. Roggisch . All rights reserved.
import serial
import pytest
import operator
import time
import threading
import queue

from functools import reduce, wraps

PORT = "/dev/serial/by-id/usb-FTDI_USB__-__Serial-if00-port0"
BAUD = 115200


class ProtocoViolation(Exception):
    pass


def rqads_assert(result, message=None):
    if not result:
        raise ProtocoViolation(message)


def rqads_encode(message):
    if isinstance(message, str):
        message = message.encode("ascii")
    total = b"RQADS" + message
    chksum = reduce(operator.xor, total, 0)
    suffix = f"*{chksum:02x}\r\n".encode("ascii")
    datagram = b"$" + total + suffix
    return datagram


def rqads_decode(line):
    rqads_assert(line.startswith(b"$RQADS"), "Prefix not $RQADS")
    rqads_assert(line.endswith(b"\r\n"), "No CRLF")
    prefix, suffix = line.split(b"*")
    rqads_assert(len(suffix) == 4, "Suffix malformed")  # XX\r\n
    checksum = int(suffix[:2], 16)
    value = reduce(operator.xor, (c for c in prefix[1:]))
    rqads_assert(
        value == checksum,
        f"Checksum Error: {value:02X} != {checksum:02X}"
    )
    return prefix[6:]  # cut off $RQADS


def command(func):
    @wraps(func)
    def _d(self, *a, **k):
        func(self, *a, **k)
        line = self.readline()
        return rqads_decode(line)

    return _d


class SerialConnector:

    SAMPLE_SPEEDS = {
        2.5: 0b00000011,
        5: 0b00010011,
        10: 0b00100011,
        15: 0b00110011,
        25: 0b01000011,
        30: 0b01010011,
        50: 0b01100011,
        60: 0b01110010,
        100: 0b10000010,
        500: 0b10010010,
        1000: 0b10100001,
        2000: 0b10110000,
        3750: 0b11000000,
        7500: 0b11010000,
        15000: 0b11100000,
        30000: 0b11110000,
    }

    def __init__(self, port, baud, read_callback=lambda x: None):
        self._conn = serial.Serial(port, baud)
        self._lines = queue.Queue()
        self._read_callback = read_callback
        self._t = threading.Thread(target=self._line_reader)
        self._t.daemon = True
        self._t.start()

    @command
    def ping(self):
        self._send("P")

    @command
    def thinning(self, thinning):
        assert thinning in range(0, 256)
        self._send(f"T:{thinning:02X}")

    @command
    def rate(self, samples_per_second):
        value = self.SAMPLE_SPEEDS[samples_per_second]
        self._send(f"R:{value:02X}")

    def listfiles(self):
        res = []
        self._send("L")
        while True:
            answer = rqads_decode(self.readline())
            if answer == b"XXX":
                break
            res.append(answer)
        return res

    def readline(self):
        return self._lines.get()

    def _send(self, message):
        self._conn.write(rqads_encode(message))

    def _line_reader(self):
        while True:
            line = self._conn.readline()
            self._read_callback(line)
            self._lines.put(line)


@pytest.fixture
def conn():
    conn = SerialConnector(PORT, BAUD, print)
    return conn


def test_decoding():
    ping_result = b'$RQADSP*05\r\n'
    assert rqads_decode(ping_result) == b"P"


def test_ping(conn):
    assert conn.ping() == b"P"


def test_thinning(conn):
    assert conn.thinning(64) == b"T"


def test_rate(conn):
    assert conn.rate(7500) == b"R"


def test_file_listing(conn):
    assert conn.listfiles() == [b"001", b"002"]


def test_cdac(conn):
    duration = 120
    repititions = 3

    #conn.write(rqads("R:03"))   # 0b00000011, 2.5 SPS
    #conn.write(rqads("R:A1"))   # 0b10100001, 1K SPS
    #conn.write(rqads("R:C0"))   # 0b11000000, 3.750 SPS
    #conn.write(rqads("R:D0"))   # 0b11010000, 7500 SPS
    #conn.write(rqads("R:E0"))   # 0b11100000, 15K SPS
    #conn.write(rqads("R:F0"))   # 0b11110000, 30K SPS
    conn.write(rqads("T:FF"))  # thinning highest
    #conn.write(rqads("T:01"))  # thinning lowest
    for _ in range(repititions):
        then = time.monotonic()
        conn.write(rqads("C1:08"))  # channel 0, single-sided
        while time.monotonic() - then < duration:
            print(conn.readline())
        # for termination and to collect the stats
        conn.write(rqads("S"))
        print(conn.readline())
