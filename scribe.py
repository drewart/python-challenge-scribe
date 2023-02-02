import time
import os
import math
from enum import Enum

from termcolor import colored

Wall = Enum('Wall',['TOP', 'BOTTOM', 'LEFT', 'RIGHT'])    

class Canvas:
    def __init__(self, width, height):
        self._x = width
        self._y = height
        self._canvas = [[' ' for y in range(self._y)] for x in range(self._x)]
        self.can_print = True

    def hitsWall(self, point):
        # TODO edge case corner bug 
        if round(point[0]) < 0:
            return Wall.LEFT
        elif round(point[0]) >= self._x:
            return Wall.RIGHT
        elif round(point[1]) < 0:
            return Wall.TOP
        elif round(point[1]) >= self._y:
            return Wall.BOTTOM
        else:
            return None

    def setPos(self, pos, mark):
        self._canvas[round(pos[0])][round(pos[1])] = mark

    def getPos(self, pos):
        return self._canvas[pos[0]][pos[1]]

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print(self):
        if not self.can_print:
            return
        self.clear()
        for y in range(self._y):
            print(' '.join([col[y] for col in self._canvas]))

class TerminalScribe:
    def __init__(self, canvas):
        self.canvas = canvas
        self.mark = '*'
        self.trail = '.'
        self.framerate = 0.05
        self.pos = [0, 0]
        self.direction = 0
        self.pos_hist = []
        self.direction_history = []

    def draw(self, pos):
        """
        test draw
        >>> c = Canvas(20,20)
        >>> c.can_print = False
        >>> ts = TerminalScribe(c)
        >>> ts.draw((1, 1))
        >>> c.getPos((0, 0)) + c.getPos((0, 1)) + c.getPos((1, 0)) + c.getPos((1, 1))
        '.  *'

        """
        self.canvas.setPos(self.pos, self.trail)
        self.pos = pos
        self.canvas.setPos(self.pos, self.mark)
        self.canvas.print()
        self.pos_hist.append(pos)

        print("History:",self.direction_history)
        
        time.sleep(self.framerate)

    def set_color(self, color_name):
        self.mark = colored('*', color_name)
        self.trail = colored('.', color_name)

    def up(self):
        pos = [self.pos[0], self.pos[1]-1]
        if not self.canvas.hitsWall(pos):
            self.draw(pos)

    def down(self):
        pos = [self.pos[0], self.pos[1]+1]
        if not self.canvas.hitsWall(pos):
            self.draw(pos)

    def right(self):
        pos = [self.pos[0]+1, self.pos[1]]
        if not self.canvas.hitsWall(pos):
            self.draw(pos)

    def left(self):
        pos = [self.pos[0]-1, self.pos[1]]
        if not self.canvas.hitsWall(pos):
            self.draw(pos)

    def calc_next_pos(self):
            x = math.sin((self.direction / 180) * math.pi)

            y = math.cos((self.direction / 180) * math.pi)

            y = y * -1
            pos = [self.pos[0]+x, self.pos[1]+y]
            return pos


    def forward(self, distance=1):
        if not self.direction:
            raise ValueError("direction not set")

        for i in range(distance):

            pos = self.calc_next_pos() 
            # bounce
            wall = self.canvas.hitsWall(pos)
            if not wall:
                self.draw(pos)
            else:
                # TODO note edge case with corners
                self.direction = self.get_reflection_degree(wall, self.direction)
                pos = self.calc_next_pos()
                self.draw(pos)
 
            if self.direction not in self.direction_history:
                self.direction_history.append(self.direction)
            if self.direction < 0:
                raise ValueError('no neg direction')

    # reflection of 360 degree based on in box walls
    def get_reflection_degree(self, wall, degree_in):
        degree_out = -1
        if wall == Wall.TOP:
            # in 270 -- 90
            if degree_in > 0 and degree_in < 90:
               degree_out = 180 - degree_in
            elif degree_in > 270 and degree_in < 360:
                degree_out = 270 + (270 - degree_in)

        elif wall == Wall.BOTTOM:
            # in 90 -- 270
            if degree_in > 90 and degree_in < 180:
                degree_out = degree_in - 90
            elif degree_in >= 180 and degree_in < 270:
                degree_out = 360 - (degree_in - 180)

        elif wall == Wall.LEFT:
            # in 181 -- 359
            if degree_in >= 180 and degree_in < 360:
                degree_out = 360 - degree_in

        elif wall == Wall.RIGHT:
            # in 0 - 179
            if degree_in >= 0 and degree_in < 180:
                degree_out = 360 - degree_in


        return degree_out

    def set_direction(self, direction):
        self.direction = direction


    def draw_square(self, size):
        # top left to top right
        for x in range(0, size):
            self.draw((x, 0))
        
        # top right to bottom right
        for y in range (1, size):
            self.draw((size - 1, y))


        # bottom right to bottom left
        for x in range(size-1, -1, -1):
            self.draw((x, size-1))
        
        # bottom left to top right
        for y in range(size-1, -1, -1):
            self.draw((0, y))

    def plot_x(self, func):
        for x in range(self.canvas._x):
            pos = [x, func(x)]
            if pos[1] and not self.canvas.hitsWall(pos):
                self.draw(pos)

    def draw_function(self, func):
        while True:
            pos = func(self.pos)
            wall = self.canvas.hitsWall(pos)
            if not wall:
                self.draw(pos)
            else:
                break


def do_scribes():

    scribes = [{'start':(10,10), 'color': 'blue', 'actions':[
            ['direction',130],['forward',10],['direction',170], ['forward',5],
            ['direction',270], ['forward',10]
            ]},
            {'start':(0,0), 'color': 'red', 'actions':[
                    ['direction',130],['forward',10],['direction',170], ['forward',5],
                    ['direction',270], ['forward',10]
                    ]},
            {'start':(20,20), 'color': 'green', 'actions':[
                    ['direction',135],['forward',15],['direction',270], ['forward',5],
                    ['direction',270], ['forward',10], ['up', 10], ['right',5]
                    ]},
                    ]
    canvas = Canvas(40, 30)


    for scribe in scribes:
        scribe['scribe'] = TerminalScribe(canvas)
        if 'color' in scribe:
            scribe['scribe'].set_color(scribe['color'])
        if 'start' in scribe:
            scribe['scribe'].pos = scribe['start']
        
        for actionData in scribe['actions']:
            action = actionData[0]
            actionValue = actionData[1]
            if action == 'direction':
                scribe['scribe'].set_direction(actionValue)
            elif action == 'forward':
                for i in range(actionValue):
                    scribe['scribe'].forward()
            elif action == 'up':
                for i in range(actionValue):
                    scribe['scribe'].up()
            elif action == 'down':
                for i in range(actionValue):
                    scribe['scribe'].down()
            elif action == 'left':
                for i in range(actionValue):
                    scribe['scribe'].left()
            elif action == 'right':
                for i in range(actionValue):
                    scribe['scribe'].right()
            else:
                raise ValueError('unknown action: ' + action[0])


def do_square():
    canvas = Canvas(30, 30)
    scribe = TerminalScribe(canvas)
    scribe.draw_square(20)

def do_forward():
    canvas = Canvas(30, 30)
    scribe = TerminalScribe(canvas)
    scribe.set_direction(45)
    scribe.pos = (10,10)
    scribe.set_color('red')
    scribe.forward(90)

    scribe2 = TerminalScribe(canvas)
    scribe2.set_direction(45)
    scribe2.pos = (20, 29)
    scribe2.set_color('blue')
    scribe2.forward(120)

def test_bounce():
    canvas = Canvas(20, 20)
    scribe = TerminalScribe(canvas)
    scribe.set_direction(93)
    scribe.pos = (0, 0)
    scribe.set_color('green')
    scribe.forward(200)

def my_draw_function(pos):
    return [pos[0]+1,pos[1]+1]

def test_func():
  canvas = Canvas(30, 30)
  scribe = TerminalScribe(canvas)
  scribe.pos = (5, 5)
  scribe.set_color('green')
  scribe.draw_function(my_draw_function)

def sine(x):
    return 5 * math.sin(x/4) + 10

def cosine(x):
    return 5 * math.cos(x/4) + 10


def test_plot():
  canvas = Canvas(50, 30)
  scribe = TerminalScribe(canvas)
  scribe.pos = (0, 0)
  scribe.set_color('red')
  scribe.plot_x(sine)
  scribe.set_color('green')
  scribe.pos = (0, 0)
  scribe.plot_x(cosine)



        

def main():

    #do_forward()
    #test_bounce()
    #test_func()
    test_plot()

if __name__ == '__main__':
    main()
