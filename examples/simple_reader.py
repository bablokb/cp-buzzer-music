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

# note: line breaks are not necessary!
HAPPY_BIRTHDAY = """
0 G5 1.8040000200271606 43;
2.8166663646698 G5 0.8213333487510681 43;
4.190666437149048 A5 3.050666570663452 43;
8.381333589553833 G5 2.5813333988189697 43;
12.71399998664856 C6 2.933333396911621 43;
51.09533333778381 G5 0.8799999952316284 43;
52.43266701698303 G6 2.640000104904175 43;
56.61866784095764 E6 2.757333278656006 43;
60.5353319644928 C6 2.9260001182556152 43;
64.57933449745178 B5 4.245999813079834 43;
68.41066384315491 A5 5.140666484832764 43;
75.73599648475647 F6 1.7233333587646484 43;
78.40333199501038 F6 0.762666642665863 43;
79.99999642372131 E6 3.5786666870117188 43;
84.15400338172913 C6 4.0993332862854 43;
88.07333016395569 D6 4.443999767303467 43;
92.75066781044006 C6 14.967333793640137 43;
16.87533402442932 B5 6.2186665534973145 43;
24.934000253677368 G5 2.111999988555908 43;
27.845999002456665 G5 0.6453333497047424 43;
29.249332666397095 A5 2.640000104904175 43;
33.11733269691467 G5 2.1046667098999023 43;
36.8460009098053 D6 3.2266666889190674 43;
40.860668420791626 C6 5.1626667976379395 43;
48.50600075721741 G5 1.5766667127609253 43;
"""

reader = MusicReader()
print("reading notes from string:")
i = 1
for note in reader.load(HAPPY_BIRTHDAY):
  print(f"  {i:4d}: {note}")
  i += 1
time.sleep(3)

print("reading notes from file:")
i = 1
for note in reader.read("music.txt"):
  print(f"  {i:4d}: {note}")
  i += 1
