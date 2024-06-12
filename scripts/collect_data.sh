#!/bin/bash

set -e

export GUM_INPUT_CURSOR_FOREGROUND=4
export GUM_CHOOSE_CURSOR_FOREGROUND=4
export GUM_CHOOSE_HEADER_FOREGROUND=4
export GUM_CHOOSE_SELECTED_FOREGROUND=4
export GUM_CONFIRM_PROMPT_FOREGROUND=4
export GUM_CONFIRM_SELECTED_BACKGROUND=4
export GUM_SPIN_SPINNER_FOREGROUND=4
export GUM_WRITE_CURSOR_FOREGROUND=4

gum style --bold --foreground=4 "Where to save the data?"
path=$(gum input --placeholder="" --value="data/$(date +%Y%m%d%H%M%S)")
echo $path
gum style --bold --foreground=4 "Select the RFID tag channel to collect:"
channels=$(gum choose --height=5 --no-limit "Tag 1 & 2" "Tag 1 & 3" "Tag 2 & 3")
printf "$channels\n"
gum style --bold --foreground=4 "Note about the data:"
note=$(gum write --placeholder="")
printf "$note\n"
gum confirm "Start collecting data?"

filters=()
names=()

while IFS= read -r channel; do
    filter=$(echo $channel | cut -c 5- | tr -d ' ' | tr '&' ',')
    name=$(echo $channel | cut -c 5- | tr -d ' ' | tr '&' '-')
    filters+=($filter)
    names+=($name)
done <<<"$channels"

mkdir -p $path

echo "$note" >"$path/note.txt"

for i in "${!filters[@]}"; do
    gum spin --title="Collecting $path/${names[$i]}.cf32" -- rfid_query.py --duration 0.6 --rx-gain 0 --tx-gain 30 --freq 900e6 -f "${filters[$i]}" \
        --out "$path/${names[$i]}.cf32"
done

for i in "${!filters[@]}"; do
    gum spin --title="Processing $path/${names[$i]}.cf32" -- ./build/split_rn16 "$path/${names[$i]}.cf32" "$path/${names[$i]}.npz"
done

gum style --bold --foreground=2 "Data successfully saved to $path"
