class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

FOUNDATION_0_POS = Position(84, 392)
FOUNDATION_1_POS = Position(238, 392)
FOUNDATION_2_POS = Position(390, 392)
FOUNDATION_3_POS = Position(542, 392)
WASTE_POS = Position(780, 392)
STOCK_POS = Position(1000, 392)

TABLEAU_0_X = 84
TABLEAU_1_X = 238
TABLEAU_2_X = 390
TABLEAU_3_X = 542
TABLEAU_4_X = 694
TABLEAU_5_X = 846
TABLEAU_6_X = 1000
