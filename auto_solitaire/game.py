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

class GameState:
    def __init__(self):
        self.tableau = [[None] * i for i in range(7)]
        self.foundation = [[] for _ in range(4)]
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
    def find_cards(self, screen, cards, threshold=0.98):
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
        cards.difference_update(found_cards)
        return found_cards

    # Updates GameState members
    def update_state(self, cards):
        for card in cards:
            print(f"Updating {card} with new position {card.pos}")
            card_x, card_y = card.pos
            col = round((card_x - 84) / 154)

            if card_y > 450:
                self.tableau[col].append(card)
            elif card_y < 450 and col <= 3:
                self.foundation[col].append(card)
            elif card_y < 450 and col > 3 and col <= 5:
                self.waste.append(card)
            else:
                self.stock.append(card)

    def move_stock_to_waste(self, screen, unfound_cards):
        screen.tap(positions.STOCK_POS)
        drawn_card = self.stock.popleft()
        if drawn_card is None:
            screen.capture()
            found_cards = self.find_cards(screen.waste_img, unfound_cards)
            self.waste.append(found_cards[0])
        else:
            self.waste.append(drawn_card)

    def move_waste_to_stock(self, screen):
        screen.tap(positions.STOCK_POS)
        for card in self.waste:
            self.stock.append(card)
        self.waste = []
