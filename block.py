class Block:
    color = (255, 255, 255)

    def __init__(self):
        self._state = 0

    def __str__(self):
        return self.__class__.__name__

    def _orientations(self):
        raise NotImplementedError()

    def rotate(self, times=1):
        for i in range(times):
            if len(self._orientations())-1 == self._state:
                self._state = 0
            else:
                self._state += 1

    def blades(self):
        return self._orientations()[self._state]

    def grid(self, pos, cols, rows):
        if cols*rows <= pos:
            return None
        grid = [None] * cols * rows
        grid[pos] = str(self)
        for x, y in self.blades():
            if pos//cols != (pos+x)//cols:
                return None
            i = pos + x + y * cols
            if i < 0:
                continue
            elif cols*rows <= i:
                return None
            grid[i] = str(self)
        return grid


class O(Block):
    color = (239, 246, 48)

    def _orientations(self):
        return (
                [(-1, 0), (-1, 1), (0, 1)],
                )


class I(Block):
    color = (48, 239, 246)

    def _orientations(self):
        return (
            [(-2, 0), (-1, 0), (1, 0)],
            [(0, -1), (0, 1), (0, 2)],
            )


class S(Block):
    color = (43, 213, 4)

    def _orientations(self):
        return (
            [(1, 0), (-1, 1), (0, 1)],
            [(0, -1), (1, 0), (1, 1)],
            )


class Z(Block):
    color = (213, 4, 4)

    def _orientations(self):
        return (
            [(-1, 0), (0, 1), (1, 1)],
            [(1, -1), (1, 0), (0, 1)],
            )


class L(Block):
    color = (255, 132, 0)

    def _orientations(self):
        return (
            [(-1, 1), (-1, 0), (1, 0)],
            [(0, -1), (0, 1), (1, 1)],
            [(-1, 0), (1, 0), (1, -1)],
            [(-1, -1), (0, -1), (0, 1)],
            )


class J(Block):
    color = (48, 48, 246)

    def _orientations(self):
        return (
            [(-1, 0), (1, 0), (1, 1)],
            [(0, 1), (0, -1), (1, -1)],
            [(-1, -1), (-1, 0), (1, 0)],
            [(-1, 1), (0, 1), (0, -1)],
            )


class T(Block):
    color = (170, 20, 165)

    def _orientations(self):
        return (
            [(-1, 0), (0, 1), (1, 0)],
            [(0, -1), (0, 1), (1, 0)],
            [(-1, 0), (0, -1), (1, 0)],
            [(-1, 0), (0, -1), (0, 1)],
            )
