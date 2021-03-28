# Copyright: 2021, Diez B. Roggisch . All rights reserved.
import serial
import pytest
import operator
from functools import reduce

PORT = "/dev/serial/by-id/usb-Parallax_Inc_Propeller_P2-EVAL_PLX4L28HW-if00-port0"
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
    print(conn.readline())
