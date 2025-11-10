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

FILENAME="pnp_S${TARGET_SIZE}_D${VEG_DENSITY}${SBUFFER}${SBACKGROUND}.bin"

pixi run -e dev \
    memray run -o "/media/TOBEDELETED/s2gos/profiling/20251106/generation/${FILENAME}" \
    simple_generation.py --size=$TARGET_SIZE --density=$VEG_DENSITY --buffer=$BUFFER --background=$BACKGROUND

pixi run -e dev \
    memray flamegraph --temporal "/media/TOBEDELETED/s2gos/profiling/20251106/generation/${FILENAME}" 
