import cv2
import numpy as np
from collections import deque

SCREEN_HEIGHT = 2340
SCREEN_WIDTH = 1080

FOUNDATION_0_X = 84
FOUNDATION_0_Y = 392
FOUNDATION_1_X = 238
FOUNDATION_1_Y = 392
FOUNDATION_2_X = 390
FOUNDATION_2_Y = 392
FOUNDATION_3_X = 542
FOUNDATION_3_Y = 392
WASTE_X = 780
WASTE_Y = 392
STOCK_X = 1000
STOCK_Y = 392
TABLEAU_0_X = 84
TABLEAU_1_X = 238
TABLEAU_2_X = 390
TABLEAU_3_X = 542
TABLEAU_4_X = 694
TABLEAU_5_X = 846
TABLEAU_6_X = 1000

class Card:
    def __init__(self, template_path, pos=None):
        self.rank = template_path[5]
        self.suit = template_path[6]
        self.template_path = template_path
        self.pos = pos

class GameState:
    def __init__(self):
        self.tableau = [[None] * i for i in range(7)]
        self.foundation = [[] for _ in range(4)]
        self.stock = deque([None] * 24)
        self.waste = []

    def print_state(self):
        for i in range(7):
            column = self.tableau[i]
            cards = []
            for card in column:
                if not card:
                    cards.append(None)
                else:
                    cards.append(card.rank + card.suit)
            print(f"TABLEAU COLUMN {i}: {cards}")

        for i in range(4):
            column = self.foundation[i]
            cards = []
            for card in column:
                cards.append(card.rank + card.suit)
            print(f"FOUNDATION COLUMN {i}: {cards}")

        cards = []
        for card in self.stock:
            if not card:
                cards.append(None)
            else:
                cards.append(card.rank + card.suit)
        print(f"STOCK: {cards}")

        cards = []
        for card in self.waste:
            cards.append(card.rank + card.suit)
        print(f"WASTE: {cards}")

    # Updates position of Card objects passed
    def find_cards(self, screen, cards, threshold=0.98):
        found_cards = []
        for card in cards:
            print(f"Finding {card.rank}{card.suit}")
            template = cv2.imread(card.template_path, cv2.IMREAD_COLOR)
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            pos = list(zip(*loc[::-1]))
            if pos:
                x, y = pos[0]
                crop_height, crop_width = screen.shape[:2]  # offset positions by cropped amount
                corrected_pos = (x + 70 + (SCREEN_WIDTH - crop_width), y + 40 + (SCREEN_HEIGHT - crop_height))    # center position on card
                card.pos = corrected_pos    # update position of card
                found_cards.append(card)
                print(f"Found {card.rank}{card.suit} at {card.pos}")
        cards.difference_update(found_cards)
        return found_cards

    # Updates GameState members
    def update_state(self, cards):
        for card in cards:
            print(f"Updating {card.rank}{card.suit} with new position {card.pos}")
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
        screen.tap(STOCK_X, STOCK_Y)
        drawn_card = self.stock.popleft()
        if drawn_card is None:
            screen.capture()
            found_cards = self.find_cards(screen.waste_img, unfound_cards)
            self.waste.append(found_cards[0])
        else:
            self.waste.append(drawn_card)

    def move_waste_to_stock(self, screen):
        screen.tap(STOCK_X, STOCK_Y)
        for card in self.waste:
            self.stock.append(card)
        self.waste = []
