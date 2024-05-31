from epc_crc import crc5, crc16
from rfid import crc5 as crc5_py

print(crc5([1, 1, 1, 1, 1, 0]))
print(crc5_py([1, 1, 1, 1, 1, 0]))

print(crc16([0] * 16))
print(
    crc16(
        [
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
        ]
    )
)
