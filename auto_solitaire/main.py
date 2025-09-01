from adb import Screen
from game import Card, GameState
from moves import MovesList
from strategy import Solver

def pop_card_from_unfound(unfound_cards, rank, suit):
    for card in unfound_cards:
        if card.rank == rank and card.suit == suit:
            unfound_cards.remove(card)
            return card
    return None

def main():
    # Initialise all 52 Card objects to a set
    unfound_cards = set(Card(rank, suit) for rank in range(13) for suit in range(4))

    # Initial screen capture
    screen = Screen()

    # Set up game state
    state = GameState()

    #''' Comment this to have the program scan the board / Uncomment this to hardcode the board
    # Find tableau cards and update game state
    print("Scanning tableau cards...")
    for i in range(7):
        found_card = state.find_cards(screen.tableau_imgs[i], (i * 154, 550), 1, unfound_cards)[0]
        state.tableau[found_card.position.col()].append(found_card)
    #print(unfound_cards)
    print(state)

    # Run through stock and update game state
    print("Scanning stock cards...")
    for _ in range(24):
        state.move_stock_to_waste(screen, unfound_cards)
        print(state)
    state.move_waste_to_stock(screen)
    #print(unfound_cards)
    print(state)

    # Print tableau and stock as string (to hardcode for debugging)
    tableau = ""
    stock = ""
    for i in range(7):
        tableau += f"{state.tableau[i][-1]}"
    for i in range(24):
        stock += f"{state.stock[i]}"
    print(tableau)
    print(stock)
    '''
    # Hardcode tableau and stock
    tableau = "QS9CAH8D3CJDTC"
    from positions import Position
    tableau_positions = [Position(84, 643), Position(238, 673), Position(390, 703), Position(542, 733), Position(694, 763), Position(864, 793), Position(1000, 823)]
    stock = "TSTHKD3SJH6CKC7CAS9H5D5H2H7S6H4SQDKHQC4C4DTD8S7D"
    for i in range(0, len(tableau), 2):
        popped_card = pop_card_from_unfound(unfound_cards, tableau[i], tableau[i + 1])
        popped_card.position = tableau_positions[i // 2]
        state.tableau[i // 2].append(popped_card)
        unfound_cards.difference_update([popped_card])
    for i in range(0, len(stock), 2):
        popped_card = pop_card_from_unfound(unfound_cards, stock[i], stock[i + 1])
        state.stock.popleft()
        state.stock.append(popped_card)
        unfound_cards.difference_update([popped_card])
    print(state)
    #'''
    # Initialize moves list and solver
    solver = Solver(state, MovesList())

    # Strategy loop
    is_finished = False
    while not is_finished:
        solver.moves_list.generate(solver.state)
        print(solver.moves_list)
        #input("Press enter to play next move.")
        is_finished = solver.play_move(screen, unfound_cards)
        print(solver.state)
    print("Game is finished.")
    
if __name__ == "__main__":
    main()
    #screen = Screen()
    #screen.point((390, 643))
