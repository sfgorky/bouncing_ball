from PyQt4 import  QtGui
from PyQt4 import QtCore 
from PyQt4.QtGui import QColor
from PyQt4.QtCore import QRect

from random import *
from Sprite import GraphicalObject

import colorsys 
def get_random_color( ):
    golden_ratio_conjugate = 0.618033988749895
    h = random( ) # use random start value
    h += golden_ratio_conjugate
    h %= 1
    (r,g,b) = colorsys.hsv_to_rgb(h, 0.5, 0.95)
    rgb = ( (int)(r*255), (int)(g*255), (int)(b*255))
    return QColor(rgb[0], rgb[1], rgb[2])  
  
###############################################################################

class RotatingBouncer (GraphicalObject):
   def __init__( self, position,
                       radius,
                       color,
                       boundary,
                       sound_status):
      GraphicalObject.__init__(self, center=position, boundary=boundary, radius=radius)
      self.color = color
      self.back_color = get_random_color( )
      self.hit_wall_sound.set_sound_status(sound_status)

   # turn ON/OFF sound
   def set_sound_status(self, status):
       self.hit_wall_sound.set_sound_status(status)

   def draw(self, painter):
      painter.setBrush(self.color)
      r = self.get_radius( )
      
      painter.drawEllipse( self.center.x()- r, self.center.y()-r, r*2, r*2 )
       
      #Graphica.draw(self, painter) # run the upper class draw() first
      saved_graphics_transform  =  painter.combinedTransform()

      #  First we move the zero point of the coordinate system into
      #  the center point of the ball.
      painter.translate(self.center.x(), self.center.y())
      #  Rotate the coordinate system as much as is the value of
      #  the data field self.current_rotation.
      painter.rotate(self.get_rotation_angle( ))
      #painter.setBrush(Qt.darkGreen)
      painter.setBrush(self.back_color)

      pieRegion = QRect(-r, -r, r*2, r*2)
      #  Fill one quarter of the ball with black color.
      painter.drawPie(pieRegion, 0, 90*16 )
      #  Fill another quarter of the ball with black color.
      painter.drawPie(pieRegion, 180*16, 90*16)
      #  Finally we restore the original coordinate system.
      painter.setTransform( saved_graphics_transform )

###############################################################################


