import math, random

from SoundCell import *
# v gores from 0 -- 10
# r gores from 3 -- 10

# r = 1, v = 10
# r = 10 v= 1

def get_v(r):
    P = math.pi*20.0 # momentum
    d = 1            # density
    v = P /(math.pi*r*d)
    return v

MAX_ANGLE_VELOCITY=3    
MIN_RADIUS=2           # min size of the ball
MAX_RADIUS=20          # max size of the ball


import glob
def get_sound_kit( ):
    sound_list = glob.glob("./sound/*.wav")
    return sound_list

sound_pos = 0;
sound_list = get_sound_kit( )
def new_sound_file( ):
    global sound_pos 
    sound_pos = sound_pos  + 1
    return sound_list[sound_pos % len(sound_list)];

###############################################################################

class GraphicalObject:
    def __init__( self, center, boundary, radius=10):
       self.center  = center
       self.radius  =  max(MIN_RADIUS, min(radius, MAX_RADIUS))
       self.boundary =  boundary
       self.rotation_angle =  0 
       self.rotation_velocity = MAX_ANGLE_VELOCITY - (self.radius-1.0)/MAX_RADIUS*MAX_ANGLE_VELOCITY;
             
       # velocity specifies the number of pixels the object
       # will be moved in a single movement operation.
       
       self.mass  = math.pi * self.radius**2.0
       self.global_speed  = 1.0;
       self.velocity = get_v(self.radius) #random.randrange(100.0, 400.0, 1)/100.0
       self.direction  =  random.random() * math.pi * 2

       self.hit_wall_sound = SoundCell(new_sound_file( ))
       #print "r=%g, v=%g alpha=%g"  % (self.radius, self.velocity, self.rotation_velocity)
       print "_init__ sprite..."
      
    #def __del__(self):
    #   print str("__dell__ sprite...")
    #    self.hit_wall_sound.soundFile(False)
        
    def set_sound(self, state):
        self.hit_wall_sound.set_sound(state)
        
    def get_boundry(self):
        return self.boundry

    def get_radius(self):
        return self.radius

    def get_rotation_angle(self):
        return self.rotation_angle

    def shrink(self):
        if  self.radius  > 5:
            self.radius  -=  3

    def enlarge(self):
      self.radius  = self.radius + 3

    def set_color(self, new_color):
       self.color  =  new_color

    def get_center(self):
        return self.center

    def set_radius( self, new_radius):
        if  new_radius > 3:
            self.radius  =  new_radius

    def get_velocity(self):
        return self.velocity * self.global_speed

    def get_direction(self):
        return self.direction

    #  The move() method is supposed to be called something like 25 times a second.
    def move(self):
        v = self.get_velocity( );
        self.center.setX(self.center.x() + v * math.cos(self.direction))
        self.center.setY(self.center.y() - v * math.sin(self.direction))
        hit_wall = self.correct_pos( );
        
        self.rotation_angle  += self.rotation_velocity
        if self.rotation_angle >= 360:
            self.rotation_angle  =  0
            
        if hit_wall:
            self.hit_wall_sound.play( )
        return hit_wall

    def move_right(self):
        self.center.setX(self.center.x() + self.get_velocity())

    def move_left(self):
        self.center.setX(self.center.x() - self.get_velocity())

    def move_up(self):
        self.center.setY(self.center.y() - self.get_velocity())

    def move_down(self):
        self.center.setY(self.center.y() + self.get_velocity())

    def move_to( self, pos_x, pos_y):
        self.center.setX(self.center.x()  +  pos_x)
        self.center.setY(self.center.y()  +  pos_y)

    def contains_point(self, pos):
      #  Here we use the Pythagorean theorem to calculate the distance
      #  from the given point to the center point of the ball.
      distance_from_pos_to_center  =  math.sqrt(math.pow(self.center.x()- pos.x, 2) + math.pow(self.center.y()- pos.y, 2))
      return  distance_from_pos_to_center  <=  self.radius 

    def colides(self, other):
        other_center = other.get_center( )
        d = math.sqrt(math.pow(self.center.x()-other_center.x( ), 2) + math.pow(self.center.y()-other_center.y( ), 2))
        r2 = self.get_radius( ) + other.get_radius( );
        do_colide = (True if d<r2 else False)
        #if do_colide:
        #    print "%g, %g" % (d, r2)
        return do_colide
    
    # reverts the direction of the movement    
    def revert(self):
        self.direction = 2 * math.pi - self.direction

    # sets the global speed multiplier of this
    def set_global_speed(self, spped):
        self.global_speed = max(0, min(spped, 1.0))

    # correct the direction of the object if it is out of bounddry
    def correct_pos(self):
        (hit_wall, self.center, self.direction) = self.boundary.new_direction(self.get_center(), self.get_radius(), self.direction)
        return hit_wall


###############################################################################
