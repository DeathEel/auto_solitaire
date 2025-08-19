import cv2
import adb
import game

def main():
    # Initialise all 52 Card objects to a set
    unfound_cards = set(game.Card(rank, suit) for rank in range(13) for suit in range(4))

    # Initial screen capture
    screen = adb.Screen()

    # Set up game state
    state = game.GameState()

    # Find tableau cards and update game state
    for i in range(7):
        found_card = state.find_cards(screen.tableau_imgs[i], (i * 154, 550), unfound_cards, 1)[0]
        state.tableau[found_card.get_col()].append(found_card)
    print(unfound_cards)
    state.print_state()

    # Run through stock and update game state
    for _ in range(24):
        state.move_stock_to_waste(screen, unfound_cards)
        state.print_state()
    state.move_waste_to_stock(screen)
    print(unfound_cards)
    state.print_state()
    
if __name__ == "__main__":
    main()
