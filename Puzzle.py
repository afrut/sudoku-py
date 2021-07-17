#exec(open('Puzzle.py').read())
import subprocess as sp
import numpy as np
import os

class Puzzle:
    # filename should be a text file with puzzle values
    # one line, one value in (row, column, value) format
    def __init__(self, filename):
        # initialize basic containers
        self.a = np.ones((9,9), dtype = int) * -1
        self.possible = np.empty((9,9), dtype = object)
        self.solved = np.zeros((9,9), dtype = bool)

        # read in a puzzle
        with open(filename, 'rt') as fl:
            lines = fl.read().splitlines()
        for line in lines:
            ls = line.split(',')
            x = int(ls[0])
            y = int(ls[1])
            self.a[x, y] = int(ls[2])
            self.solved[x, y] = True

        # initial scan to determine all possible values
        defaultset = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
        for x in range(self.a.shape[0]):
            for y in range(self.a.shape[1]):
                if self.a[x, y] == -1:
                    self.possible[x, y] = defaultset.copy()

    # examine all sets of possible values and discard impossible values
    def reduce(self) -> int:
        ret = 0
        for x in range(self.a.shape[0]):
            for y in range(self.a.shape[1]):
                if self.possible[x,y] is not None:
                    st = self.possible[x,y]

                    if len(st) > 0:
                        # remove possible values by examining the same row
                        vals = self.a[x,:]
                        ls = list(vals[vals > 0])
                        for val in ls:
                            st.discard(val)

                        # remove possible values by examining the same column
                        vals = self.a[:,y]
                        ls = list(vals[vals > 0])
                        for val in ls:
                            st.discard(val)

                        # remove possible values in the sub-square array
                        square = self.sub(x, y)
                        idx = square > 0
                        ls = list(square[idx])
                        for val in ls:
                            st.discard(val)

                    if len(st) == 1:
                        self.a[x,y] = st.pop()
                        self.solved[x,y] = True
                        ret = ret + 1
        return ret

    # get the 3x3 square that element (x,y) belongs to
    def sub(self, x, y) -> np.ndarray:
        starty = int(y / 3) * 3
        startx = int(x / 3) * 3
        return self.a[startx:startx + 3, starty:starty + 3]

    # continuously reduce the puzzle until it is solved
    def solve(self):
        while not(np.all(self.solved)):
            numreduced = self.reduce()

            if numreduced == 0:
                # process of elimination by rows
                for x in range(9):
                    y, value = self.eliminaterow(x)
                    if y >= 0:
                        numreduced = numreduced + 1
                        self.a[x,y] = value
                        self.solved[x,y] = True
                        self.possible[x,y].clear()
                        break
    
            if numreduced == 0:
                # process of elimination by columns
                for y in range(9):
                    x, value = self.eliminatecolumn(y)
                    if x >= 0:
                        numreduced = numreduced + 1
                        self.a[x,y] = value
                        self.solved[x,y] = True
                        self.possible[x,y].clear()
                        break

            # TODO: process of elimination by square

    # examine possible values in a row and try to reduce by process of elimination
    def eliminaterow(self, x):
        # initialize
        dctcnt = dict()
        found = False

        # get list of sets for row x
        for y in range(9):
            st = self.possible[x,y]

            if st is not None:
                for val in st:
                    if val in dctcnt.keys():
                        # increment the number of cells that have val as a
                        # possible value
                        dctcnt[val] = dctcnt[val] + 1
                    else:
                        dctcnt[val] = 1

        # search for the value where only 1 cell in this row has it as a
        # possible value ie, dctcnt[val] == 1
        for key, value in dctcnt.items():
            if value == 1:
                found = True
                possiblevalue = key
                break

        # find the column with value as one of its possible values
        if found:
            for y in range(9):
                st = self.possible[x,y]
                if st is not None:
                    if possiblevalue in st:
                        break
            return (y, possiblevalue)
        else:
            return (-1, -1)

    # examine possible values in a column and try to reduce by process of
    # elimination
    def eliminatecolumn(self, y):
        # initialize
        dctcnt = dict()
        found = False

        # get list of sets for row x
        for x in range(9):
            st = self.possible[x,y]

            if st is not None:
                for val in st:
                    if val in dctcnt.keys():
                        # increment the number of cells that have val as a
                        # possible value
                        dctcnt[val] = dctcnt[val] + 1
                    else:
                        dctcnt[val] = 1

        # search for the value where only 1 cell in this row has it as a
        # possible value ie, dctcnt[val] == 1
        for key, value in dctcnt.items():
            if value == 1:
                found = True
                possiblevalue = key
                break

        # find the column with value as one of its possible values
        if found:
            for x in range(9):
                st = self.possible[x,y]
                if st is not None:
                    if possiblevalue in st:
                        break
            return (x, possiblevalue)
        else:
            return (-1, -1)

    # TODO: implement
    #def eliminatesquare(self, x, y):

    # check if puzzle is actually solved
    def verify(self):
        # check each row
        for x in range(9):
            if len(set(self.a[x,:])) != 9:
                return False

        # check each column
        for y in range(9):
            if len(set(self.a[:,y])) != 9:
                return False

        # check each square
        for x in [0, 3, 6]:
            for y in [0, 3, 6]:
                square = self.sub(x,y)
                if len(set(list(np.ravel(square)))) != 9:
                    return False
        return True

    # string representation
    def toString(self):
        ret = str('')
        cnty = 0
        for y in range(9):
            ret = ret + '\n'
            if cnty == 3:
                ret = ret + '------------------------------\n'
                cnty = 0
            cntx = 0
            for x in range(9):
                if cntx == 3:
                    ret = ret + '|'
                    cntx = 0
                val = int(self.a[y,x])
                if val < 0:
                    val = ' '
                else:
                    val = str(val)
                ret = ret + ' {0} '.format(val)
                cntx = cntx + 1
            cnty = cnty + 1
        ret = ret[1:]
        return ret

if __name__ == '__main__':
    sp.call('cls', shell = True)

#    puzzle = Puzzle('.\\puzzles\\0004.txt')
#    print(puzzle.toString())
#    print('------------------------------')
#    puzzle.solve()
#    assert puzzle.verify()
#    print(puzzle.toString())
#    print('----------------------------------------------------------------------\n\n\n')


    dirname = '.\\puzzles'
    filenames = os.listdir(dirname)

    for filename in filenames:
        filename = dirname + '\\' + filename
        puzzle = Puzzle(filename)
        print(puzzle.toString())
        print('------------------------------')
        puzzle.solve()
        assert puzzle.verify()
        print(puzzle.toString())
        print('----------------------------------------------------------------------\n\n\n')