from lib.core import C, Input, Output
from lib.utils import CircuitError


class Circuit:
    ELEMENTS = {}

    def __init__(self, **kwargs):
        self._init = kwargs
        self._elements = []
        for elem, names in self.ELEMENTS.items():
            for n in names:
                e = elem()
                self._elements.append(e)
                setattr(self, n, e)
        self._input_names = []
        for name, contact in self.inout().items():
            if not (name.startswith('in') or name.startswith('out')):
                raise CircuitError("Bad contacts name")
            if contact:
                setattr(self, name, contact)
            elif name.startswith("in"):
                setattr(self, name, Input())
                self._input_names.append(name)
            else:
                setattr(self, name, Output())
        self._conductors = []
        for c in self.connect():
            self._conductors.append(C(*c))

    def inout(self):
        return {}

    def connect(self):
        return ()

    def update(self):
        for n, value in self._init.items():
            c = getattr(self, n)
            if n.startswith('in'):
                c.value = value
            else:
                value.value = c.value
        for g in self._elements:
            g.update()
        for c in self._conductors:
            c.update()
        for n in self._input_names:
            getattr(self, n).update()

    def run(self, n=100):
        for _ in range(n):
            self.update()


class Bridge(Circuit):
    def inout(self):
        return {
            "in1": None,
            "out1": None
        }

    def update(self):
        super().update()
        self.out1.value = self.in1.value


class NOT(Circuit):
    def inout(self):
        return {
            "in1": None,
            "out1": None
        }

    def update(self):
        super().update()
        self.out1.value = int(not self.in1.value)


class AND(Circuit):
    def inout(self):
        return {
            "in1": None,
            "in2": None,
            "out1": None
        }

    def update(self):
        super().update()
        self.out1.value = int(self.in1.value and self.in2.value)


class OR(Circuit):
    def inout(self):
        return {
            "in1": None,
            "in2": None,
            "out1": None
        }

    def update(self):
        super().update()
        self.out1.value = int(self.in1.value or self.in2.value)


class NOR(Circuit):
    ELEMENTS = {
        OR: ("o1",),
        NOT: ("n1",)
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in2": self.o1.in2,
            "out1": self.n1.out1
        }

    def connect(self):
        return (
            (self.o1.out1, self.n1.in1),
        )


class NAND(Circuit):
    ELEMENTS = {
        AND: ("o1",),
        NOT: ("n1",)
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in2": self.o1.in2,
            "out1": self.n1.out1
        }

    def connect(self):
        return (
            (self.o1.out1, self.n1.in1),
        )


class XOR(Circuit):
    ELEMENTS = {
        NAND: ("na1",),
        OR: ("o1",),
        AND: ("a1",),
        Bridge: ("b1", "b2",)
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.na1.in1),
            (self.b1.out1, self.o1.in2),
            (self.b2.out1, self.na1.in2),
            (self.b2.out1, self.o1.in1),
            (self.na1.out1, self.a1.in1),
            (self.o1.out1, self.a1.in2),
        )


class AND3(Circuit):
    ELEMENTS = {
        AND: ("a1", "a2",)
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a2.in1,
            "in3": self.a2.in2,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.a2.out1, self.a1.in2),
        )


class OR3(Circuit):
    ELEMENTS = {
        OR: ("o1", "o2",)
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in2": self.o1.in2,
            "in3": self.o2.in2,
            "out1": self.o2.out1
        }

    def connect(self):
        return (
            (self.o1.out1, self.o2.in1),
        )


class NOT3(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2", "n3",),
        AND3: ("a3",)
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.n2.in1,
            "in3": self.n3.in1,
            "out1": self.a3.out1
        }

    def connect(self):
        return (
            (self.n1.out1, self.a3.in1),
            (self.n2.out1, self.a3.in2),
            (self.n3.out1, self.a3.in3),
        )


class XNOR(Circuit):
    ELEMENTS = {
        AND: ("a1",),
        NOR: ("n1",),
        OR: ("o1",),
        Bridge: ("b1", "b2",),
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "out1": self.o1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.a1.in1),
            (self.b2.out1, self.a1.in2),
            (self.a1.out1, self.o1.in2),
            (self.b2.out1, self.n1.in2),
            (self.b1.out1, self.n1.in1),
            (self.n1.out1, self.o1.in1),
        )


class TOF(Circuit):
    ELEMENTS = {
        AND: ("a1",),
        NOT: ("n1",),
        AND3: ("a3",)
    }

    def inout(self):
        return {
            "in1": self.a3.in1,
            "in2": self.a3.in2,
            "in3": self.a3.in3,
            "in4": self.n1.in1,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.a3.out1, self.a1.in1),
            (self.n1.out1, self.a1.in2),
        )


class OOF(Circuit):
    ELEMENTS = {
        NOT3: ("n3",),
        AND: ("a1",)
    }

    def inout(self):
        return {
            "in1": self.n3.in1,
            "in2": self.n3.in2,
            "in3": self.n3.in3,
            "in4": self.a1.in2,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.n3.out1, self.a1.in1),
        )


class NOOF(Circuit):
    ELEMENTS = {
        OOF: ("oo1",),
        NOT: ("n1",)
    }

    def inout(self):
        return {
            "in1": self.oo1.in1,
            "in2": self.oo1.in2,
            "in3": self.oo1.in3,
            "in4": self.oo1.in4,
            "out1": self.n1.out1

        }

    def connect(self):
        return (
            (self.oo1.out1, self.n1.in1),
        )


class AND4(Circuit):
    ELEMENTS = {
        AND3: ("a3",),
        AND: ("a1",)
    }

    def inout(self):
        return {
            "in1": self.a3.in1,
            "in2": self.a3.in2,
            "in3": self.a3.in3,
            "in4": self.a1.in2,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.a3.out1, self.a1.in1),
        )


class OR4(Circuit):
    ELEMENTS = {
        OR3: ("o3",),
        OR: ("o1",)
    }

    def inout(self):
        return {
            "in1": self.o3.in1,
            "in2": self.o3.in2,
            "in3": self.o3.in3,
            "in4": self.o1.in2,
            "out1": self.o1.out1
        }

    def connect(self):
        return (
            (self.o3.out1, self.o1.in1),
        )


class MT1(Circuit):
    ELEMENTS = {
        NOOF: ("no1", "no2", "no3", "no4"),
        OR4: ("o4",),
        AND4: ("a4",),
        AND: ("a1",),
        Bridge: ("b1", "b2", "b3", "b4")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "in4": self.b4.in1,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.no1.in1),
            (self.b2.out1, self.no1.in2),
            (self.b3.out1, self.no1.in3),
            (self.b4.out1, self.no1.in4),

            (self.b1.out1, self.no2.in1),
            (self.b3.out1, self.no2.in2),
            (self.b4.out1, self.no2.in3),
            (self.b2.out1, self.no2.in4),

            (self.b1.out1, self.no3.in1),
            (self.b2.out1, self.no3.in2),
            (self.b4.out1, self.no3.in3),
            (self.b3.out1, self.no3.in4),

            (self.b3.out1, self.no4.in1),
            (self.b2.out1, self.no4.in2),
            (self.b4.out1, self.no4.in3),
            (self.b1.out1, self.no4.in4),

            (self.no1.out1, self.a4.in1),
            (self.no2.out1, self.a4.in2),
            (self.no3.out1, self.a4.in3),
            (self.no4.out1, self.a4.in4),

            (self.b1.out1, self.o4.in1),
            (self.b2.out1, self.o4.in2),
            (self.b3.out1, self.o4.in3),
            (self.b4.out1, self.o4.in4),

            (self.a4.out1, self.a1.in1),
            (self.o4.out1, self.a1.in2)
        )


class NOT2(Circuit):
    ELEMENTS = {
        OR: ("o1",),
        NOT: ("n1",)
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in2": self.o1.in2,
            "out1": self.n1.out1
        }

    def connect(self):
        return (
            (self.o1.out1, self.n1.in1),
        )


class OOT(Circuit):
    ELEMENTS = {
        AND: ("a1",),
        NOT2: ("n2",)
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.n2.in1,
            "in3": self.n2.in2,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.n2.out1, self.a1.in2),
        )


class TOT(Circuit):
    ELEMENTS = {
        AND: ("a1", "a2"),
        NOT: ("n1",)
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a1.in2,
            "in3": self.n1.in1,
            "out1": self.a2.out1
        }

    def connect(self):
        return (
            (self.n1.out1, self.a2.in2),
            (self.a1.out1, self.a2.in1)
        )


class SC(Circuit):
    ELEMENTS = {
        Bridge: ("b1", "b2", "b3"),
        AND3: ("a3",),
        OR3: ("o1", "o2"),
        NOT3: ("n3",),
        OOT: ("oot1", "oot2", "oot3"),
        TOT: ("tot1", "tot2", "tot3")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "out1": self.n3.out1,
            "out2": self.o1.out1,
            "out3": self.o2.out1,
            "out4": self.a3.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.n3.in1),
            (self.b2.out1, self.n3.in2),
            (self.b3.out1, self.n3.in3),


            (self.b1.out1, self.a3.in1),
            (self.b2.out1, self.a3.in2),
            (self.b3.out1, self.a3.in3),


            (self.b1.out1, self.oot1.in1),
            (self.b2.out1, self.oot1.in2),
            (self.b3.out1, self.oot1.in3),

            (self.b2.out1, self.oot2.in1),
            (self.b1.out1, self.oot2.in2),
            (self.b3.out1, self.oot2.in3),

            (self.b3.out1, self.oot3.in1),
            (self.b1.out1, self.oot3.in2),
            (self.b2.out1, self.oot3.in3),

            (self.oot1.out1, self.o1.in1),
            (self.oot2.out1, self.o1.in2),
            (self.oot3.out1, self.o1.in3),


            (self.b1.out1, self.tot1.in1),
            (self.b2.out1, self.tot1.in2),
            (self.b3.out1, self.tot1.in3),

            (self.b1.out1, self.tot2.in1),
            (self.b3.out1, self.tot2.in2),
            (self.b2.out1, self.tot2.in3),

            (self.b2.out1, self.tot3.in1),
            (self.b3.out1, self.tot3.in2),
            (self.b1.out1, self.tot3.in3),

            (self.tot1.out1, self.o2.in1),
            (self.tot2.out1, self.o2.in2),
            (self.tot3.out1, self.o2.in3),
        )


class ONAND(Circuit):
    ELEMENTS = {
        NAND: ("N1",),
        OR: ("o1",),
        AND: ("a1",),
        Bridge: ("b1", "b2")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.o1.in1),
            (self.b1.out1, self.N1.in1),
            (self.b2.out1, self.o1.in2),
            (self.b2.out1, self.N1.in2),
            (self.o1.out1, self.a1.in1),
            (self.N1.out1, self.a1.in2),
        )


class HADD(Circuit):
    ELEMENTS = {
        ONAND: ("O1",),
        AND: ("a1",),
        Bridge: ("b1", "b2")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "out1": self.O1.out1,
            "out2": self.a1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.a1.in1),
            (self.b1.out1, self.O1.in1),
            (self.b2.out1, self.a1.in2),
            (self.b2.out1, self.O1.in2),
        )


class UP_TOT(Circuit):
    ELEMENTS = {
        Bridge: ("b1", "b2", "b3"),
        TOT: ("tot1", "tot2", "tot3"),
        OR3: ("o1",)
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "out1": self.o1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.tot1.in1),
            (self.b2.out1, self.tot1.in2),
            (self.b3.out1, self.tot1.in3),
            (self.tot1.out1, self.o1.in1),

            (self.b1.out1, self.tot2.in1),
            (self.b3.out1, self.tot2.in2),
            (self.b2.out1, self.tot2.in3),
            (self.tot2.out1, self.o1.in2),

            (self.b3.out1, self.tot3.in1),
            (self.b2.out1, self.tot3.in2),
            (self.b1.out1, self.tot3.in3),
            (self.tot3.out1, self.o1.in3),
        )


class UP_OOT(Circuit):
    ELEMENTS = {
        Bridge: ("b1", "b2", "b3"),
        OOT: ("oot1", "oot2", "oot3"),
        OR3: ("o1",)
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "out1": self.o1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.oot1.in1),
            (self.b2.out1, self.oot1.in2),
            (self.b3.out1, self.oot1.in3),
            (self.oot1.out1, self.o1.in1),

            (self.b2.out1, self.oot2.in1),
            (self.b1.out1, self.oot2.in2),
            (self.b3.out1, self.oot2.in3),
            (self.oot2.out1, self.o1.in2),

            (self.b3.out1, self.oot3.in1),
            (self.b2.out1, self.oot3.in2),
            (self.b1.out1, self.oot3.in3),
            (self.oot3.out1, self.o1.in3),
        )


class ADD(Circuit):
    ELEMENTS = {
        AND3: ("a3_1", "a3_2"),
        UP_OOT: ("uoot1",),
        OR: ("o1", "o2"),
        UP_TOT: ("utot1", "utot2"),
        NOT: ("n1",),
        AND: ("a1",),
        Bridge: ("b1", "b2", "b3")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "out1": self.a1.out1,
            "out2": self.o2.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.a3_1.in1),
            (self.b2.out1, self.a3_1.in2),
            (self.b3.out1, self.a3_1.in3),
            (self.a3_1.out1, self.o1.in1),

            (self.b1.out1, self.uoot1.in1),
            (self.b2.out1, self.uoot1.in2),
            (self.b3.out1, self.uoot1.in3),
            (self.uoot1.out1, self.o1.in2),

            (self.o1.out1, self.a1.in1),

            (self.b1.out1, self.utot1.in1),
            (self.b2.out1, self.utot1.in2),
            (self.b3.out1, self.utot1.in3),
            (self.utot1.out1, self.n1.in1),

            (self.n1.out1, self.a1.in2),


            (self.b1.out1, self.utot2.in1),
            (self.b2.out1, self.utot2.in2),
            (self.b3.out1, self.utot2.in3),
            (self.utot2.out1, self.o2.in1),

            (self.b1.out1, self.a3_2.in1),
            (self.b2.out1, self.a3_2.in2),
            (self.b3.out1, self.a3_2.in3),
            (self.a3_2.out1, self.o2.in2)
        )


class NOT8(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8")
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.n2.in1,
            "in3": self.n3.in1,
            "in4": self.n4.in1,
            "in5": self.n5.in1,
            "in6": self.n6.in1,
            "in7": self.n7.in1,
            "in8": self.n8.in1,

            "out1": self.n1.out1,
            "out2": self.n2.out1,
            "out3": self.n3.out1,
            "out4": self.n4.out1,
            "out5": self.n5.out1,
            "out6": self.n6.out1,
            "out7": self.n7.out1,
            "out8": self.n8.out1,
        }


class OR8_s(Circuit):
    ELEMENTS = {
        OR3: ("O3_1", "O3_2", "O3_3"),
        OR: ("o1",)
    }

    def inout(self):
        return {
            "in1": self.O3_1.in1,
            "in2": self.O3_1.in2,
            "in3": self.O3_1.in3,
            "in4": self.O3_2.in1,
            "in5": self.O3_2.in2,
            "in6": self.O3_2.in3,
            "in7": self.o1.in1,
            "in8": self.o1.in2,
            "out1": self.O3_3.out1
        }

    def connect(self):
        return (
            (self.O3_1.out1, self.O3_3.in1),
            (self.O3_2.out1, self.O3_3.in2),
            (self.o1.out1, self.O3_3.in3),
        )


class ODD(Circuit):
    ELEMENTS = {
        TOF: ("t1", "t2", "t3", "t4"),
        OOF: ("oo1", "oo2", "oo3", "oo4"),
        Bridge: ("b1", "b2", "b3", "b4"),
        OR8_s: ("o8",)
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "in4": self.b4.in1,
            "out1": self.o8.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.t1.in1),
            (self.b2.out1, self.t1.in2),
            (self.b3.out1, self.t1.in3),
            (self.b4.out1, self.t1.in4),
            (self.b1.out1, self.t2.in1),
            (self.b3.out1, self.t2.in2),
            (self.b4.out1, self.t2.in3),
            (self.b2.out1, self.t2.in4),
            (self.b1.out1, self.t3.in1),
            (self.b2.out1, self.t3.in2),
            (self.b4.out1, self.t3.in3),
            (self.b3.out1, self.t3.in4),
            (self.b3.out1, self.t4.in1),
            (self.b2.out1, self.t4.in2),
            (self.b4.out1, self.t4.in3),
            (self.b1.out1, self.t4.in4),
            (self.b1.out1, self.oo1.in1),
            (self.b2.out1, self.oo1.in2),
            (self.b3.out1, self.oo1.in3),
            (self.b4.out1, self.oo1.in4),
            (self.b1.out1, self.oo2.in1),
            (self.b3.out1, self.oo2.in2),
            (self.b4.out1, self.oo2.in3),
            (self.b2.out1, self.oo2.in4),
            (self.b1.out1, self.oo3.in1),
            (self.b2.out1, self.oo3.in2),
            (self.b4.out1, self.oo3.in3),
            (self.b3.out1, self.oo3.in4),
            (self.b3.out1, self.oo4.in1),
            (self.b2.out1, self.oo4.in2),
            (self.b4.out1, self.oo4.in3),
            (self.b1.out1, self.oo4.in4),
            (self.t1.out1, self.o8.in1),
            (self.t2.out1, self.o8.in2),
            (self.t3.out1, self.o8.in3),
            (self.t4.out1, self.o8.in4),
            (self.oo1.out1, self.o8.in5),
            (self.oo2.out1, self.o8.in6),
            (self.oo3.out1, self.o8.in7),
            (self.oo4.out1, self.o8.in8),
        )


class AND8_s(Circuit):
    ELEMENTS = {
        AND4: ("a4_1", "a4_2"),
        AND: ("a1",)
    }

    def inout(self):
        return {
            "in1": self.a4_1.in1,
            "in2": self.a4_1.in2,
            "in3": self.a4_1.in3,
            "in4": self.a4_1.in4,
            "in5": self.a4_2.in1,
            "in6": self.a4_2.in2,
            "in7": self.a4_2.in3,
            "in8": self.a4_2.in4,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.a4_1.out1, self.a1.in1),
            (self.a4_2.out1, self.a1.in2),
        )


class AND8(Circuit):
    ELEMENTS = {
        AND: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8")
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in9": self.o1.in2,
            "out1": self.o1.out1,

            "in2": self.o2.in1,
            "in10": self.o2.in2,
            "out2": self.o2.out1,

            "in3": self.o3.in1,
            "in11": self.o3.in2,
            "out3": self.o3.out1,

            "in4": self.o4.in1,
            "in12": self.o4.in2,
            "out4": self.o4.out1,

            "in5": self.o5.in1,
            "in13": self.o5.in2,
            "out5": self.o5.out1,

            "in6": self.o6.in1,
            "in14": self.o6.in2,
            "out6": self.o6.out1,

            "in7": self.o7.in1,
            "in15": self.o7.in2,
            "out7": self.o7.out1,

            "in8": self.o8.in1,
            "in16": self.o8.in2,
            "out8": self.o8.out1,
        }


class EQ(Circuit):
    ELEMENTS = {
        XOR: ("x1",),
        NOT: ("n1",)
    }

    def inout(self):
        return {
            "in1": self.x1.in1,
            "in2": self.x1.in2,
            "out1": self.n1.out1
        }

    def connect(self):
        return (
            (self.x1.out1, self.n1.in1),
        )


class EQ8(Circuit):
    ELEMENTS = {
        AND8_s: ("a1",),
        EQ: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8")
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in9": self.o1.in2,

            "in2": self.o2.in1,
            "in10": self.o2.in2,

            "in3": self.o3.in1,
            "in11": self.o3.in2,

            "in4": self.o4.in1,
            "in12": self.o4.in2,

            "in5": self.o5.in1,
            "in13": self.o5.in2,

            "in6": self.o6.in1,
            "in14": self.o6.in2,

            "in7": self.o7.in1,
            "in15": self.o7.in2,

            "in8": self.o8.in1,
            "in16": self.o8.in2,

            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.o1.out1, self.a1.in1),
            (self.o2.out1, self.a1.in2),
            (self.o3.out1, self.a1.in3),
            (self.o4.out1, self.a1.in4),
            (self.o5.out1, self.a1.in5),
            (self.o6.out1, self.a1.in6),
            (self.o7.out1, self.a1.in7),
            (self.o8.out1, self.a1.in8),
        )


class OR8(Circuit):
    ELEMENTS = {
        OR: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8")
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in9": self.o1.in2,
            "out1": self.o1.out1,

            "in2": self.o2.in1,
            "in10": self.o2.in2,
            "out2": self.o2.out1,

            "in3": self.o3.in1,
            "in11": self.o3.in2,
            "out3": self.o3.out1,

            "in4": self.o4.in1,
            "in12": self.o4.in2,
            "out4": self.o4.out1,

            "in5": self.o5.in1,
            "in13": self.o5.in2,
            "out5": self.o5.out1,

            "in6": self.o6.in1,
            "in14": self.o6.in2,
            "out6": self.o6.out1,

            "in7": self.o7.in1,
            "in15": self.o7.in2,
            "out7": self.o7.out1,

            "in8": self.o8.in1,
            "in16": self.o8.in2,
            "out8": self.o8.out1,
        }


class NEQ8(Circuit):
    ELEMENTS = {
        AND8_s: ("a1",),
        EQ: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"),
        NOT: ("n1",)
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in9": self.o1.in2,

            "in2": self.o2.in1,
            "in10": self.o2.in2,

            "in3": self.o3.in1,
            "in11": self.o3.in2,

            "in4": self.o4.in1,
            "in12": self.o4.in2,

            "in5": self.o5.in1,
            "in13": self.o5.in2,

            "in6": self.o6.in1,
            "in14": self.o6.in2,

            "in7": self.o7.in1,
            "in15": self.o7.in2,

            "in8": self.o8.in1,
            "in16": self.o8.in2,

            "out1": self.n1.out1
        }

    def connect(self):
        return (
            (self.o1.out1, self.a1.in1),
            (self.o2.out1, self.a1.in2),
            (self.o3.out1, self.a1.in3),
            (self.o4.out1, self.a1.in4),
            (self.o5.out1, self.a1.in5),
            (self.o6.out1, self.a1.in6),
            (self.o7.out1, self.a1.in7),
            (self.o8.out1, self.a1.in8),
            (self.a1.out1, self.n1.in1),
        )


class AANB(Circuit):
    ELEMENTS = {
        NOT: ("n1",),
        AND: ("a1",)
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.n1.in1,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.n1.out1, self.a1.in2),
        )


class AONB(Circuit):
    ELEMENTS = {
        NOT: ("n1",),
        OR: ("a1",)
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.n1.in1,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.n1.out1, self.a1.in2),
        )


class SEG(Circuit):
    ELEMENTS = {
        AONB: ("A1",),
        AANB: ("a1",),
        OR: ("o1", "o2"),
        Bridge: ("b1", "b2", "b3")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "out1": self.o1.out1,
            "out2": self.o2.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.A1.in1),
            (self.b1.out1, self.a1.in1),
            (self.b2.out1, self.A1.in2),
            (self.b2.out1, self.a1.in2),

            (self.A1.out1, self.o1.in1),
            (self.b3.out1, self.o1.in2),
            (self.a1.out1, self.o2.in1),
            (self.b3.out1, self.o2.in2),
        )


class GT8(Circuit):
    ELEMENTS = {
        Bridge: ('B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16'),
        AND8_s: ('AND8',),
        NEQ8: ('NEQ',),
        AND: ('AND',),
        SEG: ('s1', 's2', 's3', 's4', 's5', 's6', 's7'),
        AONB: ("A1",),
        AANB: ("a1",)
    }

    def inout(self):
        return {
            "in1": self.B1.in1,
            "in9": self.B9.in1,
            "in2": self.B2.in1,
            "in10": self.B10.in1,
            "in3": self.B3.in1,
            "in11": self.B11.in1,
            "in4": self.B4.in1,
            "in12": self.B12.in1,
            "in5": self.B5.in1,
            "in13": self.B13.in1,
            "in6": self.B6.in1,
            "in14": self.B14.in1,
            "in7": self.B7.in1,
            "in15": self.B15.in1,
            "in8": self.B8.in1,
            "in16": self.B16.in1,
            "out1": self.AND.out1
        }

    def connect(self):
        return (
            (self.B1.out1, self.NEQ.in1),
            (self.B2.out1, self.NEQ.in2),
            (self.B3.out1, self.NEQ.in3),
            (self.B4.out1, self.NEQ.in4),
            (self.B5.out1, self.NEQ.in5),
            (self.B6.out1, self.NEQ.in6),
            (self.B7.out1, self.NEQ.in7),
            (self.B8.out1, self.NEQ.in8),
            (self.B9.out1, self.NEQ.in9),
            (self.B10.out1, self.NEQ.in10),
            (self.B11.out1, self.NEQ.in11),
            (self.B12.out1, self.NEQ.in12),
            (self.B13.out1, self.NEQ.in13),
            (self.B14.out1, self.NEQ.in14),
            (self.B15.out1, self.NEQ.in15),
            (self.B16.out1, self.NEQ.in16),
            (self.NEQ.out1, self.AND.in1),


            (self.B1.out1, self.A1.in1),
            (self.B1.out1, self.a1.in1),
            (self.B9.out1, self.A1.in2),
            (self.B9.out1, self.a1.in2),
            (self.A1.out1, self.AND8.in1),
            (self.a1.out1, self.s1.in3),

            (self.B2.out1, self.s1.in1),
            (self.B10.out1, self.s1.in2),
            (self.s1.out1, self.AND8.in2),
            (self.s1.out2, self.s2.in3),

            (self.B3.out1, self.s2.in1),
            (self.B11.out1, self.s2.in2),
            (self.s2.out1, self.AND8.in3),
            (self.s2.out2, self.s3.in3),

            (self.B4.out1, self.s3.in1),
            (self.B12.out1, self.s3.in2),
            (self.s3.out1, self.AND8.in4),
            (self.s3.out2, self.s4.in3),

            (self.B5.out1, self.s4.in1),
            (self.B13.out1, self.s4.in2),
            (self.s4.out1, self.AND8.in5),
            (self.s4.out2, self.s5.in3),

            (self.B6.out1, self.s5.in1),
            (self.B14.out1, self.s5.in2),
            (self.s5.out1, self.AND8.in6),
            (self.s5.out2, self.s6.in3),

            (self.B7.out1, self.s6.in1),
            (self.B15.out1, self.s6.in2),
            (self.s6.out1, self.AND8.in7),
            (self.s6.out2, self.s7.in3),

            (self.B8.out1, self.s7.in1),
            (self.B16.out1, self.s7.in2),
            (self.s7.out1, self.AND8.in8),


            (self.AND8.out1, self.AND.in2),

        )


class LT8(Circuit):
    ELEMENTS = {
        GT8: ("GT8",),
        NEQ8: ("NEQ",),
        AND: ("AND",),
        NOT: ("n1",),
        Bridge: ('B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16'),
    }

    def inout(self):
        return {
            "in1": self.B1.in1,
            "in9": self.B9.in1,
            "in2": self.B2.in1,
            "in10": self.B10.in1,
            "in3": self.B3.in1,
            "in11": self.B11.in1,
            "in4": self.B4.in1,
            "in12": self.B12.in1,
            "in5": self.B5.in1,
            "in13": self.B13.in1,
            "in6": self.B6.in1,
            "in14": self.B14.in1,
            "in7": self.B7.in1,
            "in15": self.B15.in1,
            "in8": self.B8.in1,
            "in16": self.B16.in1,
            "out1": self.AND.out1
        }

    def connect(self):
        return (
            (self.B1.out1, self.NEQ.in1),
            (self.B2.out1, self.NEQ.in2),
            (self.B3.out1, self.NEQ.in3),
            (self.B4.out1, self.NEQ.in4),
            (self.B5.out1, self.NEQ.in5),
            (self.B6.out1, self.NEQ.in6),
            (self.B7.out1, self.NEQ.in7),
            (self.B8.out1, self.NEQ.in8),
            (self.B9.out1, self.NEQ.in9),
            (self.B10.out1, self.NEQ.in10),
            (self.B11.out1, self.NEQ.in11),
            (self.B12.out1, self.NEQ.in12),
            (self.B13.out1, self.NEQ.in13),
            (self.B14.out1, self.NEQ.in14),
            (self.B15.out1, self.NEQ.in15),
            (self.B16.out1, self.NEQ.in16),
            (self.NEQ.out1, self.AND.in1),

            (self.B1.out1, self.GT8.in1),
            (self.B2.out1, self.GT8.in2),
            (self.B3.out1, self.GT8.in3),
            (self.B4.out1, self.GT8.in4),
            (self.B5.out1, self.GT8.in5),
            (self.B6.out1, self.GT8.in6),
            (self.B7.out1, self.GT8.in7),
            (self.B8.out1, self.GT8.in8),
            (self.B9.out1, self.GT8.in9),
            (self.B10.out1, self.GT8.in10),
            (self.B11.out1, self.GT8.in11),
            (self.B12.out1, self.GT8.in12),
            (self.B13.out1, self.GT8.in13),
            (self.B14.out1, self.GT8.in14),
            (self.B15.out1, self.GT8.in15),
            (self.B16.out1, self.GT8.in16),
            (self.GT8.out1, self.n1.in1),

            (self.n1.out1, self.AND.in2),

        )


class GTE8(Circuit):
    ELEMENTS = {
        GT8: ("GT8",),
        EQ8: ("EQ",),
        OR: ("O1",),
        Bridge: ('B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16'),
    }

    def inout(self):
        return {
            "in1": self.B1.in1,
            "in9": self.B9.in1,
            "in2": self.B2.in1,
            "in10": self.B10.in1,
            "in3": self.B3.in1,
            "in11": self.B11.in1,
            "in4": self.B4.in1,
            "in12": self.B12.in1,
            "in5": self.B5.in1,
            "in13": self.B13.in1,
            "in6": self.B6.in1,
            "in14": self.B14.in1,
            "in7": self.B7.in1,
            "in15": self.B15.in1,
            "in8": self.B8.in1,
            "in16": self.B16.in1,
            "out1": self.O1.out1
        }

    def connect(self):
        return (
            (self.B1.out1, self.EQ.in1),
            (self.B2.out1, self.EQ.in2),
            (self.B3.out1, self.EQ.in3),
            (self.B4.out1, self.EQ.in4),
            (self.B5.out1, self.EQ.in5),
            (self.B6.out1, self.EQ.in6),
            (self.B7.out1, self.EQ.in7),
            (self.B8.out1, self.EQ.in8),
            (self.B9.out1, self.EQ.in9),
            (self.B10.out1, self.EQ.in10),
            (self.B11.out1, self.EQ.in11),
            (self.B12.out1, self.EQ.in12),
            (self.B13.out1, self.EQ.in13),
            (self.B14.out1, self.EQ.in14),
            (self.B15.out1, self.EQ.in15),
            (self.B16.out1, self.EQ.in16),
            (self.EQ.out1, self.O1.in1),

            (self.B1.out1, self.GT8.in1),
            (self.B2.out1, self.GT8.in2),
            (self.B3.out1, self.GT8.in3),
            (self.B4.out1, self.GT8.in4),
            (self.B5.out1, self.GT8.in5),
            (self.B6.out1, self.GT8.in6),
            (self.B7.out1, self.GT8.in7),
            (self.B8.out1, self.GT8.in8),
            (self.B9.out1, self.GT8.in9),
            (self.B10.out1, self.GT8.in10),
            (self.B11.out1, self.GT8.in11),
            (self.B12.out1, self.GT8.in12),
            (self.B13.out1, self.GT8.in13),
            (self.B14.out1, self.GT8.in14),
            (self.B15.out1, self.GT8.in15),
            (self.B16.out1, self.GT8.in16),
            (self.GT8.out1, self.O1.in2),
        )


class LTE8(Circuit):
    ELEMENTS = {
        GT8: ("GT8",),
        NOT: ("n1",),
        Bridge: ('B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16'),
    }

    def inout(self):
        return {
            "in1": self.B1.in1,
            "in9": self.B9.in1,
            "in2": self.B2.in1,
            "in10": self.B10.in1,
            "in3": self.B3.in1,
            "in11": self.B11.in1,
            "in4": self.B4.in1,
            "in12": self.B12.in1,
            "in5": self.B5.in1,
            "in13": self.B13.in1,
            "in6": self.B6.in1,
            "in14": self.B14.in1,
            "in7": self.B7.in1,
            "in15": self.B15.in1,
            "in8": self.B8.in1,
            "in16": self.B16.in1,
            "out1": self.n1.out1
        }

    def connect(self):
        return (
            (self.B1.out1, self.GT8.in1),
            (self.B2.out1, self.GT8.in2),
            (self.B3.out1, self.GT8.in3),
            (self.B4.out1, self.GT8.in4),
            (self.B5.out1, self.GT8.in5),
            (self.B6.out1, self.GT8.in6),
            (self.B7.out1, self.GT8.in7),
            (self.B8.out1, self.GT8.in8),
            (self.B9.out1, self.GT8.in9),
            (self.B10.out1, self.GT8.in10),
            (self.B11.out1, self.GT8.in11),
            (self.B12.out1, self.GT8.in12),
            (self.B13.out1, self.GT8.in13),
            (self.B14.out1, self.GT8.in14),
            (self.B15.out1, self.GT8.in15),
            (self.B16.out1, self.GT8.in16),
            (self.GT8.out1, self.n1.in1),

        )


class ADD8(Circuit):
    ELEMENTS = {
        ADD: ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"),
    }

    def inout(self):
        return {
            "in8": self.A8.in1,
            "in16": self.A8.in2,
            "out1": self.A8.out1,

            "in7": self.A7.in1,
            "in15": self.A7.in2,
            "out2": self.A7.out1,

            "in6": self.A6.in1,
            "in14": self.A6.in2,
            "out3": self.A6.out1,

            "in5": self.A5.in1,
            "in13": self.A5.in2,
            "out4": self.A5.out1,

            "in4": self.A4.in1,
            "in12": self.A4.in2,
            "out5": self.A4.out1,

            "in3": self.A3.in1,
            "in11": self.A3.in2,
            "out6": self.A3.out1,

            "in2": self.A2.in1,
            "in10": self.A2.in2,
            "out7": self.A2.out1,

            "in1": self.A1.in1,
            "in9": self.A1.in2,
            "out8": self.A1.out1,

            "out9": self.A1.out2

        }

    def connect(self):
        return (
            (self.A8.out2, self.A7.in3),
            (self.A7.out2, self.A6.in3),
            (self.A6.out2, self.A5.in3),
            (self.A5.out2, self.A4.in3),
            (self.A4.out2, self.A3.in3),
            (self.A3.out2, self.A2.in3),
            (self.A2.out2, self.A1.in3),
        )


class OR9(Circuit):
    ELEMENTS = {
        OR: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8", "o9")
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in10": self.o1.in2,
            "out1": self.o1.out1,

            "in2": self.o2.in1,
            "in11": self.o2.in2,
            "out2": self.o2.out1,

            "in3": self.o3.in1,
            "in12": self.o3.in2,
            "out3": self.o3.out1,

            "in4": self.o4.in1,
            "in13": self.o4.in2,
            "out4": self.o4.out1,

            "in5": self.o5.in1,
            "in14": self.o5.in2,
            "out5": self.o5.out1,

            "in6": self.o6.in1,
            "in15": self.o6.in2,
            "out6": self.o6.out1,

            "in7": self.o7.in1,
            "in16": self.o7.in2,
            "out7": self.o7.out1,

            "in8": self.o8.in1,
            "in17": self.o8.in2,
            "out8": self.o8.out1,

            "in9": self.o9.in1,
            "in18": self.o9.in2,
            "out9": self.o9.out1
        }


class AND9(Circuit):
    ELEMENTS = {
        AND: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8", "o9")
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in10": self.o1.in2,
            "out1": self.o1.out1,

            "in2": self.o2.in1,
            "in11": self.o2.in2,
            "out2": self.o2.out1,

            "in3": self.o3.in1,
            "in12": self.o3.in2,
            "out3": self.o3.out1,

            "in4": self.o4.in1,
            "in13": self.o4.in2,
            "out4": self.o4.out1,

            "in5": self.o5.in1,
            "in14": self.o5.in2,
            "out5": self.o5.out1,

            "in6": self.o6.in1,
            "in15": self.o6.in2,
            "out6": self.o6.out1,

            "in7": self.o7.in1,
            "in16": self.o7.in2,
            "out7": self.o7.out1,

            "in8": self.o8.in1,
            "in17": self.o8.in2,
            "out8": self.o8.out1,

            "in9": self.o9.in1,
            "in18": self.o9.in2,
            "out9": self.o9.out1
        }


class OR10_s(Circuit):
    ELEMENTS = {
        OR9: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8", "o9")
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in2": self.o1.in2,
            "in3": self.o1.in3,
            "in4": self.o1.in4,
            "in5": self.o1.in5,
            "in6": self.o1.in6,
            "in7": self.o1.in7,
            "in8": self.o1.in8,
            "in9": self.o1.in9,
            "in10": self.o1.in10,
            "in11": self.o1.in11,
            "in12": self.o1.in12,
            "in13": self.o1.in13,
            "in14": self.o1.in14,
            "in15": self.o1.in15,
            "in16": self.o1.in16,
            "in17": self.o1.in17,
            "in18": self.o1.in18,
            "in19": self.o2.in1,
            "in20": self.o2.in2,
            "in21": self.o2.in3,
            "in22": self.o2.in4,
            "in23": self.o2.in5,
            "in24": self.o2.in6,
            "in25": self.o2.in7,
            "in26": self.o2.in8,
            "in27": self.o2.in9,
            "in28": self.o2.in10,
            "in29": self.o2.in11,
            "in30": self.o2.in12,
            "in31": self.o2.in13,
            "in32": self.o2.in14,
            "in33": self.o2.in15,
            "in34": self.o2.in16,
            "in35": self.o2.in17,
            "in36": self.o2.in18,
            "in37": self.o3.in1,
            "in38": self.o3.in2,
            "in39": self.o3.in3,
            "in40": self.o3.in4,
            "in41": self.o3.in5,
            "in42": self.o3.in6,
            "in43": self.o3.in7,
            "in44": self.o3.in8,
            "in45": self.o3.in9,
            "in46": self.o3.in10,
            "in47": self.o3.in11,
            "in48": self.o3.in12,
            "in49": self.o3.in13,
            "in50": self.o3.in14,
            "in51": self.o3.in15,
            "in52": self.o3.in16,
            "in53": self.o3.in17,
            "in54": self.o3.in18,
            "in55": self.o4.in1,
            "in56": self.o4.in2,
            "in57": self.o4.in3,
            "in58": self.o4.in4,
            "in59": self.o4.in5,
            "in60": self.o4.in6,
            "in61": self.o4.in7,
            "in62": self.o4.in8,
            "in63": self.o4.in9,
            "in64": self.o4.in10,
            "in65": self.o4.in11,
            "in66": self.o4.in12,
            "in67": self.o4.in13,
            "in68": self.o4.in14,
            "in69": self.o4.in15,
            "in70": self.o4.in16,
            "in71": self.o4.in17,
            "in72": self.o4.in18,
            "in73": self.o5.in1,
            "in74": self.o5.in2,
            "in75": self.o5.in3,
            "in76": self.o5.in4,
            "in77": self.o5.in5,
            "in78": self.o5.in6,
            "in79": self.o5.in7,
            "in80": self.o5.in8,
            "in81": self.o5.in9,
            "in82": self.o5.in10,
            "in83": self.o5.in11,
            "in84": self.o5.in12,
            "in85": self.o5.in13,
            "in86": self.o5.in14,
            "in87": self.o5.in15,
            "in88": self.o5.in16,
            "in89": self.o5.in17,
            "in90": self.o5.in18,


            "out1": self.o9.out1,
            "out2": self.o9.out2,
            "out3": self.o9.out3,
            "out4": self.o9.out4,
            "out5": self.o9.out5,
            "out6": self.o9.out6,
            "out7": self.o9.out7,
            "out8": self.o9.out8,
            "out9": self.o9.out9,
        }

    def connect(self):
        return (
            (self.o1.out1, self.o6.in1),
            (self.o1.out2, self.o6.in2),
            (self.o1.out3, self.o6.in3),
            (self.o1.out4, self.o6.in4),
            (self.o1.out5, self.o6.in5),
            (self.o1.out6, self.o6.in6),
            (self.o1.out7, self.o6.in7),
            (self.o1.out8, self.o6.in8),
            (self.o1.out9, self.o6.in9),
            (self.o2.out1, self.o6.in10),
            (self.o2.out2, self.o6.in11),
            (self.o2.out3, self.o6.in12),
            (self.o2.out4, self.o6.in13),
            (self.o2.out5, self.o6.in14),
            (self.o2.out6, self.o6.in15),
            (self.o2.out7, self.o6.in16),
            (self.o2.out8, self.o6.in17),
            (self.o2.out9, self.o6.in18),

            (self.o3.out1, self.o7.in1),
            (self.o3.out2, self.o7.in2),
            (self.o3.out3, self.o7.in3),
            (self.o3.out4, self.o7.in4),
            (self.o3.out5, self.o7.in5),
            (self.o3.out6, self.o7.in6),
            (self.o3.out7, self.o7.in7),
            (self.o3.out8, self.o7.in8),
            (self.o3.out9, self.o7.in9),
            (self.o4.out1, self.o7.in10),
            (self.o4.out2, self.o7.in11),
            (self.o4.out3, self.o7.in12),
            (self.o4.out4, self.o7.in13),
            (self.o4.out5, self.o7.in14),
            (self.o4.out6, self.o7.in15),
            (self.o4.out7, self.o7.in16),
            (self.o4.out8, self.o7.in17),
            (self.o4.out9, self.o7.in18),

            (self.o6.out1, self.o8.in1),
            (self.o6.out2, self.o8.in2),
            (self.o6.out3, self.o8.in3),
            (self.o6.out4, self.o8.in4),
            (self.o6.out5, self.o8.in5),
            (self.o6.out6, self.o8.in6),
            (self.o6.out7, self.o8.in7),
            (self.o6.out8, self.o8.in8),
            (self.o6.out9, self.o8.in9),
            (self.o7.out1, self.o8.in10),
            (self.o7.out2, self.o8.in11),
            (self.o7.out3, self.o8.in12),
            (self.o7.out4, self.o8.in13),
            (self.o7.out5, self.o8.in14),
            (self.o7.out6, self.o8.in15),
            (self.o7.out7, self.o8.in16),
            (self.o7.out8, self.o8.in17),
            (self.o7.out9, self.o8.in18),

            (self.o8.out1, self.o9.in1),
            (self.o8.out2, self.o9.in2),
            (self.o8.out3, self.o9.in3),
            (self.o8.out4, self.o9.in4),
            (self.o8.out5, self.o9.in5),
            (self.o8.out6, self.o9.in6),
            (self.o8.out7, self.o9.in7),
            (self.o8.out8, self.o9.in8),
            (self.o8.out9, self.o9.in9),
            (self.o5.out1, self.o9.in10),
            (self.o5.out2, self.o9.in11),
            (self.o5.out3, self.o9.in12),
            (self.o5.out4, self.o9.in13),
            (self.o5.out5, self.o9.in14),
            (self.o5.out6, self.o9.in15),
            (self.o5.out7, self.o9.in16),
            (self.o5.out8, self.o9.in17),
            (self.o5.out9, self.o9.in18),
        )


class F(Circuit):
    ELEMENTS = {
        NOT: ('n1',),
        AND: ("a1",),
        Bridge: ("b1",)
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "out1": self.a1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.n1.in1),
            (self.n1.out1, self.a1.in1),
            (self.b1.out1, self.a1.in2),
        )


class NOT8_SEG(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2", "n3", "n4"),
        AND4: ("a1",),
        AND8: ("a8",),
        Bridge: ("b1",),
        NOT8: ("N1",),
        F: ("F1",)
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.n2.in1,
            "in3": self.n3.in1,
            "in4": self.n4.in1,

            "in5": self.N1.in1,
            "in6": self.N1.in2,
            "in7": self.N1.in3,
            "in8": self.N1.in4,
            "in9": self.N1.in5,
            "in10": self.N1.in6,
            "in11": self.N1.in7,
            "in12": self.N1.in8,

            "out1": self.a8.out1,
            "out2": self.a8.out2,
            "out3": self.a8.out3,
            "out4": self.a8.out4,
            "out5": self.a8.out5,
            "out6": self.a8.out6,
            "out7": self.a8.out7,
            "out8": self.a8.out8,
            "out9": self.F1.out1,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a1.in1),
            (self.n2.out1, self.a1.in2),
            (self.n3.out1, self.a1.in3),
            (self.n4.out1, self.a1.in4),
            (self.a1.out1, self.b1.in1),

            (self.N1.out1, self.a8.in1),
            (self.N1.out2, self.a8.in2),
            (self.N1.out3, self.a8.in3),
            (self.N1.out4, self.a8.in4),
            (self.N1.out5, self.a8.in5),
            (self.N1.out6, self.a8.in6),
            (self.N1.out7, self.a8.in7),
            (self.N1.out8, self.a8.in8),

            (self.b1.out1, self.a8.in9),
            (self.b1.out1, self.a8.in10),
            (self.b1.out1, self.a8.in11),
            (self.b1.out1, self.a8.in12),
            (self.b1.out1, self.a8.in13),
            (self.b1.out1, self.a8.in14),
            (self.b1.out1, self.a8.in15),
            (self.b1.out1, self.a8.in16),

            (self.b1.out1, self.F1.in1),
        )


class OR8_SEG(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2", "n3"),
        AND4: ("a1",),
        AND8: ("a8",),
        Bridge: ("b1",),
        OR8: ("N1",),
        F: ("F1",)
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.n2.in1,
            "in3": self.n3.in1,
            "in4": self.a1.in4,

            "in5": self.N1.in1,
            "in6": self.N1.in2,
            "in7": self.N1.in3,
            "in8": self.N1.in4,
            "in9": self.N1.in5,
            "in10": self.N1.in6,
            "in11": self.N1.in7,
            "in12": self.N1.in8,
            "in13": self.N1.in9,
            "in14": self.N1.in10,
            "in15": self.N1.in11,
            "in16": self.N1.in12,
            "in17": self.N1.in13,
            "in18": self.N1.in14,
            "in19": self.N1.in15,
            "in20": self.N1.in16,

            "out1": self.a8.out1,
            "out2": self.a8.out2,
            "out3": self.a8.out3,
            "out4": self.a8.out4,
            "out5": self.a8.out5,
            "out6": self.a8.out6,
            "out7": self.a8.out7,
            "out8": self.a8.out8,
            "out9": self.F1.out1,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a1.in1),
            (self.n2.out1, self.a1.in2),
            (self.n3.out1, self.a1.in3),
            (self.a1.out1, self.b1.in1),

            (self.N1.out1, self.a8.in1),
            (self.N1.out2, self.a8.in2),
            (self.N1.out3, self.a8.in3),
            (self.N1.out4, self.a8.in4),
            (self.N1.out5, self.a8.in5),
            (self.N1.out6, self.a8.in6),
            (self.N1.out7, self.a8.in7),
            (self.N1.out8, self.a8.in8),

            (self.b1.out1, self.a8.in9),
            (self.b1.out1, self.a8.in10),
            (self.b1.out1, self.a8.in11),
            (self.b1.out1, self.a8.in12),
            (self.b1.out1, self.a8.in13),
            (self.b1.out1, self.a8.in14),
            (self.b1.out1, self.a8.in15),
            (self.b1.out1, self.a8.in16),

            (self.b1.out1, self.F1.in1),
        )


class AND8_SEG(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2", "n3"),
        AND4: ("a1",),
        AND8: ("a8", "N1"),
        Bridge: ("b1",),
        F: ("F1",)
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.n2.in1,
            "in3": self.a1.in4,
            "in4": self.n3.in1,

            "in5": self.N1.in1,
            "in6": self.N1.in2,
            "in7": self.N1.in3,
            "in8": self.N1.in4,
            "in9": self.N1.in5,
            "in10": self.N1.in6,
            "in11": self.N1.in7,
            "in12": self.N1.in8,
            "in13": self.N1.in9,
            "in14": self.N1.in10,
            "in15": self.N1.in11,
            "in16": self.N1.in12,
            "in17": self.N1.in13,
            "in18": self.N1.in14,
            "in19": self.N1.in15,
            "in20": self.N1.in16,

            "out1": self.a8.out1,
            "out2": self.a8.out2,
            "out3": self.a8.out3,
            "out4": self.a8.out4,
            "out5": self.a8.out5,
            "out6": self.a8.out6,
            "out7": self.a8.out7,
            "out8": self.a8.out8,
            "out9": self.F1.out1,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a1.in1),
            (self.n2.out1, self.a1.in2),
            (self.n3.out1, self.a1.in3),
            (self.a1.out1, self.b1.in1),

            (self.N1.out1, self.a8.in1),
            (self.N1.out2, self.a8.in2),
            (self.N1.out3, self.a8.in3),
            (self.N1.out4, self.a8.in4),
            (self.N1.out5, self.a8.in5),
            (self.N1.out6, self.a8.in6),
            (self.N1.out7, self.a8.in7),
            (self.N1.out8, self.a8.in8),

            (self.b1.out1, self.a8.in9),
            (self.b1.out1, self.a8.in10),
            (self.b1.out1, self.a8.in11),
            (self.b1.out1, self.a8.in12),
            (self.b1.out1, self.a8.in13),
            (self.b1.out1, self.a8.in14),
            (self.b1.out1, self.a8.in15),
            (self.b1.out1, self.a8.in16),

            (self.b1.out1, self.F1.in1),
        )


class EQ8_SEG(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2"),
        AND4: ("a4",),
        AND: ("a",),
        EQ8: ("E1",),
        F: ("F1",),
        Bridge: ("b1", "b2",)
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.n2.in1,
            "in3": self.a4.in3,
            "in4": self.a4.in4,

            "in5": self.E1.in1,
            "in6": self.E1.in2,
            "in7": self.E1.in3,
            "in8": self.E1.in4,
            "in9": self.E1.in5,
            "in10": self.E1.in6,
            "in11": self.E1.in7,
            "in12": self.E1.in8,
            "in13": self.E1.in9,
            "in14": self.E1.in10,
            "in15": self.E1.in11,
            "in16": self.E1.in12,
            "in17": self.E1.in13,
            "in18": self.E1.in14,
            "in19": self.E1.in15,
            "in20": self.E1.in16,

            "out1": self.b2.out1,

            "out2": self.b1.out1,
            "out3": self.b1.out1,
            "out4": self.b1.out1,
            "out5": self.b1.out1,
            "out6": self.b1.out1,
            "out7": self.b1.out1,
            "out8": self.b1.out1,
            "out9": self.b1.out1,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a4.in1),
            (self.n2.out1, self.a4.in2),
            (self.a4.out1, self.a.in2),

            (self.E1.out1, self.a.in1),
            (self.a.out1, self.b2.in1),

            (self.b2.out1, self.F1.in1),
            (self.F1.out1, self.b1.in1),
        )


class NEQ8_SEG(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2", "n3"),
        AND4: ("a4",),
        AND: ("a",),
        NEQ8: ("E1",),
        F: ("F1",),
        Bridge: ("b1", "b2",)
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.a4.in2,
            "in3": self.n2.in1,
            "in4": self.n3.in1,

            "in5": self.E1.in1,
            "in6": self.E1.in2,
            "in7": self.E1.in3,
            "in8": self.E1.in4,
            "in9": self.E1.in5,
            "in10": self.E1.in6,
            "in11": self.E1.in7,
            "in12": self.E1.in8,
            "in13": self.E1.in9,
            "in14": self.E1.in10,
            "in15": self.E1.in11,
            "in16": self.E1.in12,
            "in17": self.E1.in13,
            "in18": self.E1.in14,
            "in19": self.E1.in15,
            "in20": self.E1.in16,

            "out1": self.b2.out1,

            "out2": self.b1.out1,
            "out3": self.b1.out1,
            "out4": self.b1.out1,
            "out5": self.b1.out1,
            "out6": self.b1.out1,
            "out7": self.b1.out1,
            "out8": self.b1.out1,
            "out9": self.b1.out1,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a4.in1),
            (self.n2.out1, self.a4.in3),
            (self.n3.out1, self.a4.in4),
            (self.a4.out1, self.a.in2),

            (self.E1.out1, self.a.in1),
            (self.a.out1, self.b2.in1),

            (self.b2.out1, self.F1.in1),
            (self.F1.out1, self.b1.in1),
        )


class GT8_SEG(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2"),
        AND4: ("a4",),
        AND: ("a",),
        GT8: ("E1",),
        F: ("F1",),
        Bridge: ("b1", "b2",)
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.a4.in2,
            "in3": self.n2.in1,
            "in4": self.a4.in4,

            "in5": self.E1.in1,
            "in6": self.E1.in2,
            "in7": self.E1.in3,
            "in8": self.E1.in4,
            "in9": self.E1.in5,
            "in10": self.E1.in6,
            "in11": self.E1.in7,
            "in12": self.E1.in8,
            "in13": self.E1.in9,
            "in14": self.E1.in10,
            "in15": self.E1.in11,
            "in16": self.E1.in12,
            "in17": self.E1.in13,
            "in18": self.E1.in14,
            "in19": self.E1.in15,
            "in20": self.E1.in16,

            "out1": self.b2.out1,

            "out2": self.b1.out1,
            "out3": self.b1.out1,
            "out4": self.b1.out1,
            "out5": self.b1.out1,
            "out6": self.b1.out1,
            "out7": self.b1.out1,
            "out8": self.b1.out1,
            "out9": self.b1.out1,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a4.in1),
            (self.n2.out1, self.a4.in3),
            (self.a4.out1, self.a.in2),

            (self.E1.out1, self.a.in1),
            (self.a.out1, self.b2.in1),

            (self.b2.out1, self.F1.in1),
            (self.F1.out1, self.b1.in1),
        )


class LT8_SEG(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2"),
        AND4: ("a4",),
        AND: ("a",),
        LT8: ("E1",),
        F: ("F1",),
        Bridge: ("b1", "b2",)
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.a4.in2,
            "in3": self.a4.in3,
            "in4": self.n2.in1,

            "in5": self.E1.in1,
            "in6": self.E1.in2,
            "in7": self.E1.in3,
            "in8": self.E1.in4,
            "in9": self.E1.in5,
            "in10": self.E1.in6,
            "in11": self.E1.in7,
            "in12": self.E1.in8,
            "in13": self.E1.in9,
            "in14": self.E1.in10,
            "in15": self.E1.in11,
            "in16": self.E1.in12,
            "in17": self.E1.in13,
            "in18": self.E1.in14,
            "in19": self.E1.in15,
            "in20": self.E1.in16,

            "out1": self.b2.out1,

            "out2": self.b1.out1,
            "out3": self.b1.out1,
            "out4": self.b1.out1,
            "out5": self.b1.out1,
            "out6": self.b1.out1,
            "out7": self.b1.out1,
            "out8": self.b1.out1,
            "out9": self.b1.out1,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a4.in1),
            (self.n2.out1, self.a4.in4),
            (self.a4.out1, self.a.in2),

            (self.E1.out1, self.a.in1),
            (self.a.out1, self.b2.in1),

            (self.b2.out1, self.F1.in1),
            (self.F1.out1, self.b1.in1),
        )


class GTE8_SEG(Circuit):
    ELEMENTS = {
        NOT: ("n1",),
        AND4: ("a4",),
        AND: ("a",),
        GTE8: ("E1",),
        F: ("F1",),
        Bridge: ("b1", "b2",)
    }

    def inout(self):
        return {
            "in1": self.n1.in1,
            "in2": self.a4.in2,
            "in3": self.a4.in3,
            "in4": self.a4.in4,

            "in5": self.E1.in1,
            "in6": self.E1.in2,
            "in7": self.E1.in3,
            "in8": self.E1.in4,
            "in9": self.E1.in5,
            "in10": self.E1.in6,
            "in11": self.E1.in7,
            "in12": self.E1.in8,
            "in13": self.E1.in9,
            "in14": self.E1.in10,
            "in15": self.E1.in11,
            "in16": self.E1.in12,
            "in17": self.E1.in13,
            "in18": self.E1.in14,
            "in19": self.E1.in15,
            "in20": self.E1.in16,

            "out1": self.b2.out1,

            "out2": self.b1.out1,
            "out3": self.b1.out1,
            "out4": self.b1.out1,
            "out5": self.b1.out1,
            "out6": self.b1.out1,
            "out7": self.b1.out1,
            "out8": self.b1.out1,
            "out9": self.b1.out1,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a4.in1),
            (self.a4.out1, self.a.in2),

            (self.E1.out1, self.a.in1),
            (self.a.out1, self.b2.in1),

            (self.b2.out1, self.F1.in1),
            (self.F1.out1, self.b1.in1),
        )


class LTE8_SEG(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2", "n3"),
        AND4: ("a4",),
        AND: ("a",),
        LTE8: ("E1",),
        F: ("F1",),
        Bridge: ("b1", "b2",)
    }

    def inout(self):
        return {
            "in1": self.a4.in1,
            "in2": self.n1.in1,
            "in3": self.n2.in1,
            "in4": self.n3.in1,

            "in5": self.E1.in1,
            "in6": self.E1.in2,
            "in7": self.E1.in3,
            "in8": self.E1.in4,
            "in9": self.E1.in5,
            "in10": self.E1.in6,
            "in11": self.E1.in7,
            "in12": self.E1.in8,
            "in13": self.E1.in9,
            "in14": self.E1.in10,
            "in15": self.E1.in11,
            "in16": self.E1.in12,
            "in17": self.E1.in13,
            "in18": self.E1.in14,
            "in19": self.E1.in15,
            "in20": self.E1.in16,

            "out1": self.b2.out1,

            "out2": self.b1.out1,
            "out3": self.b1.out1,
            "out4": self.b1.out1,
            "out5": self.b1.out1,
            "out6": self.b1.out1,
            "out7": self.b1.out1,
            "out8": self.b1.out1,
            "out9": self.b1.out1,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a4.in2),
            (self.n2.out1, self.a4.in3),
            (self.n3.out1, self.a4.in4),
            (self.a4.out1, self.a.in2),

            (self.E1.out1, self.a.in1),
            (self.a.out1, self.b2.in1),

            (self.b2.out1, self.F1.in1),
            (self.F1.out1, self.b1.in1),
        )


class ADD8_SEG(Circuit):
    ELEMENTS = {
        ADD8: ("ADD8",),
        NOT: ("n1", "n2"),
        AND4: ("a4",),
        AND9: ("a9",),
        Bridge: ("b1",)
    }

    def inout(self):
        return {
            "in1": self.a4.in1,
            "in2": self.n1.in1,
            "in3": self.n2.in1,
            "in4": self.a4.in4,
            "in5": self.ADD8.in1,
            "in6": self.ADD8.in2,
            "in7": self.ADD8.in3,
            "in8": self.ADD8.in4,
            "in9": self.ADD8.in5,
            "in10": self.ADD8.in6,
            "in11": self.ADD8.in7,
            "in12": self.ADD8.in8,
            "in13": self.ADD8.in9,
            "in14": self.ADD8.in10,
            "in15": self.ADD8.in11,
            "in16": self.ADD8.in12,
            "in17": self.ADD8.in13,
            "in18": self.ADD8.in14,
            "in19": self.ADD8.in15,
            "in20": self.ADD8.in16,

            "out1": self.a9.out1,
            "out2": self.a9.out2,
            "out3": self.a9.out3,
            "out4": self.a9.out4,
            "out5": self.a9.out5,
            "out6": self.a9.out6,
            "out7": self.a9.out7,
            "out8": self.a9.out8,
            "out9": self.a9.out9,
        }

    def connect(self):
        return (
            (self.n1.out1, self.a4.in2),
            (self.n2.out1, self.a4.in3),
            (self.a4.out1, self.b1.in1),

            (self.b1.out1, self.a9.in1),
            (self.b1.out1, self.a9.in2),
            (self.b1.out1, self.a9.in3),
            (self.b1.out1, self.a9.in4),
            (self.b1.out1, self.a9.in5),
            (self.b1.out1, self.a9.in6),
            (self.b1.out1, self.a9.in7),
            (self.b1.out1, self.a9.in8),
            (self.b1.out1, self.a9.in9),

            (self.ADD8.out1, self.a9.in10),
            (self.ADD8.out2, self.a9.in11),
            (self.ADD8.out3, self.a9.in12),
            (self.ADD8.out4, self.a9.in13),
            (self.ADD8.out5, self.a9.in14),
            (self.ADD8.out6, self.a9.in15),
            (self.ADD8.out7, self.a9.in16),
            (self.ADD8.out8, self.a9.in17),
            (self.ADD8.out9, self.a9.in18),
        )


class ALU(Circuit):
    ELEMENTS = {
        NOT8_SEG: ("NOT8_SEG",),
        OR8_SEG: ("OR8_SEG",),
        AND8_SEG: ("AND8_SEG",),
        EQ8_SEG: ("EQ8_SEG",),
        NEQ8_SEG: ("NEQ8_SEG",),
        GT8_SEG: ("GT8_SEG",),
        LT8_SEG: ("LT8_SEG",),
        GTE8_SEG: ("GTE8_SEG",),
        LTE8_SEG: ("LTE8_SEG",),
        ADD8_SEG: ("ADD8_SEG",),
        OR10_s: ("OR10",),
        Bridge: ("b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10", "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20")

    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "in4": self.b4.in1,
            "in5": self.b5.in1,
            "in6": self.b6.in1,
            "in7": self.b7.in1,
            "in8": self.b8.in1,
            "in9": self.b9.in1,
            "in10": self.b10.in1,
            "in11": self.b11.in1,
            "in12": self.b12.in1,
            "in13": self.b13.in1,
            "in14": self.b14.in1,
            "in15": self.b15.in1,
            "in16": self.b16.in1,
            "in17": self.b17.in1,
            "in18": self.b18.in1,
            "in19": self.b19.in1,
            "in20": self.b20.in1,

            "out1": self.OR10.out1,
            "out2": self.OR10.out2,
            "out3": self.OR10.out3,
            "out4": self.OR10.out4,
            "out5": self.OR10.out5,
            "out6": self.OR10.out6,
            "out7": self.OR10.out7,
            "out8": self.OR10.out8,
            "out9": self.OR10.out9,
        }

    def connect(self):
        return (
            (self.b1.out1, self.NOT8_SEG.in1),
            (self.b2.out1, self.NOT8_SEG.in2),
            (self.b3.out1, self.NOT8_SEG.in3),
            (self.b4.out1, self.NOT8_SEG.in4),
            (self.b5.out1, self.NOT8_SEG.in5),
            (self.b6.out1, self.NOT8_SEG.in6),
            (self.b7.out1, self.NOT8_SEG.in7),
            (self.b8.out1, self.NOT8_SEG.in8),
            (self.b9.out1, self.NOT8_SEG.in9),
            (self.b10.out1, self.NOT8_SEG.in10),
            (self.b11.out1, self.NOT8_SEG.in11),
            (self.b12.out1, self.NOT8_SEG.in12),

            (self.NOT8_SEG.out1, self.OR10.in1),
            (self.NOT8_SEG.out2, self.OR10.in2),
            (self.NOT8_SEG.out3, self.OR10.in3),
            (self.NOT8_SEG.out4, self.OR10.in4),
            (self.NOT8_SEG.out5, self.OR10.in5),
            (self.NOT8_SEG.out6, self.OR10.in6),
            (self.NOT8_SEG.out7, self.OR10.in7),
            (self.NOT8_SEG.out8, self.OR10.in8),
            (self.NOT8_SEG.out9, self.OR10.in9),


            (self.b1.out1, self.OR8_SEG.in1),
            (self.b2.out1, self.OR8_SEG.in2),
            (self.b3.out1, self.OR8_SEG.in3),
            (self.b4.out1, self.OR8_SEG.in4),
            (self.b5.out1, self.OR8_SEG.in5),
            (self.b6.out1, self.OR8_SEG.in6),
            (self.b7.out1, self.OR8_SEG.in7),
            (self.b8.out1, self.OR8_SEG.in8),
            (self.b9.out1, self.OR8_SEG.in9),
            (self.b10.out1, self.OR8_SEG.in10),
            (self.b11.out1, self.OR8_SEG.in11),
            (self.b12.out1, self.OR8_SEG.in12),
            (self.b13.out1, self.OR8_SEG.in13),
            (self.b14.out1, self.OR8_SEG.in14),
            (self.b15.out1, self.OR8_SEG.in15),
            (self.b16.out1, self.OR8_SEG.in16),
            (self.b17.out1, self.OR8_SEG.in17),
            (self.b18.out1, self.OR8_SEG.in18),
            (self.b19.out1, self.OR8_SEG.in19),
            (self.b20.out1, self.OR8_SEG.in20),

            (self.OR8_SEG.out1, self.OR10.in10),
            (self.OR8_SEG.out2, self.OR10.in11),
            (self.OR8_SEG.out3, self.OR10.in12),
            (self.OR8_SEG.out4, self.OR10.in13),
            (self.OR8_SEG.out5, self.OR10.in14),
            (self.OR8_SEG.out6, self.OR10.in15),
            (self.OR8_SEG.out7, self.OR10.in16),
            (self.OR8_SEG.out8, self.OR10.in17),
            (self.OR8_SEG.out9, self.OR10.in18),


            (self.b1.out1, self.AND8_SEG.in1),
            (self.b2.out1, self.AND8_SEG.in2),
            (self.b3.out1, self.AND8_SEG.in3),
            (self.b4.out1, self.AND8_SEG.in4),
            (self.b5.out1, self.AND8_SEG.in5),
            (self.b6.out1, self.AND8_SEG.in6),
            (self.b7.out1, self.AND8_SEG.in7),
            (self.b8.out1, self.AND8_SEG.in8),
            (self.b9.out1, self.AND8_SEG.in9),
            (self.b10.out1, self.AND8_SEG.in10),
            (self.b11.out1, self.AND8_SEG.in11),
            (self.b12.out1, self.AND8_SEG.in12),
            (self.b13.out1, self.AND8_SEG.in13),
            (self.b14.out1, self.AND8_SEG.in14),
            (self.b15.out1, self.AND8_SEG.in15),
            (self.b16.out1, self.AND8_SEG.in16),
            (self.b17.out1, self.AND8_SEG.in17),
            (self.b18.out1, self.AND8_SEG.in18),
            (self.b19.out1, self.AND8_SEG.in19),
            (self.b20.out1, self.AND8_SEG.in20),

            (self.AND8_SEG.out1, self.OR10.in19),
            (self.AND8_SEG.out2, self.OR10.in20),
            (self.AND8_SEG.out3, self.OR10.in21),
            (self.AND8_SEG.out4, self.OR10.in22),
            (self.AND8_SEG.out5, self.OR10.in23),
            (self.AND8_SEG.out6, self.OR10.in24),
            (self.AND8_SEG.out7, self.OR10.in25),
            (self.AND8_SEG.out8, self.OR10.in26),
            (self.AND8_SEG.out9, self.OR10.in27),


            (self.b1.out1, self.EQ8_SEG.in1),
            (self.b2.out1, self.EQ8_SEG.in2),
            (self.b3.out1, self.EQ8_SEG.in3),
            (self.b4.out1, self.EQ8_SEG.in4),
            (self.b5.out1, self.EQ8_SEG.in5),
            (self.b6.out1, self.EQ8_SEG.in6),
            (self.b7.out1, self.EQ8_SEG.in7),
            (self.b8.out1, self.EQ8_SEG.in8),
            (self.b9.out1, self.EQ8_SEG.in9),
            (self.b10.out1, self.EQ8_SEG.in10),
            (self.b11.out1, self.EQ8_SEG.in11),
            (self.b12.out1, self.EQ8_SEG.in12),
            (self.b13.out1, self.EQ8_SEG.in13),
            (self.b14.out1, self.EQ8_SEG.in14),
            (self.b15.out1, self.EQ8_SEG.in15),
            (self.b16.out1, self.EQ8_SEG.in16),
            (self.b17.out1, self.EQ8_SEG.in17),
            (self.b18.out1, self.EQ8_SEG.in18),
            (self.b19.out1, self.EQ8_SEG.in19),
            (self.b20.out1, self.EQ8_SEG.in20),

            (self.EQ8_SEG.out1, self.OR10.in28),
            (self.EQ8_SEG.out2, self.OR10.in29),
            (self.EQ8_SEG.out3, self.OR10.in30),
            (self.EQ8_SEG.out4, self.OR10.in31),
            (self.EQ8_SEG.out5, self.OR10.in32),
            (self.EQ8_SEG.out6, self.OR10.in33),
            (self.EQ8_SEG.out7, self.OR10.in34),
            (self.EQ8_SEG.out8, self.OR10.in35),
            (self.EQ8_SEG.out9, self.OR10.in36),


            (self.b1.out1, self.NEQ8_SEG.in1),
            (self.b2.out1, self.NEQ8_SEG.in2),
            (self.b3.out1, self.NEQ8_SEG.in3),
            (self.b4.out1, self.NEQ8_SEG.in4),
            (self.b5.out1, self.NEQ8_SEG.in5),
            (self.b6.out1, self.NEQ8_SEG.in6),
            (self.b7.out1, self.NEQ8_SEG.in7),
            (self.b8.out1, self.NEQ8_SEG.in8),
            (self.b9.out1, self.NEQ8_SEG.in9),
            (self.b10.out1, self.NEQ8_SEG.in10),
            (self.b11.out1, self.NEQ8_SEG.in11),
            (self.b12.out1, self.NEQ8_SEG.in12),
            (self.b13.out1, self.NEQ8_SEG.in13),
            (self.b14.out1, self.NEQ8_SEG.in14),
            (self.b15.out1, self.NEQ8_SEG.in15),
            (self.b16.out1, self.NEQ8_SEG.in16),
            (self.b17.out1, self.NEQ8_SEG.in17),
            (self.b18.out1, self.NEQ8_SEG.in18),
            (self.b19.out1, self.NEQ8_SEG.in19),
            (self.b20.out1, self.NEQ8_SEG.in20),

            (self.NEQ8_SEG.out1, self.OR10.in37),
            (self.NEQ8_SEG.out2, self.OR10.in38),
            (self.NEQ8_SEG.out3, self.OR10.in39),
            (self.NEQ8_SEG.out4, self.OR10.in40),
            (self.NEQ8_SEG.out5, self.OR10.in41),
            (self.NEQ8_SEG.out6, self.OR10.in42),
            (self.NEQ8_SEG.out7, self.OR10.in43),
            (self.NEQ8_SEG.out8, self.OR10.in44),
            (self.NEQ8_SEG.out9, self.OR10.in45),


            (self.b1.out1, self.GT8_SEG.in1),
            (self.b2.out1, self.GT8_SEG.in2),
            (self.b3.out1, self.GT8_SEG.in3),
            (self.b4.out1, self.GT8_SEG.in4),
            (self.b5.out1, self.GT8_SEG.in5),
            (self.b6.out1, self.GT8_SEG.in6),
            (self.b7.out1, self.GT8_SEG.in7),
            (self.b8.out1, self.GT8_SEG.in8),
            (self.b9.out1, self.GT8_SEG.in9),
            (self.b10.out1, self.GT8_SEG.in10),
            (self.b11.out1, self.GT8_SEG.in11),
            (self.b12.out1, self.GT8_SEG.in12),
            (self.b13.out1, self.GT8_SEG.in13),
            (self.b14.out1, self.GT8_SEG.in14),
            (self.b15.out1, self.GT8_SEG.in15),
            (self.b16.out1, self.GT8_SEG.in16),
            (self.b17.out1, self.GT8_SEG.in17),
            (self.b18.out1, self.GT8_SEG.in18),
            (self.b19.out1, self.GT8_SEG.in19),
            (self.b20.out1, self.GT8_SEG.in20),

            (self.GT8_SEG.out1, self.OR10.in46),
            (self.GT8_SEG.out2, self.OR10.in47),
            (self.GT8_SEG.out3, self.OR10.in48),
            (self.GT8_SEG.out4, self.OR10.in49),
            (self.GT8_SEG.out5, self.OR10.in50),
            (self.GT8_SEG.out6, self.OR10.in51),
            (self.GT8_SEG.out7, self.OR10.in52),
            (self.GT8_SEG.out8, self.OR10.in53),
            (self.GT8_SEG.out9, self.OR10.in54),


            (self.b1.out1, self.LT8_SEG.in1),
            (self.b2.out1, self.LT8_SEG.in2),
            (self.b3.out1, self.LT8_SEG.in3),
            (self.b4.out1, self.LT8_SEG.in4),
            (self.b5.out1, self.LT8_SEG.in5),
            (self.b6.out1, self.LT8_SEG.in6),
            (self.b7.out1, self.LT8_SEG.in7),
            (self.b8.out1, self.LT8_SEG.in8),
            (self.b9.out1, self.LT8_SEG.in9),
            (self.b10.out1, self.LT8_SEG.in10),
            (self.b11.out1, self.LT8_SEG.in11),
            (self.b12.out1, self.LT8_SEG.in12),
            (self.b13.out1, self.LT8_SEG.in13),
            (self.b14.out1, self.LT8_SEG.in14),
            (self.b15.out1, self.LT8_SEG.in15),
            (self.b16.out1, self.LT8_SEG.in16),
            (self.b17.out1, self.LT8_SEG.in17),
            (self.b18.out1, self.LT8_SEG.in18),
            (self.b19.out1, self.LT8_SEG.in19),
            (self.b20.out1, self.LT8_SEG.in20),

            (self.LT8_SEG.out1, self.OR10.in55),
            (self.LT8_SEG.out2, self.OR10.in56),
            (self.LT8_SEG.out3, self.OR10.in57),
            (self.LT8_SEG.out4, self.OR10.in58),
            (self.LT8_SEG.out5, self.OR10.in59),
            (self.LT8_SEG.out6, self.OR10.in60),
            (self.LT8_SEG.out7, self.OR10.in61),
            (self.LT8_SEG.out8, self.OR10.in62),
            (self.LT8_SEG.out9, self.OR10.in63),


            (self.b1.out1, self.GTE8_SEG.in1),
            (self.b2.out1, self.GTE8_SEG.in2),
            (self.b3.out1, self.GTE8_SEG.in3),
            (self.b4.out1, self.GTE8_SEG.in4),
            (self.b5.out1, self.GTE8_SEG.in5),
            (self.b6.out1, self.GTE8_SEG.in6),
            (self.b7.out1, self.GTE8_SEG.in7),
            (self.b8.out1, self.GTE8_SEG.in8),
            (self.b9.out1, self.GTE8_SEG.in9),
            (self.b10.out1, self.GTE8_SEG.in10),
            (self.b11.out1, self.GTE8_SEG.in11),
            (self.b12.out1, self.GTE8_SEG.in12),
            (self.b13.out1, self.GTE8_SEG.in13),
            (self.b14.out1, self.GTE8_SEG.in14),
            (self.b15.out1, self.GTE8_SEG.in15),
            (self.b16.out1, self.GTE8_SEG.in16),
            (self.b17.out1, self.GTE8_SEG.in17),
            (self.b18.out1, self.GTE8_SEG.in18),
            (self.b19.out1, self.GTE8_SEG.in19),
            (self.b20.out1, self.GTE8_SEG.in20),

            (self.GTE8_SEG.out1, self.OR10.in64),
            (self.GTE8_SEG.out2, self.OR10.in65),
            (self.GTE8_SEG.out3, self.OR10.in66),
            (self.GTE8_SEG.out4, self.OR10.in67),
            (self.GTE8_SEG.out5, self.OR10.in68),
            (self.GTE8_SEG.out6, self.OR10.in69),
            (self.GTE8_SEG.out7, self.OR10.in70),
            (self.GTE8_SEG.out8, self.OR10.in71),
            (self.GTE8_SEG.out9, self.OR10.in72),


            (self.b1.out1, self.LTE8_SEG.in1),
            (self.b2.out1, self.LTE8_SEG.in2),
            (self.b3.out1, self.LTE8_SEG.in3),
            (self.b4.out1, self.LTE8_SEG.in4),
            (self.b5.out1, self.LTE8_SEG.in5),
            (self.b6.out1, self.LTE8_SEG.in6),
            (self.b7.out1, self.LTE8_SEG.in7),
            (self.b8.out1, self.LTE8_SEG.in8),
            (self.b9.out1, self.LTE8_SEG.in9),
            (self.b10.out1, self.LTE8_SEG.in10),
            (self.b11.out1, self.LTE8_SEG.in11),
            (self.b12.out1, self.LTE8_SEG.in12),
            (self.b13.out1, self.LTE8_SEG.in13),
            (self.b14.out1, self.LTE8_SEG.in14),
            (self.b15.out1, self.LTE8_SEG.in15),
            (self.b16.out1, self.LTE8_SEG.in16),
            (self.b17.out1, self.LTE8_SEG.in17),
            (self.b18.out1, self.LTE8_SEG.in18),
            (self.b19.out1, self.LTE8_SEG.in19),
            (self.b20.out1, self.LTE8_SEG.in20),

            (self.LTE8_SEG.out1, self.OR10.in73),
            (self.LTE8_SEG.out2, self.OR10.in74),
            (self.LTE8_SEG.out3, self.OR10.in75),
            (self.LTE8_SEG.out4, self.OR10.in76),
            (self.LTE8_SEG.out5, self.OR10.in77),
            (self.LTE8_SEG.out6, self.OR10.in78),
            (self.LTE8_SEG.out7, self.OR10.in79),
            (self.LTE8_SEG.out8, self.OR10.in80),
            (self.LTE8_SEG.out9, self.OR10.in81),


            (self.b1.out1, self.ADD8_SEG.in1),
            (self.b2.out1, self.ADD8_SEG.in2),
            (self.b3.out1, self.ADD8_SEG.in3),
            (self.b4.out1, self.ADD8_SEG.in4),
            (self.b5.out1, self.ADD8_SEG.in5),
            (self.b6.out1, self.ADD8_SEG.in6),
            (self.b7.out1, self.ADD8_SEG.in7),
            (self.b8.out1, self.ADD8_SEG.in8),
            (self.b9.out1, self.ADD8_SEG.in9),
            (self.b10.out1, self.ADD8_SEG.in10),
            (self.b11.out1, self.ADD8_SEG.in11),
            (self.b12.out1, self.ADD8_SEG.in12),
            (self.b13.out1, self.ADD8_SEG.in13),
            (self.b14.out1, self.ADD8_SEG.in14),
            (self.b15.out1, self.ADD8_SEG.in15),
            (self.b16.out1, self.ADD8_SEG.in16),
            (self.b17.out1, self.ADD8_SEG.in17),
            (self.b18.out1, self.ADD8_SEG.in18),
            (self.b19.out1, self.ADD8_SEG.in19),
            (self.b20.out1, self.ADD8_SEG.in20),

            (self.ADD8_SEG.out1, self.OR10.in82),
            (self.ADD8_SEG.out2, self.OR10.in83),
            (self.ADD8_SEG.out3, self.OR10.in84),
            (self.ADD8_SEG.out4, self.OR10.in85),
            (self.ADD8_SEG.out5, self.OR10.in86),
            (self.ADD8_SEG.out6, self.OR10.in87),
            (self.ADD8_SEG.out7, self.OR10.in88),
            (self.ADD8_SEG.out8, self.OR10.in89),
            (self.ADD8_SEG.out9, self.OR10.in90),
        )
