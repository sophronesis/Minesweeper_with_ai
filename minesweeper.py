from random import shuffle, randint
from time import sleep
FLAG_CHAR = chr(9872) # 'F'
UNREVEALED_CHAR = "." # "#" # " "
MINE_CHAR = "*"
EMPTY_CHAR = "-"
BOARD_XRANGE = 65
BOARD_YRANGE = 36
MINE_COUNT = 220


class Board:
    """Minesweeper board class"""

    def __init__(self, size, mineCount):
        """Minesweeper board constructor"""
        self.size = size
        self.mineCount = mineCount
        minearr = [1 if i < mineCount else 0 for i in range(size['x'] * size['y'])]
        shuffle(minearr)
        self.mineBoard = [minearr[size['x'] * i:size['x'] * (i + 1)] for i in range(size['y'])]
        self.gameBoard = [[0 for i in range(size['x'])] for j in range(size['y'])]
        self.flagBoard = [[0 for i in range(size['x'])] for j in range(size['y'])]
        self.revealed = [[0 for i in range(size['x'])] for j in range(size['y'])]
        self.gameStarted = False
        self.gameOver = False
        self.gameVictory = False
    def makegameboard(self):
        for j in range(self.size['y']):
            for i in range(self.size['x']):
                self.gameBoard[j][i] = 9 if self.mineBoard[j][i] == 1 else self.countAround(self.mineBoard, j, i)
    def display(self):
        print(self.getDisplay())
    def countAround(self, matrix, y, x):
        """Count mines around given location"""
        return sum(sum(i for i in j[x - 1 if x - 1 > 0 else 0:x + 2 if x + 2 < len(j) else len(j)]) for j in
                   matrix[y - 1 if y - 1 > 0 else 0:y + 2 if y + 2 < len(matrix) else len(matrix)])
    def difficulty(self):
        return int(100 * self.mineCount / (self.size['x'] * self.size['y']))
    def getDisplay(self):
        return "\n".join("".join(
            str(self.gameBoard[n][m]) if i != 0 else UNREVEALED_CHAR if self.flagBoard[n][m] == 0 else FLAG_CHAR for
            m, i in enumerate(j)) for n, j in enumerate(self.revealed))
    def checkVictoryCondition(self):
        """Checking thats all minefield is revealed"""
        self.gameVictory = all(
            all(self.mineBoard[j][i] + self.revealed[j][i] == 1 for i in range(len(self.mineBoard[0]))) for j in
            range(len(self.mineBoard)))
    def checkMine(self, y, x):
        """Check board element for mine"""
        # check correctness of input data
        if not (y < self.size['y'] and x < self.size['x'] and x > -1 and y > -1):
            return
        # do nothing if calculated already
        if self.revealed[y][x] == 1:
            return
        # generate game board on first move
        if not self.gameStarted:
            self.makegameboard()
            self.gameStarted = True
            # move mine if find mine on first move
            if self.mineBoard[y][x] == 1:
                for n, i in enumerate(self.mineBoard):
                    if 0 in i:
                        self.mineBoard[n][i.index(0)] = 1
                        self.checkMine(y, x)
                self.mineBoard[y][x] = 0
        # end game if found mine
        if self.gameBoard[y][x] == 9:
            self.gameOver = True
            return
        if self.gameBoard[y][x] == 0:
            self.revealed[y][x] = 1
            self.flagBoard[y][x] = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if not i == j == 0:
                        self.checkMine(y + i, x + j)
        else:
            self.revealed[y][x] = 1
            self.flagBoard[y][x] = 0
        self.checkVictoryCondition()
    def putFlag(self, y, x):
        """Put flag on board or remove if already placed"""
        self.flagBoard[y][x] = 1 if self.flagBoard[y][x] == 0 and self.revealed[y][x] == 0 else 0


class AiAgent:
    def __init__(self, board):
        self.board = board

    def compareUnrevealed(self, matrix, y, x):
        """Compare unrevealed dots around given dot with dot's number"""
        flags = 0
        unrevealed = 0
        unrevealeddots = []
        if matrix[y][x].isdigit():
            number = int(matrix[y][x])
        else:
            return False, []
        for j in range(y - 1 if y - 1 > 0 else 0, y + 2 if y + 2 < len(matrix) else len(matrix)):
            for i in range(x - 1 if x - 1 > 0 else 0, x + 2 if x + 2 < len(matrix[0]) else len(matrix[0])):
                if matrix[j][i] == FLAG_CHAR:
                    flags += 1
                elif matrix[j][i] == UNREVEALED_CHAR:
                    unrevealed += 1
                    unrevealeddots.append((j, i))
                elif matrix[j][i].isdigit():
                    continue
                else:
                    print("Something strange happening in ai agent")
        return number - unrevealed - flags == 0, unrevealeddots

    def findbombs(self):
        boarddata = self.board.getDisplay()
        matrix = boarddata.split("\n")
        dots = []
        for j in range(len(matrix)):
            for i in range(len(matrix[0])):
                checkresult, tempdots = self.compareUnrevealed(matrix, j, i)
                if checkresult: dots += tempdots
        return list(set(dots))

    def compareFlags(self, matrix, y, x):
        """Compare flags around given dot with dot's number"""
        flags = 0
        unrevealed = 0
        unrevealeddots = []
        if matrix[y][x].isdigit():
            number = int(matrix[y][x])
        else:
            return False, []
        for j in range(y - 1 if y - 1 > 0 else 0, y + 2 if y + 2 < len(matrix) else len(matrix)):
            for i in range(x - 1 if x - 1 > 0 else 0, x + 2 if x + 2 < len(matrix[0]) else len(matrix[0])):
                if matrix[j][i] == FLAG_CHAR:
                    flags += 1
                elif matrix[j][i] == UNREVEALED_CHAR:
                    unrevealed += 1
                    unrevealeddots.append((j, i))
                elif matrix[j][i].isdigit():
                    continue
                else:
                    print("Something strange happening in ai agent")
        return number - flags == 0, unrevealeddots

    def findsafespots(self):
        # if mines count == flag count -> unrevealed around is mineless
        boarddata = self.board.getDisplay()
        matrix = boarddata.split("\n")
        dots = []
        for j in range(len(matrix)):
            for i in range(len(matrix[0])):
                checkresult, tempdots = self.compareFlags(matrix, j, i)
                if checkresult: dots += tempdots
        return list(set(dots))


def main():
    a = Board({'x': BOARD_XRANGE, 'y': BOARD_YRANGE}, MINE_COUNT)
    b = AiAgent(a)
    #Main game loop
    #If input:
    #0 - find bombs bot mode
    #1 - find safe spots bot mode
    #2 - activate auto bot mode
    #{x} {y} - checks (x,y) for mine
    #{x} {y} {m}:
    #if m = 0 - checks (x,y) for mine
    #if m = 1 - puts flag on (x,y)
    while not a.gameOver and not a.gameVictory:
        a.display()
        arr = list(map(int, input("input coords:\n").split()))
        if len(arr) == 3:
            x, y, mode = arr
        elif len(arr) == 1:
            if arr[0] == 0:
                dots = b.findbombs()
                print(dots)
                for i in dots: a.putFlag(*i)
                continue
            elif arr[0] == 1:
                dots = b.findsafespots()
                print(dots)
                for i in dots: a.checkMine(*i)
                continue
            else:
                while not a.gameOver and not a.gameVictory:
                    sleep(1)
                    tempdisp = a.getDisplay()
                    dots = b.findbombs()
                    for j in dots:
                        a.putFlag(*j)
                    if len(dots)>0:
                        print("\nFinding bombs:")
                        a.display()
                    dots = b.findsafespots()
                    for j in dots:
                        a.checkMine(*j)
                    if len(dots)>0:
                        print("\nFinding safe spots:")
                        a.display()
                    currdisp = a.getDisplay()
                    if tempdisp == currdisp:
                        while True:
                            y = randint(0, a.size["y"] - 1)
                            x = randint(0, a.size["x"] - 1)
                            if currdisp.split("\n")[y][x] == UNREVEALED_CHAR:
                                a.checkMine(y, x)
                                print("\nRandom mine check:")
                                a.display()
                                break
                print("\nFinal state:")
                a.display()
                break
        else:
            x, y = arr
            mode = 0
        x-=1
        y-=1
        if mode == 0:
            a.checkMine(y, x)
        elif mode == 1:
            a.putFlag(y, x)
        #elif mode == 2:
        #    b.compareFlags(a.getDisplay().split("\n"), y, x)
    print("Victory" if a.gameVictory else "Game Over")
    if (a.gameOver):    
        print("Mine positions:")
        for i in a.mineBoard:
            print("".join(MINE_CHAR if j==1 else EMPTY_CHAR for j in i))


if __name__ == "__main__":
    main()
