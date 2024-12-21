# ----------------------------------------------------------------------------
# Simple test of the AsyncBuzzer.
#
# Both versions of main() give the same result, since the AsyncBuzzer uses
# locking internally, so additional tasks will wait until the buzzer is idle
# again.
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

# notes (pitch,duration,volume),...
NOTES = [('C4',1,3),('E4',1,7),('G4',1,8),('C5',1.5,10)]

async def main1():
  buzzer = AsyncBuzzer(board.GP18)
  for note in NOTES:
    t = asyncio.create_task(buzzer.play(*note))
    asyncio.run_until_complete(t)
  buzzer.deinit()

async def main2():
  buzzer = AsyncBuzzer(board.GP18)
  n_tasks = []
  for note in NOTES:
    t = asyncio.create_task(buzzer.play(*note))
    n_tasks.append(t)
  await asyncio.gather(*n_tasks)
  buzzer.deinit()

asyncio.run(main1())
asyncio.run(main2())
