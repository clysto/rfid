from epc_crc import crc5, crc16


def crc5_py(bits: list):
    crc = [1, 0, 0, 1, 0]

    for i in range(len(bits)):
        tmp = [0, 0, 0, 0, 0]
        tmp[4] = crc[3]

        if crc[4] == 1:
            if bits[i] == 1:
                tmp[0] = 0
                tmp[1] = crc[0]
                tmp[2] = crc[1]
                tmp[3] = crc[2]
            else:
                tmp[0] = 1
                tmp[1] = crc[0]
                tmp[2] = crc[1]
                tmp[3] = 0 if crc[2] == 1 else 1
        else:
            if bits[i] == 1:
                tmp[0] = 1
                tmp[1] = crc[0]
                tmp[2] = crc[1]
                tmp[3] = 0 if crc[2] == 1 else 1
            else:
                tmp[0] = 0
                tmp[1] = crc[0]
                tmp[2] = crc[1]
                tmp[3] = crc[2]

        crc[:] = tmp

    return crc[::-1]


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
