# Copyright: 2021, Diez B. Roggisch . All rights reserved.
import serial
import pytest
import operator
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
    conn.write(rqads("R$F0"))
    print(conn.readline())
