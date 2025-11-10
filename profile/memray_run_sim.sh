#!/bin/bash

TARGET_SIZE=$1
VEG_DENSITY=$2
BUFFER=$3
BACKGROUND=$4

SBUFFER=""
SBACKGROUND=""
if [ -n "$BUFFER" ] && [ $BUFFER -eq 0 ] ; then
    SBUFFER="_noBU"
fi

if [ -n "$BACKGROUND" ] && [ $BACKGROUND -eq 0 ] ; then
    SBACKGROUND="_noBa"
fi

FILENAME="pnp_S${TARGET_SIZE}_D${VEG_DENSITY}${SBUFFER}${SBACKGROUND}_opt.bin"

pixi run -e dev \
    memray run --force -o "./profile/simulation/${FILENAME}" \
    simple_simulation.py --size=$TARGET_SIZE --density=$VEG_DENSITY --buffer=$BUFFER --background=$BACKGROUND

pixi run -e dev \
    memray flamegraph --force --temporal "./profile/simulation/${FILENAME}" 
