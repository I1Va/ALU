class CircuitError(ValueError):
    pass


class Cell:
    def __init__(self):
        self.value = None


class Display:
    def __init__(self, n):
        self.n = n
        for i in range(self.n):
            setattr(self, f"c{i + 1}", Cell())

    def res(self):
        if self.n == 1:
            return self.c1.value
        r = []
        for i in range(self.n):
            r.append(getattr(self, f"c{i + 1}").value)
        return r

    def __str__(self):
        return ' '.join(map(str, self.res()))

    def check(self, outputs):
        return self.res() == outputs
