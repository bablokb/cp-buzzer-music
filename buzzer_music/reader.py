# ----------------------------------------------------------------------------
# The MusicReader class wraps reading the notes from a file or a string.
#
# Note that this class uses the onlinesequencer.net schematic format:
# Time, Note, Duration, Instrument; ...
#
# When reading from a filename, the music-data needs preprocessing. See
# tools/preprocess-mucic.sh. When reading from a string, the header
# ('Online Sequencer:123456:') and the trailing ':' need to be removed manually.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-buzzer-music
#
# ----------------------------------------------------------------------------

""" Implementation of class MusicReader """

import os

BUF_SIZE = 4096

class MusicReader:
  """ read notes from a file or a string """

  def __init__(self):
    """ constructor """

  # --- load song from a file or string   ------------------------------------

  def load(self,filename=None, song=None, bpm=60, ref=0.25):
    """ load music from a file or a given string """

    if filename is None and song is None:
      raise ValueError("must provide either filename or song as string")

    if filename is None:
      yield from self._load(song,60*ref/bpm)
    else:
      yield from self._read(filename,60*ref/bpm)
      
  # --- read song from a file   ----------------------------------------------

  def _read(self,filename,btime):
    """ read and parse a file with notes """

    with open(filename,"rt") as file:
      for note in file:
        if not note or note[0] == "#":  # skip empty lines and comments
          continue
        t, pitch, duration, *_ = note.split(" ")   # ignore instrument
        yield float(t)*btime, pitch, float(duration)*btime

  # --- load song from a string   --------------------------------------------

  def _load(self,song,btime):
    """ load music from a file or a given string """

    song = song.replace("\n","").replace("\r","")
    if song[-1] != ';':
      song += ';'
    notes = [note for note in self._parse(song,btime) if note]
    notes.sort(key=lambda note: note[0])
    yield from notes

  # --- parse song   ---------------------------------------------------------

  def _parse(self,buffer,btime):
    """ parse song-fragment """

    buffer = buffer.lstrip(";")
    notes = buffer.split(";")
    # If we have a complete note with trailing ';', then the last note is empty
    # Otherwise, the last note is (maybe) incomplete, so we return it for
    # later processing.
    if not notes[-1] or len(notes[-1].split(" ")) != 4:
      rest = notes.pop()
    else:
      rest = ""

    # at a given t, we can have multiple notes. So create a list of lists
    # with one list of notes for every given t
    for note in notes:
      try:
        t, pitch, duration, *_ = note.split(" ")   # ignore instrument
        yield float(t)*btime, pitch, float(duration)*btime
      except:
        raise
    yield rest
