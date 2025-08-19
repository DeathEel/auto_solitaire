import cv2
import numpy as np
from collections import deque
from positions import Position
import constants as C

class Card:
    def __init__(self, rank, suit, position=None):
        self.rank = C.RANKS[rank]
        self.suit = C.SUITS[suit]
        self.rank_num = rank
        self.suit_num = suit
        self.template_path = f"data/{self.rank}{self.suit}.png"
        self.position = position

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def update_position(self, offset):
        offset_x, offset_y = offset
        self.position.x += offset_x
        self.position.y += offset_y

    def col(self):
        return round((self.position.x - 84) / 154)

    def rank_difference(self, other):
        return self.rank_num - other.rank_num

    def is_same_color(self, other):
        self_color = "red" if self.suit in ["D", "H"] else "black"
        other_color = "red" if other.suit in ["D", "H"] else "black"
        return self_color == other_color

class GameState:
    def __init__(self):
        self.tableau = [[None] * i for i in range(7)]
        self.foundation = {suit: [] for suit in C.SUITS}
        self.stock = deque([None] * 24)
        self.waste = []

    def can_build(self, src_card, dst_card):
        # Cards are built on each other if descending rank and different colors
        if dst_card:
            return src_card.rank_difference(dst_card) == -1 and not src_card.is_same_color(dst_card)

        # Cards can be moved to empty column if it is King
        return src_card.rank == "K"

    def can_build_foundation(self, src_card, dst_card):
        # Cards are built on foundation if ascending rank and same suit
        if dst_card:
            return src_card.rank_difference(dst_card) == 1 and src_card.suit == dst_card.suit

        # Cards be moved to empty foundation if it is Ace
        return src_card.rank == "A"

    def print_state(self):
        for i in range(7):
            col = self.tableau[i]
            print(f"TABLEAU COLUMN {i}: {col}")
        for i in C.SUITS:
            col = self.foundation[i]
            print(f"FOUNDATION COLUMN {i}: {col}")
        print(f"STOCK: {self.stock}")
        print(f"WASTE: {self.waste}")

    # Updates position of Card objects passed
    def find_cards(self, screen, screen_offset, cards, amount_to_find, threshold=0.98):
        found_cards = []
        for card in cards:
            print(f"Finding {card}")
            template = cv2.imread(card.template_path, cv2.IMREAD_COLOR)
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            position = list(zip(*loc[::-1]))
            if position:
                x, y = position[0]
                corrected_position = Position(x + 70, y + 40)  # center position on card
                card.position = corrected_position    # initially update position of card
                card.update_position(screen_offset) # account for cropped image
                found_cards.append(card)
                print(f"Found {card} at {card.position}")

                if len(found_cards) == amount_to_find:  # break early to avoid unnecessary loops
                    break
        cards.difference_update(found_cards)
        return found_cards

    def move_tableau_to_tableau(self, screen, src_card, dst_card, unfound_cards):
        screen.swipe(src_card.position, dst_card.position)

        src_col = src_card.col()
        dst_col = dst_card.col()

        src_idx = self.tableau[src_col].index(src_card)
        cut = self.tableau[src_col][src_idx:]

        del self.tableau[src_col][src_idx:]
        self.tableau[dst_col].extend(cut)

        # Case for reveal card
        if self.tableau[src_col] and self.tableau[src_col][-1] is None:
            screen.capture()
            revealed_card = self.find_cards(screen.tableau_imgs[src_col], (src_col * 154, 550), unfound_cards, 1)[0]
            self.tableau[src_col][-1] = revealed_card

        print(f"Moved {src_card} from tableau {src_col} to tableau {dst_col}")

    def move_stock_to_waste(self, screen, unfound_cards):
        screen.tap(C.STOCK_POSITION)
        
        drawn_card = self.stock.popleft()
        if drawn_card is None:
            screen.capture()
            drawn_card = self.find_cards(screen.waste_img, (610, 0), unfound_cards, 1)[0]
        self.waste.append(drawn_card)

        print(f"Moved {drawn_card} from stock to waste")

    def move_waste_to_tableau(self, screen, dst_card):
        screen.swipe(C.WASTE_POSITION, dst_card.position)

        src_card = self.waste.pop()
        dst_col = dst_card.col()
        self.tableau[dst_col].append(src_card)
        
        print(f"Moved {src_card} from waste to tableau {dst_col}")

    def move_waste_to_stock(self, screen):
        screen.tap(C.STOCK_POSITION)

        for card in self.waste:
            self.stock.append(card)
        self.waste = []

        print(f"Moved all of waste to stock")

    def move_tableau_to_foundation(self, screen, src_card, unfound_cards):
        screen.swipe(src_card.position, C.FOUNDATION_POSITIONS[src_card.suit])

        src_col = src_card.col()
        self.foundation[src_card.suit].append(self.tableau[src_col].pop())

        # Case for reveal card
        if self.tableau[src_col] and self.tableau[src_col][-1] is None:
            screen.capture()
            revealed_card = self.find_cards(screen.tableau_imgs[src_col], (src_col * 154, 550), unfound_cards, 1)[0]
            self.tableau[src_col][-1] = revealed_card

        print(f"Moved {src_card} from tableau {src_col} to foundation {src_card.suit}")

    def move_waste_to_foundation(self, screen):
        src_card = self.waste.pop()
        screen.swipe(C.WASTE_POSITION, C.FOUNDATION_POSITIONS[src_card.suit])

        self.foundation[src_card.suit].append(src_card)

        print(f"Moved {src_card} from waste to foundation {src_card.suit}")

    def move_foundation_to_tableau(self, screen, src_card, dst_card):
        screen.swipe(src_card.position, dst_card.position)

        dst_col = dst_card.col()
        self.tableau[dst_col].append(self.foundation[src_card.suit].pop())

        print(f"Moved {src_card} from foundation {src_card.suit} to tableau {dst_col}")
