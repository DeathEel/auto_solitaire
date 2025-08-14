import cv2
import numpy as np
from collections import deque

class GameState:
    def __init__(self):
        self.tableau = [[None] * i for i in range(7)]
        self.foundation = [[] for _ in range(4)]
        self.stock = deque([None] * 24)
        self.waste = []

    def find_known_card(self, screen, template_path, threshold=0.98):
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        pos = list(zip(*loc[::-1]))
        if pos:
            corrected_pos = (pos[0][0] + 70, pos[0][1] + 40)
            found_card = (template_path, corrected_pos)
            return found_card
        else:
            return None

    def find_all_cards(self, screen, template_paths, threshold=0.98):
        found_cards = []

        for template_path in template_paths:
            found_card = self.find_known_card(screen, template_path, threshold)
            if found_card:
                print(f"Found {found_card[0]} at {found_card[1]}")
                found_cards.append(found_card)

        return found_cards

    def update_game_state(self, card_infos):
        for card_info in card_infos:
            print(f"Updating {card_info[0]}, {card_info[1]}")
            card_x, card_y = card_info[1]
            col = round((card_x - 84) / 154)

            if card_y > 450:
                print(f"{card_info[0]} is in tableau, column {col}")
                self.tableau[col].append(card_info)
            elif card_y < 450 and col <= 3:
                print(f"{card_info[0]} is in foundation, column {col}")
                self.foundation[col].append(card_info)
            elif card_y < 450 and col > 3 and col <= 5:
                print(f"{card_info[0]} is in waste, column {col}")
                self.waste.append(card_info)
            else:
                print(f"{card_info[0]} is in stock, column {col}")
                self.stock.append(card_info)
