import re
from epc_crc import crc16

# A preamble shall comprise a fixed-length start delimiter 12.5us +/-5%
DELIM_DURATION = 12


def crc5(bits: list):
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


def ebv_encode(bits: list[int]) -> list[int]:
    n_pad = (len(bits) + 6) // 7 * 7 - len(bits)
    bits = [0] * n_pad + bits
    n_block = len(bits) // 7
    encoded = []
    for n in range(n_block):
        extension_bit = 1 if n < n_block - 1 else 0
        block = [extension_bit] + bits[n * 7 : (n + 1) * 7]
        encoded.extend(block)
    return encoded


class PulseIntervalEncoder:

    def __init__(self, samp_rate, pw_d=12):
        """
        Initializes an instance of the PulseIntervalEncoder class.

        Args:
            samp_rate (int): The sample rate in Hz.
            pw_d (int, optional): The pulse width duration in us. Defaults to 12us.
        """
        self.samp_rate = samp_rate
        self.pw_d = pw_d
        self.n_data0 = int(2 * pw_d * 1e-6 * samp_rate)
        self.n_data1 = int(4 * pw_d * 1e-6 * samp_rate)
        self.n_pw = int(pw_d * 1e-6 * samp_rate)
        self.n_delim = int(DELIM_DURATION * 1e-6 * samp_rate)
        # RTcal = 0_length + 1_length
        self.n_rtcal = int(6 * pw_d * 1e-6 * samp_rate)
        self.data0 = [1] * self.n_data0
        self.data0[-self.n_pw :] = [0] * self.n_pw
        self.data1 = [1] * self.n_data1
        self.data1[-self.n_pw :] = [0] * self.n_pw

    def preamble(self, blf=40e3, dr=8):
        # BLF = DR / TRcal => TRcal = DR / BLF
        n_trcal = int(dr / blf * self.samp_rate)
        delim = [0] * self.n_delim
        rt_cal = [1] * self.n_rtcal
        rt_cal[-self.n_pw :] = [0] * self.n_pw
        tr_cal = [1] * n_trcal
        tr_cal[-self.n_pw :] = [0] * self.n_pw
        return delim + self.data0 + rt_cal + tr_cal

    def frame_sync(self):
        delim = [0] * self.n_delim
        rt_cal = [1] * self.n_rtcal
        rt_cal[-self.n_pw :] = [0] * self.n_pw
        return delim + self.data0 + rt_cal

    def encode(self, data: list):
        sig = []
        for bit in data:
            if bit == 0:
                sig += self.data0
            else:
                sig += self.data1
        return sig


class RFIDReaderCommand:

    def __init__(self, pie: PulseIntervalEncoder):
        self.pie = pie

    def select(
        self,
        pointer: int,
        length: int,
        mask: list[int],
        trunc: bool = False,
        target: str = "sl",
        action: int = 0,
        mem_bank: str = "FileType",
    ):
        bits = [1, 0, 1, 0]
        if target not in ["inv-s0", "inv-s1", "inv-s2", "inv-s3", "sl"]:
            raise ValueError(
                "Invalid target value. Must be either 'inv-s0', 'inv-s1', 'inv-s2', 'inv-s3', or 'sl'."
            )
        if target == "inv-s0":
            bits += [0, 0, 0]
        elif target == "inv-s1":
            bits += [0, 0, 1]
        elif target == "inv-s2":
            bits += [0, 1, 0]
        elif target == "inv-s3":
            bits += [0, 1, 1]
        else:
            bits += [1, 0, 0]

        if action < 0 or action > 7:
            raise ValueError("Invalid action value. Must be between 0 and 7.")

        bits += list(map(int, format(action, "03b")))

        if mem_bank not in ["FileType", "EPC", "TID", "File_0"]:
            raise ValueError(
                "Invalid mem_bank value. Must be either 'FileType', 'EPC', 'TID', or 'File_0'."
            )
        if mem_bank == "FileType":
            bits += [0, 0]
        elif mem_bank == "EPC":
            bits += [0, 1]
        elif mem_bank == "TID":
            bits += [1, 0]
        else:
            bits += [1, 1]

        bits += ebv_encode(list(map(int, bin(pointer)[2:])))
        if length < 0 or length > 255:
            raise ValueError("Invalid length value. Must be between 0 and 255.")
        bits += list(map(int, format(length, "08b")))
        if len(mask) != length:
            raise ValueError("Mask length must match the specified length.")
        bits += mask

        if trunc:
            bits += [1]
        else:
            bits += [0]

        bits += crc16(bits)

        return self.pie.frame_sync() + self.pie.encode(bits)

    def query(
        self,
        dr: str = "8",
        m: int = 1,
        trext: bool = False,
        sel: str = "all",
        session: str = "s0",
        target: str = "A",
        q: int = 0,
    ):
        """
        Query initiates and specifies an inventory round.

        Args:
            dr (str): The TRcal divide ratio. It can be either "8" or "64/3".
            m (int): The number of cycles per symbol.
            trext (bool): Determines whether a Tag prepends the T=>R preamble with a pilot tone.
            sel (str): The selection mode for Tags. It can be "all", "~sl", or "sl".
            session (str): The session for the inventory round. It can be "s0", "s1", "s2", or "s3".
            target (str): The flag selection for Tags. It can be "A" or "B".
            q (int): The number of slots in the round.

        Returns:
            sig: The encoded query command waveform.
        """

        bits = [1, 0, 0, 0]
        if dr not in ["8", "64/3"]:
            raise ValueError("Invalid dr value. Must be either '8' or '64/3'.")
        if dr == "8":
            bits += [0]
        else:
            bits += [1]
        if m not in [1, 2, 4, 8]:
            raise ValueError("Invalid m value. Must be either 1, 2, 4, or 8.")
        if m == 1:
            bits += [0, 0]
        elif m == 2:
            bits += [0, 1]
        elif m == 4:
            bits += [1, 0]
        else:
            bits += [1, 1]

        if trext:
            bits += [1]
        else:
            bits += [0]

        if sel not in ["all", "sl", "~sl"]:
            raise ValueError("Invalid sel value. Must be either 'all', '~sl', or 'sl'.")
        if sel == "all":
            bits += [0, 0]
        elif sel == "~sl":
            bits += [1, 0]
        else:
            bits += [1, 1]

        if session not in ["s0", "s1", "s2", "s3"]:
            raise ValueError(
                "Invalid session value. Must be either 's0', 's1', 's2', or 's3'."
            )
        if session == "s0":
            bits += [0, 0]
        elif session == "s1":
            bits += [0, 1]
        elif session == "s2":
            bits += [1, 0]
        else:
            bits += [1, 1]

        if target not in ["A", "B"]:
            raise ValueError("Invalid target value. Must be either 'A' or 'B'.")
        if target == "A":
            bits += [0]
        else:
            bits += [1]

        if q < 0 or q > 15:
            raise ValueError("Invalid q value. Must be between 0 and 15.")
        bits += list(map(int, format(q, "04b")))

        bits += crc5(bits)

        dr = 8 if dr == "8" else 64 / 3
        return self.pie.preamble(dr=dr) + self.pie.encode(bits)

    def query_rep(self, session: str = "s0"):
        """
        QueryRep instructs Tags to decrement their slot counters.

        Args:
            session (str): The session value to use for the query. Must be one of the following: 's0', 's1', 's2', or 's3'. Defaults to 's0'.

        Returns:
            sig: The encoded query command waveform.
        """
        bits = [0, 0]
        if session not in ["s0", "s1", "s2", "s3"]:
            raise ValueError(
                "Invalid session value. Must be either 's0', 's1', 's2', or 's3'."
            )

        if session == "s0":
            bits += [0, 0]
        elif session == "s1":
            bits += [0, 1]
        elif session == "s2":
            bits += [1, 0]
        else:
            bits += [1, 1]

        return self.pie.frame_sync() + self.pie.encode(bits)


def epc_str_to_bits(epc: str) -> list[int]:
    """
    Converts a hexadecimal EPC string to a list of bits.
    `epc_str_to_bits` will ignore any whitespace in the EPC string.

    Args:
        epc (str): The hexadecimal EPC string.

    Returns:
        list[int]: A list of bits representing the EPC.
    """
    epc = epc.strip()
    epc = re.sub(r"\s+", "", epc)
    return list(map(int, "".join(format(int(c, 16), "04b") for c in epc)))
