import numpy as np
from rfid import PulseIntervalEncoder, RFIDReaderCommand, epc_str_to_bits

if __name__ == "__main__":
    pie = PulseIntervalEncoder(samp_rate=2e6)
    reader = RFIDReaderCommand(pie)
    # sig = reader.query(q=1) + [1] * 2500 + reader.query_rep() + [1] * 2500
    # sig = reader.query(q=0) + [1] * 2500
    sig = (
        reader.select(
            pointer=32,
            length=96,
            mask=epc_str_to_bits("E280 6890 0000 500E 87E2 99D2"),
            mem_bank="EPC",
        )
        + [1] * 200
        + reader.query(q=0, sel="sl")
        + [1] * 2500
    )
    np.array(sig).astype(np.float32).tofile("reader.f32")
