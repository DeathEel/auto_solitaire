from copy import deepcopy

def pick_column_by_king(state, moves):
    king_available = state.has_playable_king()
    def column_size(move):
        return len(state.tableau[move.src_card.position.col()])
    return min(moves, key=column_size) if king_available else max(moves, key=column_size)

def pick_tableau_move_by_king(state, moves):
    if not moves:
        return None
    if len(moves) == 1:
        return moves[0]
    return pick_column_by_king(state, moves)

def pick_king_for_empty_column(state, moves):
    if len(moves) == 1:
        return moves[0]
    for move in moves:
        if (Q_tableau := state.find_card_in_tableau("Q")) and not Q_tableau.is_same_color(move.src_card):
            return move
        elif (J_tableau := state.find_card_in_tableau("J")) and J_tableau.is_same_color(move.src_card):
            return move
        elif (T_tableau := state.find_card_in_tableau("T")) and not T_tableau.is_same_color(move.src_card):
            return move
    return moves[0]

def filter_moves(moves, condition):
    return [move for move in moves if condition(move)]
                
class Solver:
    def __init__(self, state, moves_list):
        self.state = state
        self.moves_list = moves_list
        self.history = History()
        self.seen_states = set()
        self.last_was_undo = False

    def play_move(self, screen, unfound_cards):
        # Check for duplicate game state
        if self.state in self.seen_states:
            print(f"Undoing")
            previous_state = self.history.pop()
            if previous_state:
                self.state.move_undo(screen)
                self.state = previous_state
                self.last_was_undo = True
                return

        self.seen_states.add(self.state)
        self.last_was_undo = False

        self.history.push(self.state)

        # Autocomplete if available
        if not unfound_cards:
            print(f"Autocompleting")
            self.state.move_autocomplete(screen)
            return True

        # Move A or 2 from stock to foundation
        for move in self.moves_list.stock_to_foundation:
            if move.src_card.rank != "A":
                continue
            print(f"Moving {move.src_card} from stock to foundation")
            self.state.move_stock_to_foundation(screen, move.src_card)
            return False
        for move in self.moves_list.stock_to_foundation:
            if move.src_card.rank != "2":
                continue
            print(f"Moving {move.src_card} from stock to foundation")
            self.state.move_stock_to_foundation(screen, move.src_card)
            return False

        # Move A or 2 from tableau to foundation
        for move in self.moves_list.tableau_to_foundation:
            if move.src_card.rank != "A":
                continue
            print(f"Moving {move.src_card} from tableau to foundation")
            self.state.move_tableau_to_foundation(screen, move.src_card, unfound_cards)
            return False
        for move in self.moves_list.tableau_to_foundation:
            if move.src_card.rank != "2":
                continue
            print(f"Moving {move.src_card} from tableau to foundation")
            self.state.move_tableau_to_foundation(screen, move.src_card, unfound_cards)
            return False

        # Move K from tableau into empty columns
        candidate_moves = filter_moves(self.moves_list.tableau_to_tableau, lambda move: move.src_card.rank == "K" and not move.src_card.is_bottom_card(self.state))
        if candidate_moves:
            move = pick_king_for_empty_column(self.state, candidate_moves)
            print(f"Moving {move.src_card} from tableau to empty column {move.dst_position.col()}")
            self.state.move_tableau_to_tableau(screen, move.src_card, move.dst_position, unfound_cards)
            return False

        # Move K from stock into empty columns
        candidate_moves = filter_moves(self.moves_list.stock_to_tableau, lambda move: move.src_card.rank == "K")
        if candidate_moves:
            move = pick_king_for_empty_column(self.state, candidate_moves)
            print(f"Moving {move.src_card} from stock to empty column {move.dst_position.col()}")
            self.state.move_stock_to_tableau(screen, move.src_card, move.dst_position)
            return False

        # Empty columns for K
        if self.state.has_playable_king():
            for move in self.moves_list.tableau_to_tableau:
                if move.src_card.rank == "K" or not move.src_card.is_bottom_card(self.state):
                    continue
                print(f"Moving {move.src_card} to tableau to create empty column for K")
                self.state.move_tableau_to_tableau(screen, move.src_card, move.dst_position)
                return False
            for move in self.moves_list.tableau_to_foundation:
                if move.src_card.rank == "K" or not move.src_card.is_bottom_card(self.state):
                    continue
                print(f"Moving {move.src_card} to foundation to create empty column for K")
                self.state.move_tableau_to_foundation(screen, move.src_card)
                return False

        # Expose hidden cards by moving to tableau
        candidate_moves = filter_moves(self.moves_list.tableau_to_tableau, lambda move: move.src_card.card_behind(self.state) is None and not move.src_card.is_bottom_card(self.state))
        if candidate_moves:
            move = pick_tableau_move_by_king(self.state, candidate_moves)
            print(f"Moving {move.src_card} from tableau to tableau to expose hidden cards")
            self.state.move_tableau_to_tableau(screen, move.src_card, move.dst_position, unfound_cards)
            return False

        # Expose hidden cards by moving to foundation
        candidate_moves = filter_moves(self.moves_list.tableau_to_foundation, lambda move: move.src_card.card_behind(self.state) is None and not move.src_card.is_bottom_card(self.state))
        if candidate_moves:
            move = pick_tableau_move_by_king(self.state, candidate_moves)
            print(f"Moving {move.src_card} from tableau to foundation to expose hidden cards")
            self.state.move_tableau_to_foundation(screen, move.src_card, unfound_cards)
            return False

        # Play from stock to tableau
        for move in self.moves_list.stock_to_tableau:
            print(f"Moving {move.src_card} from stock to tableau")
            self.state.move_stock_to_tableau(screen, move.src_card, move.dst_position)
            return False

        # Play from tableau to foundation:
        for move in self.moves_list.tableau_to_foundation:
            print(f"Moving {move.src_card} from tableau to foundation")
            self.state.move_tableau_to_foundation(screen, move.src_card)
            return False

        # Play everything else
        for move in self.moves_list.tableau_to_tableau:
            print(f"Moving {move.src_card} to tableau column {move.dst_position.col()}")
            self.state.move_tableau_to_tableau(screen, move.src_card, move.dst_position, unfound_cards)
            return False
        for move in self.moves_list.stock_to_tableau:
            print(f"Moving {move.src_card} to tableau column {move.dst_position.col()}")
            self.state.move_stock_to_tableau(screen, move.src_card, move.dst_position)
            return False
        for move in self.moves_list.stock_to_foundation:
            print(f"Moving {move.src_card} to foundation")
            self.state.move_stock_to_foundation(screen, move.src_card)
            return False
        for move in self.moves_list.tableau_to_foundation:
            print(f"Moving {move.src_card} to foundation")
            self.state.move_tableau_to_foundation(screen, move.src_card, unfound_cards)
            return False
        for move in self.moves_list.foundation_to_tableau:
            print(f"Moving {move.src_card} to tableau column {move.dst_position.col()}")
            self.state.move_foundation_to_tableau(screen, move.src_card, move.dst_position)
            return False

        # Undo if out of moves
        print(f"Undoing")
        previous_state = self.history.pop()
        if previous_state:
            self.state.move_undo(screen)
            self.state = previous_state
            self.last_was_undo = True

class History:
    def __init__(self):
        self.stack = []

    def push(self, state):
        self.stack.append(deepcopy(state))

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None
