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

    # Find tableau cards and update game state
    for i in range(7):
        found_card = state.find_cards(screen.tableau_imgs[i], (i * 154, 550), 1, unfound_cards)[0]
        state.tableau[found_card.position.col()].append(found_card)
    #print(unfound_cards)
    state.print_state()

    # Run through stock and update game state
    for _ in range(24):
        state.move_stock_to_waste(screen, unfound_cards)
        state.print_state()
    state.move_waste_to_stock(screen)
    #print(unfound_cards)
    state.print_state()
    '''
    # Hardcode tableau and stock
    tableau = "8DKC9STH7S7C6H"
    from positions import Position
    tableau_positions = [Position(84, 643), Position(238, 673), Position(390, 703), Position(542, 733), Position(694, 763), Position(864, 793), Position(1000, 823)]
    stock = "9D5D3CQS7H8HAC8C7DKH2H2C4S4HQHJHJDKS6DKD2D9H3S6S"
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
    state.print_state()
    '''
    # Initialize moves list and solver
    solver = Solver(state, MovesList())

    # Strategy loop
    is_finished = False
    while not is_finished:
        solver.moves_list.generate(solver.state)
        solver.moves_list.print_moves()
        #input("Press enter to play next move.")
        is_finished = solver.play_move(screen, unfound_cards)
        solver.state.print_state()
    print("Game is finished.")
    
if __name__ == "__main__":
    main()
