#from PyQt4.QtGui import  QSound
from collections import deque
from PyQt4.phonon import Phonon

class SoundCell:

    def __init__(self, soundFile, POOL_COUNT=3):
        self.state = True
        self.soundFile = soundFile
        self.resourcePool = deque()
        self.current = None
        self.POOL_COUNT = POOL_COUNT

        for i in xrange(self.POOL_COUNT):
            #self.resourcePool.append( QSound(soundFile) )
            player = Phonon.createPlayer(Phonon.MusicCategory, Phonon.MediaSource(soundFile));
            self.resourcePool.append(player)

    def set_sound_status(self, state):
        self.state = state
        if not self.state and self.current != None:
            self.current.stop( )
            self.current = None

    def play(self):
        if self.state:
            self.resourcePool.rotate(1)
            self.current = self.resourcePool[0]
            self.current.seek(0)
                
            #m.stop()
            self.current.play()
        else:
            if self.current != None: 
                self.current.stop()
                self.current = None

    def stop(self):
        if self.current != None: 
            self.current.stop()
            self.state = False
        
