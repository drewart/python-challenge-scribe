import time
import os
import math
from enum import Enum
import random
from termcolor import colored, COLORS
from threading import Thread

Wall = Enum('Wall',['TOP', 'BOTTOM', 'LEFT', 'RIGHT'])


class TerminalScribeException(Exception):

    def __init__(self, message=''):
       super().__init__(colored(message, 'red'))

class InvalidParameter(TerminalScribeException):
    pass

class Canvas:
    def __init__(self, width, height, scribes=[], framerate=0.5):
        self._x = width
        self._y = height
        self._canvas = [[' ' for y in range(self._y)] for x in range(self._x)]
        self.scribes = scribes
        self.framerate = framerate
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

    def is_out_of_bounds(self, pos):
        if round(pos[0]) < 0 or round(pos[1]) < 0 or round(pos[0]) >= self._x or round(pos[1]) >= self._y:
            return True
        else:
            return False

    def setPos(self, pos, mark):
        """
        >>> c = Canvas(10,10)
        >>> c.setPos((20,20), '.')
        Traceback (most recent call last):
        ...
        ValueError: pos out of bounds max (10,10)
        """
        if self.is_out_of_bounds(pos):
            raise ValueError("pos out of bounds max ({0},{1})".format(self._x,self._y))
        try:
            self._canvas[round(pos[0])][round(pos[1])] = mark
        except Exception as e:
            raise TerminalScribeException('Cound not set position to {}} with mark '.format(pos, mark))

    def getPos(self, pos):
        return self._canvas[pos[0]][pos[1]]

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def go(self):
        max_moves = max([len(scribe.moves) for scribe in self.scribes])
        for i in range(max_moves):
            for scribe in self.scribes:
                threads = []
                if len(scribe.moves) > i:
                    args = scribe.moves[i][1]+[self]
                    threads.append(Thread(target=scribe.moves[i][0], args=args))
                [thread.start() for thread in threads]
                [thread.join() for thread in threads]

            self.print()
            time.sleep(self.framerate)

    def print(self):
        if not self.can_print:
            return
        self.clear()
        for y in range(self._y):
            print(' '.join([col[y] for col in self._canvas]))

class CanvasAxis(Canvas):
    # Pads 1-digit numbers with an extra space
    def format_axis_number(self, num, y=True):
        if not y and (num % 10 == 9 or ((num+1) % 5 == 0 and num > 10)):
            return ''
        if num % 5 != 0:
            if not y:
                return ' '
            else:
                return '  '
        if y and num < 10:
            return ' '+str(num)

        # create space before x double digit
        return str(num)

    def print(self):
        self.clear()
        for y in range(self._y):
            print(self.format_axis_number(y) + ' '.join([col[y] for col in self._canvas]))

        print('  '+' '.join([self.format_axis_number(x, False) for x in range(self._x)]))
        # debug fix
        #print('  '+' '.join([str(x % 10) for x in range(self._x)]))

class TerminalScribe:
    def __init__(self, color='red', mark='*', trail='.', pos=(0,0), framerate=.05):
        self.moves = []
        if color not in COLORS:
            raise InvalidParameter(f'color {color} not a valid color ({", ".join(list(COLORS.keys()))})')

        if len(str(trail)) != 1:
            raise InvalidParameter('Trail must be a single character')
        self.trail = str(trail)

        if len(str(mark)) != 1:
            raise InvalidParameter('Mark must be a single character')
        self.mark = str(mark)

        self.color=color
        #self.canvas = canvas
        self.mark = mark
        self.trail = trail
        self.framerate = framerate
        self.pos = pos
        self.direction = 0
        self.pos_hist = []
        self.direction_history = []
        self.show_direction_history = False

    def draw(self, pos, canvas):
        """
        test draw
        >>> c = Canvas(20,20)
        >>> c.can_print = False
        >>> ts = TerminalScribe()
        >>> ts.set_position((0,0))
        >>> ts.set_direction(135)
        >>> ts.forward(1)
        >>> c.scribes.append(ts)
        >>> c.go()
        >>> c.getPos((0, 0)) + c.getPos((0, 1)) + c.getPos((1, 0)) + c.getPos((1, 1))
        '.  *'

        """
        canvas.setPos(self.pos, colored(self.trail, self.color))
        self.pos = pos
        canvas.setPos(self.pos, colored(self.mark, self.color))
        self.pos_hist.append(pos)

        if self.show_direction_history:
            print("History:",self.direction_history)


    def set_color(self, color_name):
        def _set_color(self, color_name):
            self.color = color_name
        self.moves.append((_set_color, [self, color_name]))

    def set_position(self, pos):
        def _set_position(self, pos, _):
            self.pos = pos
        self.moves.append((_set_position, [self, pos]))

    def calc_next_pos(self):
        x = math.sin((self.direction / 180) * math.pi)

        y = math.cos((self.direction / 180) * math.pi)

        y = y * -1
        pos = [self.pos[0]+x, self.pos[1]+y]
        return pos


    def forward(self, distance=1):
        if self.direction < 0 or self.direction > 360:
            raise ValueError('direction set out of bounds {} needs to be between 0 to 360'.format(self.direction))

        def _forward(self, canvas):


            pos = self.calc_next_pos()
            # bounce check
            wall = canvas.hitsWall(pos)
            if not wall:
                self.draw(pos, canvas)
            else:
                # TODO note edge case with corners
                self.direction = self.get_reflection_degree(wall, self.direction)
                pos = self.calc_next_pos()
                self.draw(pos, canvas)

            if self.direction not in self.direction_history:
                self.direction_history.append(self.direction)
            if self.direction < 0:
                raise ValueError('no neg direction: last_direction: ', self.direction_history[-2], ' current:', self.direction)

        for i in range(distance):
            self.moves.append((_forward,[self]))

    # reflection of 360 degree based on in box walls
    def get_reflection_degree(self, wall, degree_in):
        degree_out = -1
        if wall == Wall.TOP:
            # in 270 -- 90
            if degree_in >= 0 and degree_in <= 90:
               degree_out = 180 - degree_in
            elif degree_in >= 270 and degree_in <= 360:
                degree_out = 270 + (270 - degree_in)

        elif wall == Wall.BOTTOM:
            # in 90 -- 270
            if degree_in >= 90 and degree_in <= 180:
                degree_out = degree_in - 90
            elif degree_in >= 180 and degree_in < 270:
                degree_out = 360 - (degree_in - 180)

        elif wall == Wall.LEFT:
            # in 181 -- 359
            if degree_in >= 180 and degree_in <= 360:
                degree_out = 360 - degree_in

        elif wall == Wall.RIGHT:
            # in 0 - 179
            if degree_in >= 0 and degree_in <= 180:
                degree_out = 360 - degree_in


        return degree_out

    def set_direction(self, direction):
        def _set_direction(self, direction, _):
            self.direction = direction
        self.moves.append((_set_direction, [self, direction]))

    def get_direction(self):
        return self.direction

    def draw_function(self, func):
        def _draw_function(self, func, canvas):
            pos = func(self.pos)
            wall = self.canvas.hitsWall(pos)
            if not wall:
                self.draw(pos, canvas)

        for i in range(100):
            self.moves.append((_draw_function, [self,function]))


class PlotScribe(TerminalScribe):

    def __init__(self, domain, **kwargs):
        self.x = domain[0]
        self.domain = domain
        super().__init__(**kwargs)

    def plot_x(self, func):

        def _plot_x(self, func, canvas):
            pos = [self.x, func(self.x)]
            if pos[1] and not canvas.hitsWall(pos):
                self.draw(pos, canvas)
            self.x = self.x + 1

        for x in range(self.domain[0], self.domain[1]):
            self.moves.append((_plot_x, [self, func]))


class FunctionScribe(TerminalScribe):

    def draw_function(self, func, move_count=100):

        def _draw_function(self, func, canvas):
            pos = func(self)
            wall = canvas.hitsWall(pos)
            if not wall:
                self.draw(pos, canvas)

        for i in range(move_count):
            self.moves.append((_draw_function, [self, func]))

class RobotScribe(TerminalScribe):

    def calc_next_pos(self):
        x = 0
        y = 0
        if self.direction == 180:
            y += 1
        elif self.direction == 0 or self.direction == 360:
            y -= 1
        elif self.direction == 90:
            x += 1
        elif self.direction == 270:
            x -= 1

        pos = [self.pos[0]+x, self.pos[1]+y]
        return pos


    def up(self, distance=1):
        self.set_direction(0)
        self.forward(distance)

    def down(self, distance=1):
        self.set_direction(180)
        self.forward(distance)

    def right(self, distance=1):
        self.set_direction(90)
        self.forward(distance)

    def left(self, distance=1):
        self.set_direction(270)
        self.forward(distance)

class ShapeScribe(RobotScribe):

    def draw_square(self, size):
        # top left to top right
        self.right(size)
        self.down(size)
        self.left(size)
        self.up(size)


class WalkScribe(FunctionScribe):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 0
        self.color_list = list(COLORS.keys())
        self.color_index = 0
        self.last_color_index = -1

    def calc_next_pos(self):
        dir = self.direction + random.randrange(-10,10,1)
        if dir <= 0:
            dir = 360 + dir
        elif dir > 360:
            self.direction = self.direction - 360
        self.step += 1

        if self.step % 10 == 0:
            # change color make sure there is a new color
            while True:
                color_index = random.randrange(len(self.color_list))
                if self.color_index != self.last_color_index:
                    break

                self.color = self.color_list[color_index]
            self.last_color_index = self.color_index

        return super().calc_next_pos()


    def walk(self, distance=1000):
        self.set_direction(random.randrange(360))
        i = 0
        while i < distance:
            self.forward()
            # change direction
            i += 1



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
        scribe['scribe'] = RobotScribe(canvas)
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
    scribe = ShapeScribe(canvas)
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

def test_base_func():
  canvas = Canvas(30, 30)
  scribe = TerminalScribe(canvas)
  scribe.pos = (5, 5)
  scribe.set_color('green')
  scribe.draw_function(my_draw_function)

def sine(x):
    return 5 * math.sin(x/4) + 10

def cosine(x):
    return 5 * math.cos(x/4) + 10

def x2(x):
    return 2 * x + 1


def test_plot():
  canvas = CanvasAxis(50, 30)
  scribe = PlotScribe(canvas)
  scribe.pos = (0, 0)
  scribe.set_color('red')
  scribe.plot_x(sine)
  scribe.set_color('green')
  scribe.pos = (0, 0)
  scribe.plot_x(cosine)
  scribe.set_color('blue')
  scribe.pos = (0, 0)
  scribe.pos = (0, 0)
  scribe.plot_x(x2)

def my_random(scribe: FunctionScribe):
    scribe.pos
    scribe.direction = random.randrange(360)
    pos = scribe.calc_next_pos()
    return pos


def test_func_scribe():
  canvas = Canvas(50, 30)
  scribe = FunctionScribe(canvas)
  scribe.pos = (20,20)
  scribe.draw_function(my_random)

def test_walk_scribe():
  canvas = Canvas(50, 30)
  scribe = WalkScribe(canvas)
  scribe.pos = (20,20)
  scribe.walk()

def run_threads():
    scribe1 = TerminalScribe(color='green')
    scribe1.set_position((10,10))
    scribe1.set_direction(135)
    scribe1.forward(100)

    scribe2 = ShapeScribe(color='yellow')
    scribe2.set_position((5, 5))
    scribe2.draw_square(10)


    scribe3 = WalkScribe(color='red')
    #scribe3.show_direction_history = True
    scribe3.set_position((15,15))
    scribe3.walk(100)

    scribe4 = PlotScribe(domain=(0,31), color='blue')
    scribe4.plot_x(sine)

    canvas = CanvasAxis(31, 31, scribes=[scribe1, scribe2, scribe3, scribe4])
    canvas.go()


def main():

    #do_forward()
    #test_bounce()
    #test_func()
    #test_plot()
    #test_func_scribe()
    #test_walk_scribe()
    run_threads()


if __name__ == '__main__':
    main()
