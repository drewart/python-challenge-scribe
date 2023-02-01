import time
import os
import math
from enum import Enum

Wall = Enum('Wall',['TOP', 'BOTTOM', 'LEFT', 'RIGHT'])    

class Canvas:
    def __init__(self, width, height):
        self._x = width
        self._y = height
        self._canvas = [[' ' for y in range(self._y)] for x in range(self._x)]
        self.can_print = True

    def hitsWall(self, point):
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
        time.sleep(self.framerate)

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

    def forward(self, distance=1):
        if not self.direction:
            raise ValueError("direction not set")

        for i in range(distance):

            x = math.sin((self.direction / 180) * math.pi)
            y = math.cos((self.direction / 180) * math.pi)

            y = y * -1

            pos = [self.pos[0]+x, self.pos[1]+y]

            # bounce
            if not self.canvas.hitsWall(pos):
                self.draw(pos)



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

def load_scribes():

    data = [['start',(10,10)],
            ['direction',130],['forward',10],['direction',170], ['forward',5],
            ['direction',270], ['forward',10]
            ]

    canvas = Canvas(40, 40)
    scribe = TerminalScribe(canvas)

    for action in data:
        #print(action[0], action[1])
        act = action[0]
        if act == 'start':
            scribe.pos = action[1]
        elif act == 'direction':
            scribe.set_direction(action[1])
        elif act == 'forward':
            for i in range(action[1]):
                scribe.forward()
        else:
            print('unknown command'+action)

def do_square():
    canvas = Canvas(30, 30)
    scribe = TerminalScribe(canvas)
    scribe.draw_square(20)

def do_forward():
    canvas = Canvas(30, 30)
    scribe = TerminalScribe(canvas)
    scribe.set_direction(135)

    for i in range(20):
        scribe.forward()


def main():
    load_scribes()

if __name__ == '__main__':
    main()
