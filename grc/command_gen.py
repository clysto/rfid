import numpy as np
import argparse
from rfid import PulseIntervalEncoder, RFIDReaderCommand, epc_str_to_bits

TAGS = {
    1: "E200470C09806026E477010D",
    2: "E200470E4FB0602608DA0107",
    3: "E200470C12006026E4FF010F",
    4: "E200470E47A060260859010E",
}


def reader_cmd_gen(samp_rate=2e6, filter="all") -> np.ndarray:
    pie = PulseIntervalEncoder(samp_rate)
    reader = RFIDReaderCommand(pie)
    # add 100ms of silence
    sig = [1] * int(0.1 * samp_rate)
    if filter == "all":
        sig += reader.query(q=0) + [1] * 2500
        sig += (reader.query_adjust() + [1] * 2500) * 99
    else:
        filter = filter.split(",")
        filter = [int(tag_id) for tag_id in filter]
        for tag_id in filter:
            sig += (
                reader.select(
                    pointer=32,
                    length=96,
                    mask=epc_str_to_bits(TAGS[tag_id]),
                    mem_bank="EPC",
                    action=1,
                )
                + [1] * 300
            )
        sig += reader.query(q=0, sel="sl") + [1] * 2500
        sig += (reader.query_adjust() + [1] * 2500) * 99
    return (np.array(sig) + 0j).astype(np.complex64)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samp-rate", type=float, default=2e6)
    parser.add_argument("--filter", type=str, default="all")
    parser.add_argument("out", type=str, default="reader.cf32", nargs="?")
    args = parser.parse_args()
    sig = reader_cmd_gen(args.samp_rate, args.filter)
    sig.tofile(args.out)
