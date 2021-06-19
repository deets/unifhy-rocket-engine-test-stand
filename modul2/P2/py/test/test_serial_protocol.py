# Copyright: 2021, Diez B. Roggisch . All rights reserved.
import serial
import pytest
import operator
import time
from functools import reduce

PORT = "/dev/serial/by-id/usb-FTDI_USB__-__Serial-if00-port0"
BAUD = 115200


def rqads(message):
    if isinstance(message, str):
        message = message.encode("ascii")
    total = b"RQADS" + message
    chksum = reduce(operator.xor, total, 0)
    suffix = f"*{chksum:02x}\r\n".encode("ascii")
    datagram = b"$" + total + suffix
    print(datagram)
    return datagram


@pytest.fixture
def conn():
    conn = serial.Serial(PORT, BAUD)
    return conn


def test_ping(conn):
    conn.write(rqads("P"))
    print("ping answer", conn.readline())


def test_rate(conn):
    conn.write(rqads("R:F0"))
    print(conn.readline())


def test_thinning(conn):
    conn.write(rqads("T:0a"))
    print(conn.readline())


def test_cdac(conn):
    duration = 5
    repititions = 1

    #conn.write(rqads("R:03"))   # 0b00000011, 2.5 SPS
    #conn.write(rqads("R:A1"))   # 0b10100001, 1K SPS
    #conn.write(rqads("R:C0"))   # 0b11000000, 3.750 SPS
    conn.write(rqads("R:D0"))   # 0b11010000, 7500 SPS
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
