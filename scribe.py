import time
import os

class Canvas:
    def __init__(self, width, height):
        self._x = width
        self._y = height
        self._canvas = [[' ' for y in range(self._y)] for x in range(self._x)]
        self.can_print = True

    def setPos(self, pos, mark):
        self._canvas[pos[0]][pos[1]] = mark

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
        time.sleep(self.framerate)

    def drawSquare(self, size):
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
        for y in range(size-1, 0, -1):
            self.draw((0, y))


def main():
    canvas = Canvas(30, 30)
    scribe = TerminalScribe(canvas)


    #for i in range(0, 10):
    #    for j in range(0, 10):
    #        scribe.draw((i, j))
    #    time.sleep(0.1)

    scribe.drawSquare(20)

if __name__ == '__main__':
    main()
