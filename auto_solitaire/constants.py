SCREEN_HEIGHT = 2340
SCREEN_WIDTH = 1080

RANKS = "A23456789TJQK"
SUITS = "SDCH"

from positions import Position

FOUNDATION_POSITIONS = {suit: Position(x, 392) for suit, x in zip(SUITS, [84, 238, 390, 542])}
WASTE_POSITION = Position(780, 392)
STOCK_POSITION = Position(1000, 392)
TABLEAU_POSITIONS = (Position(x, 643) for x in (84, 238, 390, 542, 694, 846, 1000))
