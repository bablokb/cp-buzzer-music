# ----------------------------------------------------------------------------
# Play music on (multiple) buzzers. Inspired by
# https://github.com/james1236/buzzer_music
#
# There are a number of major changes compared to the original:
#   - implemented in CircuitPython
#   - songs can be passed as string or as filename
#   - processing using asyncio
#   - low memory requirements (uses streaming)
#   - (currently) no simulated polyphony (i.e. no fast arpeggios)
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-buzzer-music
#
# ----------------------------------------------------------------------------

""" Implementation of class MusicPlayer """

import time
import gc
import collections
import asyncio
from buzzer_music.async_buzzer import AsyncBuzzer
from buzzer_music.reader       import MusicReader

GC_INTERVAL = 60

class MusicPlayer:
  """ play notes on (multiple) buzzers """

  def __init__(self, pins=[], volume=10, qlength=10, debug=False):
    """ constructor """

    self._buzzers = [AsyncBuzzer(pin) for pin in pins]
    self._volume  = volume
    self._reader  = MusicReader()
    self._qlimit  = qlength*len(pins)
    self._queue   = []
    self._tasks   = []
    self._debug   = debug
    self._stop    = False
    self._pause   = False

    if debug:
      self._msg = self._print
    else:
      self._msg = lambda msg: None

    self._start   = time.monotonic()  # will be updated by play

  # --- print debug-messages   -----------------------------------------------

  def _print(self,msg):
    """ print debug-messages """
    print(f"[{time.monotonic()-self._start:5.3f}] {msg}")

  # --- return first available buzzer   --------------------------------------

  async def _free_buzzer(self):
    """ return first free buzzer """
    while True:
      for index,buzzer in enumerate(self._buzzers):
        if not buzzer.busy:
          buzzer.busy = True
          return index,buzzer
      await asyncio.sleep(0)

  # --- gc task   ------------------------------------------------------------

  async def _gc(self):
    """ run gc periodically """
    try:
      self._msg(f"g: starting GC-task")
      while True:
        await asyncio.sleep(GC_INTERVAL)
        self._msg(f"g: free memory: {gc.mem_free()}")
        gc.collect()
        self._msg(f"g: free memory: {gc.mem_free()}")
    except:
      pass
    self._msg(f"g: GC-task finished")

  # --- reader task   --------------------------------------------------------

  async def _read(self,filename,song,bpm,ref):
    """ reader task providing notes to the queue """

    self._msg("r: starting reader task...")
    for note in self._reader.load(filename,song,bpm,ref):
      while len(self._queue) >= self._qlimit:
        await asyncio.sleep(0)
      self._msg(f"r: appending note: {note}")
      #self._queue.appendleft(note)
      self._queue.insert(0,note)
      await asyncio.sleep(0)
    self._msg("r: no more notes, appending None...")
    #self._queue.appendLeft(None)   # signal end
    self._queue.insert(0,None)   # signal end
    self._msg("r: end of reader task...")

  # --- dispatcher task   ----------------------------------------------------

  async def _dispatch(self):
    """ dispatcher task providing notes to the buzzers """

    self._msg("d: starting dispatcher task...")
    self._start  = time.monotonic()
    end_of_music = self._start
    note_nr = 0
    while True:

      # check for empty queue
      if not len(self._queue):     # nothing to play
        await asyncio.sleep(0)
        continue

      # check for end of music and finish task
      if self._queue[-1] is None:  # end of music
        self._msg(f"d: end of music")
        self._queue.pop()
        # wait for music to finish
        await asyncio.sleep(max(0,end_of_music-time.monotonic()))
        self._msg(f"d: dispatcher task finished")
        self.stop()
        return

      # peek at first note in queue, sleep until due
      rtime = time.monotonic() - self._start  # relative time
      if rtime < self._queue[-1][0]:
        self._msg(
          f"d: nothing due, waiting for {self._queue[-1][0]-rtime:.3}s...")
        await asyncio.sleep(self._queue[-1][0]-rtime)

      # now at least one note is due: dispatch notes to buzzers
      self._msg(f"d: dispatching notes")
      rtime = time.monotonic() - self._start
      while (len(self._queue) and
             self._queue[-1] is not None and rtime >= self._queue[-1][0]):
        note = self._queue.pop()
        note_nr += 1
        self._msg(f"   waiting for buzzer...")
        bnr,b = await self._free_buzzer()
        self._msg(f"   playing note {note_nr} on buzzer {bnr}: {note}")
        t = asyncio.create_task(b.tone(*note[1:]))
        rtime = time.monotonic() - self._start
        end_of_music = max(end_of_music,time.monotonic()+note[2])
      self._msg(f"d: dispatching done")

  # ---  play   --------------------------------------------------------------

  async def play(self,filename=None, song=None, bpm=None, ref=None, loop=False):
    """ play music """
    self._stop    = False
    self._pause   = False
    self.init()

    self._msg("p: starting play")
    self._tasks.extend(
      [asyncio.create_task(self._read(filename,song,bpm,ref)),
       asyncio.create_task(self._dispatch()),
       asyncio.create_task(self._gc())])
    await asyncio.gather(*self._tasks)
    self._msg("p: play finished")

  # --- pause song   ----------------------------------------------------------

  def pause(self):
    """ pause the player """
    self._pause   = True

  # --- stop song   ----------------------------------------------------------

  def stop(self):
    """ stop the player """
    for t in self._tasks:
      try:
        if not t.done():
          t.cancel()
      except:
        pass
    self._tasks =  []
    self._stop = True

  # --- resume song   --------------------------------------------------------

  def resume(self):
    """ resume playing after pause """

    self._pause = False

  # --- init buzzers   -------------------------------------------------------

  def init(self):
    """ init buzzers """

    for buzzer in self._buzzers:
      buzzer.init()

  # --- deinit buzzers   -----------------------------------------------------

  def deinit(self):
    """ deinit buzzers """

    for buzzer in self._buzzers:
      buzzer.deinit()
