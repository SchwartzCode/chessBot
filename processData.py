import numpy as np
import os, sys
import chess

# kaggle data columns
# 1.t 2.date 3.result 4.welo 5.belo 6.len 7.date_c 8.resu_c 9.welo_c 10.belo_c 11.edate_c 12.setup 13.fen 14.resu2_c 15.oyrange 16.bad_len 17.game...
dataPath = "data/kaggle_dataset.txt"

# make smaller dataset for testing
smallDataPath = "data/kaggle_dataset_small.txt"
# with open(dataPath) as f:
#     lines = f.read().split("\n")
#     with open(smallDataPath, 'w') as f_out:
#         for i in range(100):
#             f_out.write( (lines[i] + "\n") )

pieceBitBoardIndeces = {
    "P" : 0,
    "N" : 64,
    "B" : 128,
    "R" : 192,
    "K" : 256,
    "Q" : 320,
    "p" : 384,
    "n" : 448,
    "b" : 512,
    "r" : 576,
    "k" : 640,
    "q" : 704
}


def flipBitBoard(bitBoard):
    # convert bit board to other player's perspective
    flippedBoard = bitBoard.copy()
    flippedBoard[-4:-2] = bitBoard[-2:]
    flippedBoard[-2:] = bitBoard[-4:-2]
    flippedBoard[-5] = not bitBoard[-5]
    flippedBoard[:768] = np.flip( bitBoard.copy()[:768] )
    return flippedBoard

def convertGameToBoards(game, whiteWin):
    boards = 0

    gameBoard = chess.Board()
    # print(gameBoard,"\n")
    for turn in game:
        try:
            # print("new turn!")
            # apply move to existing game board, get back new board
            move = turn.split(".")[1]
            gameBoard.push_san(move)
            boardState = gameBoard.fen().split('/')

            bitBoard = np.zeros(773) # vector representation of board state in 1's and 0's
            # print(gameBoard, "\n\n")
            for i, row in enumerate(boardState):
                # convert board state to bitBoard representation
                col = 0
                # print("hey", row)
                if i<7:
                    boardRow = row
                else:
                    boardStateVals = row.split(" ") # has castling info too
                    boardRow = boardStateVals[0]
                    # handle whose turn as well as castling info
                    if (boardStateVals[1] == 'w'):
                        # add whose turn it is to state
                        bitBoard[768] = 1
                        # print("WHITE TURN", boardStateVals)
                    if "K" in boardStateVals[2]:
                        bitBoard[769] = 1 # white can castle kingside
                        # print("WHITE CASTLE KINGSIDE", boardStateVals)
                    if "Q" in boardStateVals[2]:
                        bitBoard[770] = 1 # white can castle queenside
                        # print("WHITE CASTLE QUEENSIDE", boardStateVals)
                    if "k" in boardStateVals[2]:
                        bitBoard[771] = 1 # black can castle kingside
                        # print("black CASTLE KINGSIDE", boardStateVals)
                    if "q" in boardStateVals[2]:
                        bitBoard[772] = 1 # black can castle queenside
                        # print("black CASTLE queenSIDE", boardStateVals)
                # print(i, row, boardRow)
                for elem in boardRow:
                    if elem in pieceBitBoardIndeces.keys():
                        # print('elem', elem)
                        # print(elem, pieceBitBoardIndeces[elem], row, col, '-')
                        pieceLocBitBoard = pieceBitBoardIndeces[elem] + 8*i + col # i is row index
                        bitBoard[pieceLocBitBoard] = 1
                        col+=1 # to account for square piece is on
                    else:
                        try:
                            col += int(elem) # account for empty squares
                            # print("PROBABLY A NUMBER", elem)
                        except:
                            pass
                            # print("not a number", elem)
            # print("all done")
            if whiteWin:
                if 'winningStates' in locals():
                    winningStates = np.vstack([winningStates, bitBoard])
                else:
                    winningStates = bitBoard

                losingBitBoard = flipBitBoard(bitBoard.copy())
                if 'losingStates' in locals():
                    losingStates = np.vstack([losingStates, losingBitBoard])
                else:
                    losingStates = losingBitBoard
            else:
                # black win
                if 'losingStates' in locals():
                    losingStates = np.vstack([losingStates, bitBoard])
                else:
                    losingStates = bitBoard

                winningBitBoard = flipBitBoard(bitBoard.copy())
                if 'winningStates' in locals():
                    winningStates = np.vstack([winningStates, winningBitBoard])
                else:
                    winningStates = winningBitBoard

        except:
            pass # probably empty newline line at end of file


    return winningStates, losingStates




with open(dataPath) as f:
    lines = f.read().split("\n")
    for i in range(20000):#range(len(lines)-1):
        if(lines[i][0]) == '#':
            pass
            # this line isn't a game, skip it
            # print("commented out")
        else:
            items = lines[i].split(" ")
            # print(items[0], items[2])
            if(len(items[17:]) > 1): # filter out garbage games
                if items[2] == '1-0' :
                    # white win
                    winningStates, losingStates = convertGameToBoards(items[17:], 1)
                elif items[2] == '0-1':
                    # black win
                    winningStates, losingStates = convertGameToBoards(items[17:], 0)
                else:
                    print(i, "tie")
                    continue

            # store all moves after 5 in big array
            # make sure we can skip first 5 moves and that there isn't only 1 move
            if 'allWinningStates' in locals() and winningStates.shape[0] > 5 and len(winningStates.shape) == 2:
                allWinningStates = np.vstack([allWinningStates, winningStates[5:]])
                allLosingStates = np.vstack([allLosingStates, losingStates[5:]])
            elif winningStates.shape[0] > 5 and len(winningStates.shape) == 2:
                allWinningStates = winningStates[5:]
                allLosingStates = losingStates[5:]


print(allWinningStates.shape, allLosingStates.shape)



with open('winningStates.npy', 'wb') as f:
    np.save(f, winningStates)

with open('losingStates.npy', 'wb') as f:
    np.save(f, losingStates)
