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
    def __init__(self, state, unordered_moves_list):
        self.state = state
        self.unordered_moves_list = unordered_moves_list
        self.history = History()
        self.seen_states = set()
        self.last_was_undo = False

    def order_moves(self):
        self.ordered_moves_list = []

        # Move A or 2 from stock to foundation
        for move in self.unordered_moves_list.stock_to_foundation:
            if move.src_card.rank != "A":
                continue
            self.ordered_moves_list.append((move, "SF"))
        for move in self.unordered_moves_list.stock_to_foundation:
            if move.src_card.rank != "2":
                continue
            self.ordered_moves_list.append((move, "SF"))

        # Move A or 2 from tableau to foundation
        for move in self.unordered_moves_list.tableau_to_foundation:
            if move.src_card.rank != "A":
                continue
            self.ordered_moves_list.append((move, "TF"))
        for move in self.unordered_moves_list.tableau_to_foundation:
            if move.src_card.rank != "2":
                continue
            self.ordered_moves_list.append((move, "TF"))

        # Move K from tableau into empty columns
        candidate_moves = filter_moves(self.unordered_moves_list.tableau_to_tableau, lambda move: move.src_card.rank == "K" and not move.src_card.is_bottom_card(self.state))
        if candidate_moves:
            move = pick_king_for_empty_column(self.state, candidate_moves)
            self.ordered_moves_list.append((move, "TT"))
            
        # Move K from stock into empty columns
        candidate_moves = filter_moves(self.unordered_moves_list.stock_to_tableau, lambda move: move.src_card.rank == "K")
        if candidate_moves:
            move = pick_king_for_empty_column(self.state, candidate_moves)
            self.ordered_moves_list.append((move, "ST"))

        # Empty columns for K
        if self.state.has_playable_king():
            for move in self.unordered_moves_list.tableau_to_tableau:
                if move.src_card.rank == "K" or not move.src_card.is_bottom_card(self.state):
                    continue
                self.ordered_moves_list.append((move, "TT"))
            for move in self.unordered_moves_list.tableau_to_foundation:
                if move.src_card.rank == "K" or not move.src_card.is_bottom_card(self.state):
                    continue
                self.ordered_moves_list.append((move, "TF"))

        # Expose hidden cards by moving to tableau
        candidate_moves = filter_moves(self.unordered_moves_list.tableau_to_tableau, lambda move: move.src_card.card_behind(self.state) is None and not move.src_card.is_bottom_card(self.state))
        if candidate_moves:
            move = pick_tableau_move_by_king(self.state, candidate_moves)
            self.ordered_moves_list.append((move, "TT"))

        # Expose hidden cards by moving to foundation
        candidate_moves = filter_moves(self.unordered_moves_list.tableau_to_foundation, lambda move: move.src_card.card_behind(self.state) is None and not move.src_card.is_bottom_card(self.state))
        if candidate_moves:
            move = pick_tableau_move_by_king(self.state, candidate_moves)
            self.ordered_moves_list.append((move, "TF"))

        # Play from stock to tableau
        for move in self.unordered_moves_list.stock_to_tableau:
            if (move, "ST") not in self.ordered_moves_list:
                self.ordered_moves_list.append((move, "ST"))

        # Play from tableau to foundation:
        for move in self.unordered_moves_list.tableau_to_foundation:
            if (move, "TF") not in self.ordered_moves_list:
                self.ordered_moves_list.append((move, "TF"))
        
        # Play from stock to foundation:
        for move in self.unordered_moves_list.stock_to_foundation:
            if (move, "SF") not in self.ordered_moves_list:
                self.ordered_moves_list.append((move, "SF"))

        # Play everything else
        for move in self.unordered_moves_list.tableau_to_tableau:
            if (move, "TT") not in self.ordered_moves_list:
                self.ordered_moves_list.append((move, "TT"))
        for move in self.unordered_moves_list.foundation_to_tableau:
            if (move, "FT") not in self.ordered_moves_list:
                self.ordered_moves_list.append((move, "FT"))

    def play_move(self, screen, unfound_cards):
        # Order moves if last move was not undo
        if not self.last_was_undo:
            self.order_moves()

        print("========== MOVE ORDER ==========")
        for move in self.ordered_moves_list:
            print(move)
        print()

        print("========== CHOSE MOVE ==========")
        # Check for duplicate game state
        if self.state in self.seen_states and not self.last_was_undo:
            print(f"Duplicate game state found. Undoing\n")
            previous_state, previous_ordered_moves_list = self.history.pop()
            if previous_state:
                self.state.move_undo(screen)
                self.state = previous_state
                self.ordered_moves_list = previous_ordered_moves_list[1:]
                self.last_was_undo = True
                return False

        # Add current game state to set of seen states
        self.seen_states.add(deepcopy(self.state))
        self.last_was_undo = False

        with open("states.log", "w") as f:
            for idx, state in enumerate(self.seen_states):
                f.write(f"State hash {idx}: {hash(state)}\n")
                f.write(f"State {idx}:\n{state}\n")

        # Add current game state and ordered moves list to history
        self.history.push((self.state, self.ordered_moves_list))

        # Autocomplete if available
        if not unfound_cards:
            print(f"All cards found. Autocompleting\n")
            self.state.move_autocomplete(screen)
            return True

        # Undo if out of moves
        if not self.ordered_moves_list:
            print(f"Out of moves. Undoing\n")
            previous_state, previous_ordered_moves_list = self.history.pop()
            if previous_state:
                self.state.move_undo(screen)
                self.state = previous_state
                self.ordered_moves_list = previous_ordered_moves_list[1:]
                self.last_was_undo = True
                return False

        # Play the first move
        chosen_move, move_type = self.ordered_moves_list[0]
        move_src = move_type[0]
        move_dst = move_type[1]

        if move_src == "T":
            if move_dst == "T":
                print(f"Moving {chosen_move.src_card} from tableau column {chosen_move.src_card.position.col()} to tableau column {chosen_move.dst_position.col()}\n")
                self.state.move_tableau_to_tableau(screen, chosen_move.src_card, chosen_move.dst_position, unfound_cards)
                return False
            else:
                print(f"Moving {chosen_move.src_card} from tableau to foundation {chosen_move.src_card.suit}\n")
                self.state.move_tableau_to_foundation(screen, chosen_move.src_card, unfound_cards)
                return False
        elif move_src == "S":
            if move_dst == "T":
                print(f"Moving {chosen_move.src_card} from stock to tableau column {chosen_move.dst_position.col()}\n")
                self.state.move_stock_to_tableau(screen, chosen_move.src_card, chosen_move.dst_position)
                return False
            else:
                print(f"Moving {chosen_move.src_card} from stock to foundation {chosen_move.src_card.suit}\n")
                self.state.move_stock_to_foundation(screen, chosen_move.src_card)
                return False
        else:
            print(f"Moving {chosen_move.src_card} from foundation {chosen_move.src_card.suit} to tableau column {chosen_move.dst_position.col()}\n")
            self.state.move_foundation_to_tableau(screen, chosen_move.src_card, chosen_move.dst_position)
            return False

class History:
    def __init__(self):
        self.stack = []

    def push(self, state_and_moves):
        self.stack.append(deepcopy(state_and_moves))

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None
