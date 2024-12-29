# ----------------------------------------------------------------------------
# Play a chord on multiple buzzers.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-buzzer-music
#
# ----------------------------------------------------------------------------

import board
import asyncio
from buzzer_music.async_buzzer import AsyncBuzzer

# notes: (pitch,duration),...
NOTES = [('C4',1),('E4',1),('G4',1),('C5',1)]
PINS  = [board.GP18,board.GP17,board.GP15,board.GP13]

# Create and start all tasks at once.
async def main():
  buzzers = [AsyncBuzzer(pin) for pin in PINS]
  coros = [buzzer.tone(*note) for buzzer,note in zip(buzzers,NOTES)]
  await asyncio.gather(*coros)
  for buzzer in buzzers:
    buzzer.deinit()

asyncio.run(main())
