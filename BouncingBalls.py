import sys
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QPointF
from PyQt4.QtCore import QMutex
from PyQt4.QtGui  import QApplication
from PyQt4.QtGui  import QPainter

from PyQt4.QtGui import QSound

from random import randrange
from time import sleep 
from itertools import combinations

from Boundary import Boundary
from RotatingBouncer import RotatingBouncer
from RotatingBouncer import get_random_color
from SoundCell import SoundCell

from BoucingBallUI import *

GLOBAL_SPEED_RANGE=(0.0, 1000.0)
###############################################################################

class AnimationThread(QThread):
    def __init__(self):
        QThread.__init__(self) 
        self.is_running =  True
        self.mutex = QMutex()

    def stop(self):
        self.is_running = False

    def get_state(self):
        return self.is_running
    
    def change_state(self):
        self.is_running = not self.is_running

    def run(self):
        while  self.is_running:
            self.mutex.lock( ) # locking may not be necessary
            self.emit(SIGNAL("window_update_request" ))
            self.mutex.unlock()
            sleep( 0.005 )  
            #QThread.sleep( 1 )  # An alternative way to sleep.


###############################################################################

# this is a debug thread - for test purpose
class ComputationThread(QThread):
   def __init__(self, animation_thread):
      QThread.__init__(self) 
      self.is_running =  True
      self.mutex = QMutex()
      self.other_thread = animation_thread

   def stop(self):
      self.is_running = False

   def run(self):
      while  self.is_running:
         self.mutex.lock() # locking may not be necessary
         raw_input("")
         #self.other_thread.stop( )
         self.mutex.unlock()
      print " run method ends "

###############################################################################
PRESSURE_TIMER = 1000
INITIAL_NB_BALL=3

class BouncingBallWindow(QtGui.QWidget):
    """
    The main window. Contains a region for the bouncing balls, and controls
    widgets.
    
    Pause Button: stop the sprite
    Reset Button: recreate the sprite list, with random sizes, speeds
    Global Speed Slider: Controls a multipler factor to all current sprite speeds.
    Nb Sprites Sliders: Number of objects in the screen
    Sound Check box: turns on/off sound
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.ui = Ui_BouncingBall() 
        self.ui.setupUi(self)
        self.setWindowTitle( "Bouncing Balls" )
        self.boundary = Boundary(self.ui.bouncingFrame.frameGeometry( ))
        
        self.ui.pressure_timer = QtCore.QTimer( )
        self.ui.pressure_timer.timeout.connect(self.pressure_measure)
        self.ui.pressure_timer.start(PRESSURE_TIMER)

        self.ui.pauseButton.clicked.connect(self.cmd_pauseButton)
        self.ui.resetButton.clicked.connect(self.cmd_resetButton)
        
        self.ui.resetButton.clicked.connect(self.cmd_resetButton)

        self.ui.globalSpeedSlider.setMinimum(GLOBAL_SPEED_RANGE[0])
        self.ui.globalSpeedSlider.setMaximum(GLOBAL_SPEED_RANGE[1])
        self.connect(self.ui.globalSpeedSlider, QtCore.SIGNAL('valueChanged(int)'), self.change_global_speed)        
        self.connect(self.ui.nbSlider, QtCore.SIGNAL('valueChanged(int)'), self.nb_slider_change)

        self.ui.SoundBox.stateChanged.connect(self.cmd_setSoundBox)
        self.ui.backgroundSoundBox.stateChanged.connect(self.cmd_setBackgroundSoundBox)
        self.ui.allowCollisionBox.stateChanged.connect(self.cmd_setCollisionBox)

        self.ui.backgroundSoundBox.hide( )

        self.setValueSignal = QtCore.pyqtSignal(int)            
        #self.setValueSignal.connect(self.ui.collisionNumber.display)      
        self.connect(self.ui.collisionNumber, SIGNAL('setValueSignal(int)'), self.ui.collisionNumber.display)
              
        self.ui.collisionNumber.display(str(0))
        
        self.backgroundSound = SoundCell("background/Autumn_Winds_preview_whitenoisemp3s-com.mp3")
        self.sound_status = False
      
        self.spriteList = [];
        self.set_nb_ball(INITIAL_NB_BALL);

        self.nb_wall_hit = 0;        
        self.total_nb_collision = 0
        self.update_balls = True
        self.allow_collision = False
        
        self.animation_thread  =  AnimationThread()
        self.connect( self.animation_thread, SIGNAL( "window_update_request" ), self.process_window_update_request )
        #  After the following method call, the program execution
        #  system will automatically call the run() method of the
        #  AnimationThread class. The run() method is executed
        #  in parallel with "this" thread.
        self.animation_thread.start()
        
    def set_nb_ball(self, nb=1):
        if nb<=0:
            self.spriteList = []
        else:
            current_size = len(self.spriteList)
            delta = (nb-current_size)
            print delta
            if delta>0:
                for i in range(0, delta):
                    size = randrange(1, 20)
                    eps = 2*size
                    center = QPointF(randrange(eps, self.boundary.width()-eps), randrange(eps, self.boundary.height()-eps))
                    self.spriteList.append(RotatingBouncer(center, size, get_random_color( ),  self.boundary, self.sound_status))
            else:
                # remove the n-th last eleemnts
                self.spriteList = self.spriteList[ : current_size-abs(delta)]
                    
        # print "debug: sprite list size: nb=%d current_size=%d" %(nb, len(self.spriteList))

    def pressure_measure(self):
        current_pressure = int(100.0* (self.nb_wall_hit / (float(PRESSURE_TIMER)/1000.0)))
        self.ui.pressureBar.setValue(current_pressure)

    # changes the temperature values (val in 0...100)
    def change_global_speed(self, val):
        alpha = val/GLOBAL_SPEED_RANGE[1]
        [ sprite.set_global_speed(alpha) for sprite in self.spriteList ]

        
    # changes the number of balls
    def nb_slider_change(self, val):
        self.set_nb_ball(val);
            
    def process_window_update_request(self):
        collision = False
        nb_wall_hit_before = self.nb_wall_hit
        if self.update_balls:
            for sprite in self.spriteList:
                 hit_wall = sprite.move( )
                 self.nb_wall_hit += hit_wall
            if self.allow_collision:
                reverted = set([])
                for S1, S2 in list(combinations(self.spriteList, 2)):
                    if S1.colides(S2):
                        reverted.add(S1)
                        reverted.add(S2)
                        collision = True
                        self.total_nb_collision += 1
                [S.revert() for S in reverted]
               
        if collision and self.ui.stopBox.isChecked( ):
            self.cmd_pauseButton( )
        if collision:
            self.ui.collisionNumber.display(str(self.total_nb_collision))
           
        if self.nb_wall_hit > nb_wall_hit_before:
            self.ui.wallCollisionNumber.display(str(self.nb_wall_hit))
        
        self.update()
        

    def cmd_pauseButton(self):
        if self.update_balls:
            self.ui.pauseButton.setText("Start")
        else:
            self.ui.pauseButton.setText("Pause")
        self.update_balls = not self.update_balls

    def cmd_setSoundBox(self, i):
        if(i == 0): # sound is off
            self.sound_status = False
            [S.set_sound_status(False) for S in self.spriteList]
            self.ui.backgroundSoundBox.hide( )
            self.backgroundSound.set_sound_status(False)
        else:      # sound is on
            self.sound_status = True
            self.ui.backgroundSoundBox.show( )
            if self.ui.backgroundSoundBox.isChecked():
                self.backgroundSound.set_sound_status(True)
                self.backgroundSound.play( )
            self.backgroundSound.set_sound_status(True)
            [S.set_sound_status(True) for S in self.spriteList]

    def cmd_setBackgroundSoundBox(self, i):
        if(i == 0): # sound is off
            self.backgroundSound.stop( )
        else:      # sound is on
            if self.sound_status:
                self.backgroundSound.set_sound_status(True)
                self.backgroundSound.play( )

    def cmd_setCollisionBox(self, i):
        if(i == 0): # collision if off
            self.allow_collision = False
            self.ui.stopBox.hide( )
        else:
            self.allow_collision = True
            self.ui.stopBox.show( )

    def cmd_resetButton(self):
        nb = len(self.spriteList)
        self.set_nb_ball(0)
        self.set_nb_ball(nb)
        self.total_nb_collision = 0
        self.nb_wall_hit = 0
        self.ui.collisionNumber.display(str(self.total_nb_collision))
        self.ui.wallCollisionNumber.display(str(self.nb_wall_hit))
        #self.setValueSignal.emit(self.total_nb_collision)
        self.emit(SIGNAL("setValueSignal(val)"), self.total_nb_collision)

    def keyPressEvent(self, event):
        if  event.key() == Qt.Key_Escape:
            [ S.move() for S in self.spriteList]

    def paintEvent( self, event):
        painter = QPainter( )
        painter.begin(self)
        [S.draw(painter) for S in self.spriteList]
           
        self.boundary.draw(painter)
        painter.end( )

    def exit_this_window(self):
        self.animation_thread.stop( )
        self.close() #is this necessary???

###############################################################################

def run(args):
    this_q_application = QApplication(args)
    main_window = BouncingBallWindow( )
    main_window.show()

    computation_thead = ComputationThread(main_window.animation_thread)
    computation_thead.start( ) 

   # The following statement specifies that when the
   # "lastWindowClosed()" signal is emitted by QApplication,
   # the Python method exit_this_window is called for the
   # PictureShowWindow object.
    this_q_application.connect( this_q_application, SIGNAL( "lastWindowClosed()" ), main_window.exit_this_window )
   
    this_q_application.exec_()
      
  
if __name__== "__main__" :
    run( sys.argv )


