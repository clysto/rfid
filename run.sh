#!/bin/bash

gains=(74 77 80)
repeat=4

for gain in ${gains[@]}; do
    for i in $(seq 0 $((repeat - 1))); do
        echo "gain: $gain, repeat: $i"
        ./rfid_query.py --tx-gain $gain --out data/${gain}_8cm_$i.cf32
    done
done
