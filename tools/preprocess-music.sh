#!/bin/bash
# ----------------------------------------------------------------------------
# Preprocess notes copied from onlinesequencer.net.
#
# To copy the notes, enter edit-mode (pencil) on onlinesequencer.net, then
# select all notes (dotted-square) and copy them with CTRL-C (make sure your
# cursor is somewhere within the score).
#
# Then open a textfile with extension ".raw" and insert with CTRL-V. Close the
# file and then run this script passing the raw-file as an argument. The
# script will generate an output file with the same name and the extension ".txt".
#
# The script will split the notes at every semicolon and put a single note
# on every line. It will also remove the header and the trailer of the notes.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-buzzer-music
#
# ----------------------------------------------------------------------------

if [ -z "$1" ]; then
  echo "usage: $0 infile.raw [outfile]" >&2
  exit 3
fi

infile="$1"
outfile="$2"
if [ -z "$outfile" ]; then
  outfile="${infile%.*}.txt"
fi

# the sed commands do
#   - split notes at ';'
#   - remove header (e.g. "Online Sequencer:250354:")
#   - remove trailing ":"
# finally, the result is sorted by start-time

echo "creating $outfile..."
export LANG=en
sed -e 's/;/\n/g' -e 's/^[^:]*:[^:]*://' -e 's/://' "$infile" | \
  sort -n > "$outfile"
