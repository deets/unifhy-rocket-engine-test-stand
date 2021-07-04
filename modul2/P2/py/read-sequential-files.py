# Copyright: 2021, Diez B. Roggisch . All rights reserved.
import sys
import serial
from itertools import count

PORT = "/dev/serial/by-id/usb-FTDI_USB__-__Serial-if00-port0"
BAUD = 1_000_000


def main():
    conn = serial.Serial(PORT, BAUD)
    for number in count(1):
        filename = f"/tmp/RQADS{number:03x}.DAT"
        with open(filename, "wb") as outf:
            while True:
                line = conn.readline()
                if line.strip() == b"done":
                    break
                outf.write(line)
                print(".", end="")
                sys.stdout.flush()
            print(f"\nstreamed to {filename}")


if __name__ == '__main__':
    main()
