import numpy as np
from rfid import PulseIntervalEncoder, RFIDReaderCommand, epc_str_to_bits

TAGS = {
    1: "E200470C09806026E477010D",
    2: "E200470E4FB0602608DA0107",
    3: "E200470C12006026E4FF010F",
    4: "E200470E47A060260859010E",
}

if __name__ == "__main__":
    pie = PulseIntervalEncoder(samp_rate=2e6)
    reader = RFIDReaderCommand(pie)
    sig = (
        [1] * 25000
        + reader.select(
            pointer=32,
            length=96,
            mask=epc_str_to_bits(TAGS[3]),
            mem_bank="EPC",
            action=1,
        )
        + [1] * 500
        + reader.select(
            pointer=32,
            length=96,
            mask=epc_str_to_bits(TAGS[4]),
            mem_bank="EPC",
            action=1,
        )
        + [1] * 500
        + reader.query(q=0, sel="sl")
        + [1] * 2500
        + (reader.query_adjust() + [1] * 2500) * 100
    )
    np.array(sig).astype(np.float32).tofile("data/reader.f32")
