import constants as C
from game import Card, GameState
from positions import Position

class Move:
    def __init__(self, src_card: Card, dst_position: Position | None):
        self.src_card = src_card
        self.dst_position = dst_position

class MovesList:
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.tableau_to_tableau = []
        self.stock_to_tableau = []
        self.tableau_to_foundation = []
        self.stock_to_foundation = []
        self.foundation_to_tableau = []

    def _top_card(self, pile: list[Card]) -> Card | None:
        return pile[-1] if pile else None

    def _dst_position(self, dst_card: Card | None, fallback_position: Position) -> Position:
        return dst_card.position if dst_card else fallback_position

    def generate(self, state: GameState) -> None:
        self.reset()

        # Tableau to Tableau
        for src_col in state.tableau:
            for src_card in src_col:
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
                    self.waste_to_tableau.append(Move(src_card, dst_position))

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

        # Stock to Foundation
        if state.stock:
            dst_stack = state.foundation[src_card.suit]
            dst_card = self._top_card(dst_stack)
            for src_card in state.stock:
                if state.can_build_foundation(src_card, dst_card):
                    dst_position = self._dst_position(dst_card, C.FOUNDATION_POSITIONS[src_card.suit])
                    self.waste_to_foundation.append(Move(src_card, dst_position))

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
