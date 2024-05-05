import numpy as np
from crc5 import crc5

# A preamble shall comprise a fixed-length start delimiter 12.5us +/-5%
DELIM_DURATION = 12


class PulseIntervalEncoder:

    def __init__(self, samp_rate, pw_d=12):
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
        Queries the RFID device with the specified parameters.

        Args:
            dr (str): The TRcal divide ratio. It can be either "8" or "64/3".
            m (int): The number of cycles per symbol.
            trext (bool): Determines whether a Tag prepends the T=>R preamble with a pilot tone.
            sel (str): The selection mode for Tags. It can be "all", "~sl", or "sl".
            session (str): The session for the inventory round. It can be "s0", "s1", "s2", or "s3".
            target (str): The flag selection for Tags. It can be "A" or "B".
            q (int): The number of slots in the round.

        Returns:
            bytes: The encoded query result.
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


pie = PulseIntervalEncoder(samp_rate=2e6)
reader = RFIDReaderCommand(pie)
sig = reader.query()
np.array(sig).astype(np.float32).tofile("reader.f32")
