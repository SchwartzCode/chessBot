import numpy as np
import chess

class chessBot:
    board = None
    def __init__(self):
        self.board = chess.Board()

    def showBoard(self):
        print(self.board)



# currently just for testing
if __name__ == "__main__":
    print('oi')
    test = chessBot()
    test.showBoard()
