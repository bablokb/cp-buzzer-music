# ----------------------------------------------------------------------------
# The AsyncBuzzer class wraps low-level PWM to play tones.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-buzzer-music
#
# ----------------------------------------------------------------------------

""" Implementation of class AsyncBuzzer """

import pwmio
import asyncio

from .pitch import PITCH   # dictionary of tones mapping tone to frequency

DC_ON  = 65535
DC_OFF = 0
VOLDIV = [200, 100, 67, 50, 40, 33, 29, 22, 11, 2]

class AsyncBuzzer:
  """ asynchronous operating buzzer """

  def __init__(self,pin):
    """ constructor """
    self._pwm  = pwmio.PWMOut(pin,variable_frequency=True)
    self._lock = asyncio.Lock()
    self.busy  = False   # set early before calling tone() if necessary!

  def deinit(self):
    """ free ressources """
    self._pwm.deinit()

  async def tone(self,pitch,duration,volume=10,on_end=None):
    """ play the tone for the given duration (volume: 1-10) """

    # Note: calling tone() will not start the method, but just return
    #       a coroutine-object. Set buzzer.busy=True externally to
    #       mark the buzzer as busy if necessary. But be aware that
    #       Buzzer.busy is purely informational.

    await self._lock.acquire()
    self.busy = True
    if not volume:
      await asyncio.sleep(duration)  # just sleep for for zero volume
      return
    if volume < 1:
      volume = int(round(volume*10,0))
    elif volume > 10 and volume < 101:
      volume = int(round(volume/10,0))
    else:
      volume = min(volume,10)
    self._pwm.frequency = PITCH[pitch]
    self._pwm.duty_cycle = int(DC_ON/VOLDIV[volume-1])
    await asyncio.sleep(duration)
    self._pwm.duty_cycle = DC_OFF
    self._lock.release()
    self.busy = False

    # execute callback if provided (workaround for missing task.add_done_callback)
    if on_end:
      on_end(self)

  def busy(self):
    """ check busy state """
    return self._lock.locked()
