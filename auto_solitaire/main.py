import cv2
from adb import Screen
from game import GameState, Card

'''
Foundation =	(84,	392)
				(238,	392)
				(390,	392)
				(542,	392)

Waste =			(780,	392)

Stock =			(1000,	392)

Tableau =		(84,	y)
				(238,	y)
				(390,	y)
				(542,	y)
				(694,	y)
				(846,	y)
				(1000,	y)
'''

def main():
    suits = ["H", "S", "C", "D"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    template_paths = [f"data/{value}{suit}.png" for value in values for suit in suits]
    
    screen = Screen()
    game = GameState()

    # Initialise all 52 Card objects to a list
    unfound_cards = set(Card(path) for path in template_paths)

    # Initial screen capture, card find, and game update
    img = screen.capture()
    
    found_cards = game.find_cards(img, unfound_cards)
    
    game.update_state(found_cards)
    print(", ".join(f"{card.rank}{card.suit}" for card in unfound_cards))
    print(", ".join(f"{card.rank}{card.suit}" for card in found_cards))
    
    game.print_state()
    
    cv2.imshow("Screen", img)
    cv2.waitKey(0)

if __name__ == "__main__":
    main()
