import numpy as np
from rfid import PulseIntervalEncoder, RFIDReaderCommand

if __name__ == "__main__":
    pie = PulseIntervalEncoder(samp_rate=2e6)
    reader = RFIDReaderCommand(pie)
    sig = reader.query(q=1) + [1] * 2500 + reader.query_rep() + [1] * 2500
    np.array(sig).astype(np.float32).tofile("reader.f32")
