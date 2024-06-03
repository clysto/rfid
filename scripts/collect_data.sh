#!/bin/bash

read -p "Enter the index of experiments: " index


rfid_query.py --duration 0.6 --rx-gain 0 --tx-gain 30 --freq 900e6 -f 1,2 --out data/1-2.cf32
rfid_query.py --duration 0.6 --rx-gain 0 --tx-gain 30 --freq 900e6 -f 3,2 --out data/3-2.cf32
./build/split_rn16 data/1-2.cf32 "data/1-2#$index.npz"
./build/split_rn16 data/3-2.cf32 "data/3-2#$index.npz"
