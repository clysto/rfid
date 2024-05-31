import numpy as np
import matplotlib.pyplot as plt
from rfid import PulseIntervalEncoder, RFIDReaderCommand, epc_str_to_bits
from epc_crc import crc16

pie = PulseIntervalEncoder(samp_rate=2e6, pw_d=10)
reader = RFIDReaderCommand(pie)
sig_gen = reader.select(
    pointer=32,
    length=96,
    mask=epc_str_to_bits("E280 6890 0000 500E 87E2 99D2"),
    mem_bank="EPC",
)
sig_gen = sig_gen[183:]

sig_recv = np.fromfile("data/2024-05-31/select_cmd.cf32", dtype=np.complex64)
sig_recv = np.abs(sig_recv) > 0.4
sig_recv = sig_recv[739:]

n_tari = 40

prev_low_index = 0
status = 1
data = []
for i in range(len(sig_recv)):
    if status == 1 and sig_recv[i] == 0:
        status = 0

        if i - prev_low_index > 1.5 * n_tari:
            data.append(1)
        else:
            data.append(0)
        prev_low_index = i

    if status == 0 and sig_recv[i] == 1:
        status = 1

print(data)

plt.figure()
plt.plot(sig_recv)
plt.plot(sig_gen)
plt.show()

"""
Command:
1010

Target:
100

Action:
000

MemBank:
01

Pointer:
00100000

Length:
01100000

Mask:
111000101000000001101000100100000000000000000000010100000000111010000111111000101001100111010010

Truncate:
0

CRC:
1011101000110111
"""

epc = list(
    map(
        int,
        "111000101000000001101000100100000000000000000000010100000000111010000111111000101001100111010010",
    )
)
epc = np.packbits(epc)
print("EPC:", "".join(map(lambda x: format(x, "02x"), epc)).upper())


select_data = list(
    map(
        int,
        "10101000000100100000011000001110001010000000011010001001000000000000000000000101000000001110100001111110001010011001110100100",
    )
)

print("".join(map(str, crc16(select_data))))
print(epc_str_to_bits("E280 6890 0000 500E 87E2 99D2"))
assert (
    "".join(map(str, epc_str_to_bits("E280 6890 0000 500E 87E2 99D2")))
    == "111000101000000001101000100100000000000000000000010100000000111010000111111000101001100111010010"
)
