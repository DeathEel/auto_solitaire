import cv2
import numpy as np
from collections import deque
import positions

SCREEN_HEIGHT = 2340
SCREEN_WIDTH = 1080

class Card:
    def __init__(self, template_path=None, pos=None):
        if not template_path:
            self.rank = ""
            self.suit = ""
        else:
            self.rank = template_path[5]
            self.suit = template_path[6]
        self.template_path = template_path
        self.pos = pos

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def get_col(self):
        return round((self.pos.x - 84) / 154)

class GameState:
    def __init__(self):
        self.tableau = [[None] * i for i in range(7)]
        self.foundation = {"H": [], "S": [], "C": [], "D": []}
        self.stock = deque([None] * 24)
        self.waste = []

    def print_state(self):
        for i in range(7):
            col = self.tableau[i]
            print(f"TABLEAU COLUMN {i}: {col}")
        for i in range(4):
            col = self.foundation[i]
            print(f"FOUNDATION COLUMN {i}: {col}")
        print(f"STOCK: {self.stock}")
        print(f"WASTE: {self.waste}")

    # Updates position of Card objects passed
    def find_cards(self, screen, cards, amount_to_find, threshold=0.98):
        found_cards = []
        for card in cards:
            print(f"Finding {card}")
            template = cv2.imread(card.template_path, cv2.IMREAD_COLOR)
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            pos = list(zip(*loc[::-1]))
            if pos:
                x, y = pos[0]
                crop_height, crop_width = screen.shape[:2]  # offset positions by cropped amount
                corrected_pos = positions.Position(x + 70 + (SCREEN_WIDTH - crop_width), y + 40 + (SCREEN_HEIGHT - crop_height))  # center position on card

                card.pos = corrected_pos    # update position of card
                found_cards.append(card)
                print(f"Found {card} at {card.pos}")

                if len(found_cards) == amount_to_find:  # break early to avoid unnecessary loops
                    break
        cards.difference_update(found_cards)
        return found_cards

    # Updates GameState members
    def update_state(self, cards):
        for card in cards:
            print(f"Updating {card} with new position {card.pos}")
            card_x, card_y = card.pos
            col = card.get_col()

            if card_y > 450:
                self.tableau[col].append(card)
            elif card_y < 450 and col <= 3:
                self.foundation[col].append(card)
            elif card_y < 450 and col > 3 and col <= 5:
                self.waste.append(card)
            else:
                self.stock.append(card)

    def move_tableau_to_tableau(self, screen, src_card, dst_card, unfound_cards):
        screen.swipe(src_card.pos, dst_card.pos)

        src_col = src_card.get_col()
        dst_col = dst_card.get_col()

        src_idx = self.tableau[src_col].index(src_card)
        cut = self.tableau[src_col][src_idx:]

        del self.tableau[src_col][src_idx:]
        self.tableau[dst_col].extend(cut)

        # Case for reveal card
        if self.tableau[src_col] and self.tableau[src_col][-1] is None:
            screen.capture()
            revealed_card = self.find_cards(screen.tableau_imgs[src_col], unfound_cards, 1)[0]
            self.tableau[src_col][-1] = revealed_card

        print(f"Moved {src_card} from tableau {src_col} to tableau {dst_col}")

    def move_stock_to_waste(self, screen, unfound_cards):
        screen.tap(positions.STOCK_POS)
        
        drawn_card = self.stock.popleft()
        if drawn_card is None:
            screen.capture()
            drawn_card = self.find_cards(screen.waste_img, unfound_cards, 1)[0]
        self.waste.append(drawn_card)

        print(f"Moved {drawn_card} from stock to waste")

    def move_waste_to_tableau(self, screen, dst_card):
        screen.swipe(positions.WASTE_POS, dst_card.pos)

        src_card = self.waste.pop()
        dst_col = dst_card.get_col()
        self.tableau[dst_col].append(src_card)
        
        print(f"Moved {src_card} from waste to tableau {dst_col}")

    def move_waste_to_stock(self, screen):
        screen.tap(positions.STOCK_POS)

        for card in self.waste:
            self.stock.append(card)
        self.waste = []

        print(f"Moved all of waste to stock")

    def move_tableau_to_foundation(self, screen, src_card, unfound_cards):
        screen.tap(src_card.pos)

        src_col = src_card.get_col()
        self.foundation[src_card.suit].append(self.tableau[src_col].pop())

        # Case for reveal card
        if self.tableau[src_col] and self.tableau[src_col][-1] is None:
            screen.capture()
            revealed_card = self.find_cards(screen.tableau_imgs[src_col], unfound_cards, 1)[0]
            self.tableau[src_col][-1] = revealed_card

        print(f"Moved {src_card} from tableau {src_col} to foundation {src_card.suit}")

    def move_waste_to_foundation(self, screen):
        screen.tap(positions.WASTE_POS)

        src_card = self.waste.pop()
        self.foundation[src_card.suit].append(src_card)

        print(f"Moved {src_card} from waste to foundation {src_card.suit}")

    def move_foundation_to_tableau(self, screen, src_card, dst_card):
        screen.swipe(src_card.pos, dst_card.pos)

        dst_col = dst_card.get_col()
        self.tableau[dst_col].append(self.foundation[src_card.suit].pop())

        print(f"Moved {src_card} from foundation {src_card.suit} to tableau {dst_col}")
