import constants as C

class Move:
    def __init__(self, src_position, dst_position):
        self.src_position = src_position
        self.dst_position = dst_position

class MovesList:
    def __init__(self):
        self.reset()

    def reset(self):
        self.tableau_to_tableau = []
        self.stock_to_waste = []
        self.waste_to_tableau = []
        self.waste_to_stock = []
        self.tableau_to_foundation = []
        self.waste_to_foundation = []
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
                for dst_idx, dst_col in enumerate(state.tableau):
                    dst_card = self._top_card(dst_col)
                    if state.can_build(src_card, dst_card):
                        dst_position = self._dst_position(dst_card, C.TABLEAU_POSITIONS[dst_idx])
                        self.tableau_to_tableau.append(Move(src_card.position, dst_position))

        # Stock to Waste
        if state.stock:
            self.stock_to_waste.append(Move(C.STOCK_POSITION, None))

        # Waste to Tableau
        for dst_idx, dst_col in enumerate(state.tableau):
            # Verify waste is not empty
            if not state.waste:
                break
            src_card = state.waste[-1]
            dst_card = self._top_card(dst_col)
            if state.can_build(src_card, dst_card):
                dst_position = self._dst_position(dst_card, C.TABLEAU_POSITIONS[dst_idx])
                self.waste_to_tableau.append(Move(src_card.position, dst_position))

        # Waste to Stock
        if state.waste and not state.stock:
            self.waste_to_stock.append(Move(C.WASTE_POSITION, None))

        # Tableau to Foundation
        for src_col in state.tableau:
            if not src_col:
                continue
            src_card = src_col[-1]
            dst_stack = state.foundation[src_card.suit]
            dst_card = self._top_card(dst_stack)
            if state.can_build_foundation(src_card, dst_card):
                dst_position = self._dst_position(dst_card, C.FOUNDATION_POSITIONS[src_card.suit])
                self.tableau_to_foundation.append(Move(src_card.position, dst_position))

        # Waste to Foundation
        if state.waste:
            src_card = state.waste[-1]
            dst_stack = state.foundation[src_card.suit]
            dst_card = self._top_card(dst_stack)
            if state.can_build_foundation(src_card, dst_card):
                dst_position = self._dst_position(dst_card, C.FOUNDATION_POSITIONS[src_card.suit])
                self.waste_to_foundation.append(Move(src_card.position, dst_position))

        # Foundation to Tableau
        for src_stack in state.foundation.values():
            src_card = self._top_card(src_stack)
            if not src_card:
                continue
            for dst_idx, dst_col in enumerate(state.tableau):
                dst_card = self._top_card(dst_col)
                if state.can_build(src_card, dst_card):
                    dst_position = self._dst_position(dst_card, TABLEAU_POSITIONS[dst_idx])
                    self.foundation_to_tableau.append(Move(src_card.position, dst_position))
