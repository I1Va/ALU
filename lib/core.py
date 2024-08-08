class Contact:
    def __init__(self):
        self.conductors = []
        self.value = 0

    def addConductor(self, c):
        self.conductors.append(c)


class Input(Contact):
    def update(self):
        try:
            self.value = max([c.value for c in self.conductors])
        except Exception:
            pass


class Output(Contact):
    pass


class BaseConductor:
    def __init__(self, *contacts):
        self.contacts = []
        for c in contacts:
            if isinstance(c, Output):
                self.contacts.append(c)
            else:
                c.addConductor(self)
        self.value = 0

    def update(self):
        self.value = max([c.value for c in self.contacts])


class C(BaseConductor):
    pass
