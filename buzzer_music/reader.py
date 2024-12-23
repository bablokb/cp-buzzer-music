# ----------------------------------------------------------------------------
# The MusicReader class wraps reading the notes from a file or a string.
#
# Note that this class uses the onlinesequencer.net schematic format:
# Time, Note, Duration, Instrument; ...
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
    pass

  # --- read song from a file   ----------------------------------------------

  def read(self,filename):
    """ read and parse a file with notes """

    file_size = os.stat(filename)[6]
    n_total = 0
    rest = ""
    with open(filename,"rt") as file:
      while n_total < file_size:
        buf = file.read(BUF_SIZE)
        for result in self._parse(rest+buf):
          if isinstance(result,tuple):
            yield result
          else:
            rest = result
            break
        n_total += len(buf)

    # in case the song does not end with a ';'
    if rest:
      yield from self._parse(rest+";")

  # --- load song from a string   --------------------------------------------

  def load(self,song):
    """ parse a string with notes """

    song = song.replace("\n","").replace("\r","")
    if song[-1] != ';':
      song += ';'
      yield from self._parse(song)
      
  # --- parse song   ---------------------------------------------------------

  def _parse(self,buffer):
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
        t, pitch, duration, _ = note.split(" ")   # ignore instrument
        yield t, pitch, duration
      except:
        raise
    yield rest
