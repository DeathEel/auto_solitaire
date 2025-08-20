import constants as C

class Move:
    def __init__(self, src_card, dst_position):
        self.src_card = src_card
        self.dst_position = dst_position

class MovesList:
    def __init__(self):
        self.reset()

    def reset(self):
        self.tableau_to_tableau = []
        self.stock_to_tableau = []
        self.stock_to_foundation = []
        self.tableau_to_foundation = []
        self.foundation_to_tableau = []

    def _top_card(self, pile):
        return pile[-1] if pile else None

    def _dst_position(self, dst_card, fallback_position):
        return dst_card.position if dst_card else fallback_position

    def generate(self, state):
        self.reset()

        # Tableau to Tableau
        for src_col in state.tableau:
            for src_card in src_col:
                if not src_card:
                    continue
                for dst_idx, dst_col in enumerate(state.tableau):
                    dst_card = self._top_card(dst_col)
                    if state.can_build(src_card, dst_card):
                        dst_position = self._dst_position(dst_card, C.TABLEAU_POSITIONS[dst_idx])
                        self.tableau_to_tableau.append(Move(src_card, dst_position))

        # Stock to Tableau
        for dst_idx, dst_col in enumerate(state.tableau):
            # Verify stock is not empty
            if not state.stock:
                break
            dst_card = self._top_card(dst_col)
            for src_card in state.stock:
                if state.can_build(src_card, dst_card):
                    dst_position = self._dst_position(dst_card, C.TABLEAU_POSITIONS[dst_idx])
                    self.stock_to_tableau.append(Move(src_card, dst_position))

        # Stock to Foundation
        if state.stock:
            dst_stack = state.foundation[src_card.suit]
            dst_card = self._top_card(dst_stack)
            for src_card in state.stock:
                if state.can_build_foundation(src_card, dst_card):
                    dst_position = self._dst_position(dst_card, C.FOUNDATION_POSITIONS[src_card.suit])
                    self.stock_to_foundation.append(Move(src_card, dst_position))

        # Tableau to Foundation
        for src_col in state.tableau:
            if not src_col:
                continue
            src_card = src_col[-1]
            dst_stack = state.foundation[src_card.suit]
            dst_card = self._top_card(dst_stack)
            if state.can_build_foundation(src_card, dst_card):
                dst_position = self._dst_position(dst_card, C.FOUNDATION_POSITIONS[src_card.suit])
                self.tableau_to_foundation.append(Move(src_card, dst_position))

        # Foundation to Tableau
        for src_stack in state.foundation.values():
            src_card = self._top_card(src_stack)
            if not src_card:
                continue
            for dst_idx, dst_col in enumerate(state.tableau):
                dst_card = self._top_card(dst_col)
                if state.can_build(src_card, dst_card):
                    dst_position = self._dst_position(dst_card, C.TABLEAU_POSITIONS[dst_idx])
                    self.foundation_to_tableau.append(Move(src_card, dst_position))

    def print_moves(self):
        print("Tableau to Tableau:")
        for move in self.tableau_to_tableau:
            print(f"\t{move}")
        print("Stock to Tableau:")
        for move in self.stock_to_tableau:
            print(f"\t{move}")
        print("Stock to Foundation:")
        for move in self.stock_to_foundation:
            print(f"\t{move}")
        print("Tableau to Foundation:")
        for move in self.tableau_to_foundation:
            print(f"\t{move}")
        print("Foundation to Tableau:")
        for move in self.foundation_to_tableau:
            print(f"\t{move}")
