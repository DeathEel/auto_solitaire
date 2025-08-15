import cv2
from adb import Screen
from game import GameState, Card

def main():
    suits = ["H", "S", "C", "D"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    template_paths = [f"data/{value}{suit}.png" for value in values for suit in suits]
    
    # Initialise all 52 Card objects to a list
    unfound_cards = set(Card(path) for path in template_paths)

    # Initial screen capture
    screen = Screen()

    # Set up game state
    game = GameState()
    
    # Find tableau cards and update game state
    found_cards = game.find_cards(screen.tableau_img, unfound_cards, 7)
    game.update_state(found_cards)
    print(unfound_cards)
    print(found_cards)
    game.print_state()

    # Run through stock and update game state
    for _ in range(24):
        game.move_stock_to_waste(screen, unfound_cards)
        game.print_state()
    game.move_waste_to_stock(screen)
    print(unfound_cards)
    print(found_cards)
    game.print_state()
    
if __name__ == "__main__":
    main()
