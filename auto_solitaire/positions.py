class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __call__(self) -> tuple[int, int]:
        return (self.x, self.y)

    def col(self) -> int:
        return round((self.x - 84) / 154)
