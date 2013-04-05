import math

from PyQt4.QtGui import  *
from PyQt4.QtCore import QRectF
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import QPointF
from PyQt4.QtGui import QPolygon

class Boundary:
    def __init__( self, rectangle = QRectF( )):
        self.boundary = rectangle

    
    def new_direction(self, center, radius, direction_angle):
        hit_wall = False
        cy = center.y( )
        cx = center.x( )
        
        #  The following four if constructs must be four separate ifs.
        #  If they are replaced with an if - elif - elif - elif
        #  construct, the program will not work when the bouncer enters
        #  a corner in an angle of 45 degrees (i.e. math.pi / 4).
        if  cy-radius <= self.boundary.top():
            #  The bouncer has hit the northern 'wall' of the bouncing area.
            direction_angle = 2 * math.pi - direction_angle
            cy = self.boundary.top( ) + radius
            hit_wall = True
        if  cx - radius <= self.boundary.left():
           #  The western wall has been reached.
           direction_angle = math.pi - direction_angle
           cx = self.boundary.left( ) + radius
           hit_wall = True
        if  cy+radius  >= self.boundary.bottom():
            #  Southern wall has been reached.
            direction_angle = 2 * math.pi - direction_angle
            cy = self.boundary.bottom( ) - radius
            hit_wall = True
        if  cx+radius  >= self.boundary.right():
            #  Eastern wall reached.
            direction_angle = math.pi-direction_angle
            cx = self.boundary.right( ) - radius
            hit_wall = True

        center = QPointF(cx, cy)
        return (hit_wall, center, direction_angle)
        
    def height(self):
        return self.boundary.height( )

    def width(self):
        return self.boundary.width( )

    def draw(self, painter):
        painter.setPen(QColor(200, 0, 0))
        L = self.boundary.left( )
        R = self.boundary.right( )
        T = self.boundary.top( )
        B = self.boundary.bottom( )
        #painter.setBackground(QBrush(QColor(200, 0, 0)))
        #painter.fillRect(L, T, self.boundary.width(),  self.boundary.height(),QColor(200, 0, 0) )
        
        L = [QPoint(L, T),   QPoint(R, T), 
             QPoint(R, T),   QPoint(R, B), 
             QPoint(R, B),   QPoint(L, B), 
             QPoint(L, B),   QPoint(L, T)
            ]
        painter.drawLines(L)




