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
    self._start   = time.monotonic()  # will be updated by play

  # --- print debug-messages   -----------------------------------------------

  def _print(self,msg):
    """ print debug-messages """
    if self._debug:
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
      self._print(f"g: starting GC-task")
      while True:
        await asyncio.sleep(GC_INTERVAL)
        self._print(f"g: free memory: {gc.mem_free()}")
        gc.collect()
        self._print(f"g: free memory: {gc.mem_free()}")
    except:
      pass
    self._print(f"g: GC-task finished")

  # --- reader task   --------------------------------------------------------

  async def _read(self,filename,song,bpm,ref):
    """ reader task providing notes to the queue """

    self._print("r: starting reader task...")
    for note in self._reader.load(filename,song,bpm,ref):
      while len(self._queue) >= self._qlimit:
        await asyncio.sleep(0)
      self._print(f"r: appending note: {note}")
      #self._queue.appendleft(note)
      self._queue.insert(0,note)
      await asyncio.sleep(0)
    self._print("r: no more notes, appending None...")
    #self._queue.appendLeft(None)   # signal end
    self._queue.insert(0,None)   # signal end
    self._print("r: end of reader task...")

  # --- dispatcher task   ----------------------------------------------------

  async def _dispatch(self):
    """ dispatcher task providing notes to the buzzers """

    self._print("d: starting dispatcher task...")
    last_note = None
    note_nr = 0
    while True:
      if not len(self._queue):     # nothing to play
        await asyncio.sleep(0)
        continue
      if self._queue[-1] is None:  # end of music
        self._print(f"d: end of music")
        self._queue.pop()
        # wait for last note to finish
        await asyncio.sleep(last_note[2])
        self._print(f"d: dispatcher task finished")
        self.stop()
        return

      now = time.monotonic() - self._start
      # if nothing is due, sleep
      if now < self._queue[-1][0]:
        self._print(
          f"d: nothing pending, waiting for {self._queue[-1][0]-now:.3}s...")
        await asyncio.sleep(self._queue[-1][0]-now)

      # collect notes which are due to play
      self._print(f"d: collecting notes")
      notes = []
      now = time.monotonic() - self._start
      while (len(self._queue) and
             self._queue[-1] is not None and now >= self._queue[-1][0]):
        note = self._queue.pop()
        note_nr += 1
        self._print(f"   processing note {note_nr}: {note}")
        notes.append((note,note_nr))
      self._print(f"d: collecting done")

      # dispatch notes
      if not len(notes):
        continue
      self._print(f"d: dispatching notes")
      for note,nnr in notes:
        self._print(f"   waiting for buzzer...")
        bnr,b = await self._free_buzzer()
        self._print(f"   playing note {nnr} on buzzer {bnr}: {note}")
        t = asyncio.create_task(b.tone(*note[1:]))
        last_note = note
      self._print(f"d: dispatching done")

  # ---  play   --------------------------------------------------------------

  async def play(self,filename=None, song=None, bpm=None, ref=None, loop=False):
    """ play music """
    self._stop    = False
    self._pause   = False
    self.init()

    self._print("p: starting play")
    self._start = time.monotonic()
    self._tasks.extend(
      [asyncio.create_task(self._read(filename,song,bpm,ref)),
       asyncio.create_task(self._dispatch()),
       asyncio.create_task(self._gc())])
    await asyncio.gather(*self._tasks)
    self._print("p: play finished")

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
