# ----------------------------------------------------------------------------
# Simple test of the MusicReader.
#
# This test does not play music, it just checks if the notes are correctly
# read and parsed.

# TODO: The data itself is not correct (time is always zero,
#       i.e. all the notes start at the same time-point).
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-buzzer-music
#
# ----------------------------------------------------------------------------

import time
import board
import asyncio
from buzzer_music.reader import MusicReader

HAPPY_BIRTHDAY = """
0 E5 2 0;0 E5 2 0;0 E5 4 0;0 E5 2 0;0 E5 2 0;0 E5 4 0;
0 E5 2 0;0 G5 2 0;0 C5 4 0;0 D5 1 0;0 E5 6 0;
0 F5 2 0;0 F5 2 0;0 F5 3 0;0 F5 1 0;0 F5 2 0;0 E5 2 0;
0 E5 2 0;0 E5 1 0;0 E5 1 0;0 E5 2 0;0 D5 2 0;0 D5 2 0;
0 E5 2 0;0 D5 4 0;0 G5 2 0;
0 E5 2 0;0 E5 2 0;0 E5 4 0;0 E5 2 0;0 E5 2 0;0 E5 4 0;
0 E5 2 0;0 G5 2 0;0 C5 4 0;0 D5 1 0;0 E5 6 0;
0 F5 2 0;0 F5 2 0;0 F5 3 0;0 F5 1 0;0 F5 2 0;0 E5 2 0;
0 E5 2 0;0 E5 1 0;0 E5 1 0;0 G5 2 0;0 G5 2 0;0 F5 2 0;
0 D5 2 0;0 C5 6 0
"""

reader = MusicReader()
#print("reading notes from string:")
#for note in reader.load(HAPPY_BIRTHDAY):
#  print(f"  {note}")
#time.sleep(3)

print("reading notes from file:")
i = 0
for note in reader.read("music.txt"):
  print(f"  {i:4d}: {note}")
  i += 1
