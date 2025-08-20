class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __call__(self):
        return (self.x, self.y)

    def col(self):
        return round((self.x - 84) / 154)
