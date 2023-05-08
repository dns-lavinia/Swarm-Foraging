import math
import matplotlib.pyplot as plt
import numpy as np 

from fuzzylogic.classes import Domain, Set, FuzzyWarning, Rule
from fuzzylogic.functions import triangular, linear


class RuleModified(Rule):
    def __call__(self, args: "dict[Domain, float]", method="cog"):
        """Calculate the infered value based on different methods.
        Default is center of gravity (cog).
        """
        assert len(args) >= max(
            len(c) for c in self.conditions.keys()
        ), "Number of values must correspond to the number of domains defined as conditions!"
        assert isinstance(args, dict), "Please make sure to pass in the values as a dictionary."
        if method == "cog":
            assert (
                len({C.domain for C in self.conditions.values()}) == 1
            ), "For CoG, all conditions must have the same target domain."
            actual_values = {f: f(args[f.domain]) for S in self.conditions.keys() for f in S}

            weights = []
            for K, v in self.conditions.items():
                x = min((actual_values[k] for k in K if k in actual_values), default=0)
                if x > 0:
                    weights.append((v, x))

            if not weights:
                return None
            target_domain = list(self.conditions.values())[0].domain
            index = sum(v.center_of_gravity * x for v, x in weights) / sum(x for v, x in weights)
            return (target_domain._high - target_domain._low) / len(
                target_domain.range
            ) * index + target_domain._low


class DomainModified(Domain):
    __slots__ = ["_name", "_low", "_high", "_res", "_sets", "_fig"]
    def __init__(self, name, low, high, *, res=1, sets: dict = None):
        super(DomainModified, self).__init__(name, low, high, res=res, sets=sets)

        # Use a figure instead of a normal plot
        self._fig = plt.figure()

    
    def __setattr__(self, name, value):
        """Define a set within a domain or assign a value to a domain attribute."""
        # It's a domain attr
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        # We've got a fuzzyset
        else:
            assert str.isidentifier(name), f"{name} must be an identifier."
            if not isinstance(value, SetModified):
                # Often useful to just assign a function for simple sets..
                value = SetModified(value)
            # However, we need the abstraction if we want to use Superfuzzysets (derived sets).
            self._sets[name] = value
            value.domain = self
            value.name = name

    def view(self):
        """Plot all of the terms in the set."""

        for s in self._sets.values():
            s.plot()

        # Add the names of the x and y axis
        plt.xlabel(self._name)
        plt.ylabel("Membership")

        # Show the fuzzy terms names
        leg = plt.legend(loc='lower right')

        self._fig.show()


class SetModified(Set):
    def plot(self):
        if self.domain is None:
            raise FuzzyWarning("No domain assigned, cannot plot")
        
        R = self.domain.range
        V = [self.func(x) for x in R]
        
        # Get the indices for all of the values that are not zero for V
        idxs = list(np.nonzero(V)[0])

        # If it is a singleton term, then print it as is
        if len(idxs) == 1:
            x = (R[idxs[0]], R[idxs[0]])
            y = (0, 1)
            
            plt.plot(x, y, scaley=False, label=self.name)
            return

        # append start - 1 and end + 1 if possible
        if idxs[0] > 0 and V[idxs[0]] > 1e-10:
            idxs.insert(0, idxs[0] - 1)
        
        if idxs[-1] < len(V):
            idxs.append(idxs[-1] + 1)
        
        # Plot only 
        plt.plot(R[idxs[0]: idxs[-1] + 1], V[idxs[0]: idxs[-1] + 1], label=self.name)


def singleton(p, *, no_m=0, c_m=1):
    """This is a reimplementation of the `singleton` function found in the 
    `fuzzylogic.functions` module. 

    This change was done because in the case of a singleton memebership function
    for a floating point number, because of the representation errors, this 
    would always return false. Thus, for comparation purposes, `math.isclose()` 
    was used instead.
    """
    assert 0 <= no_m < c_m <= 1

    def f(x):
        return c_m if math.isclose(x, p, abs_tol=1e-9) else no_m
    return f


def main():
    # (a)
    # (left)
    left = DomainModified("laser perception", 0, 400, res=1)

    # Add the fuzzy set terms
    left.near = linear(m=-1.0/55, b=1.0)
    left.far = triangular(48, 150, c=100)
    left.emer = linear(m=1.0/300, b=-1.0/3) 

    left.view()

    # (right)
    right = DomainModified("laser perception", 0, 400, res=1)

    # Add the fuzzy set terms
    right.near = linear(m=-1.0/55, b=1.0)
    right.far = triangular(48, 150, c=100)
    right.emer = linear(m=1.0/300, b=-1.0/3) 

    # (front)
    front = DomainModified("laser perception", 0, 400, res=1)

    # Add the fuzzy set terms
    front.near = linear(m=-1.0/55, b=1.0)
    front.far = triangular(48, 150, c=100)
    front.emer = linear(m=1.0/300, b=-1.0/3) 

    # (b)
    dist = DomainModified("distance to goal", 0, 2000, res=5)

    # # Add the fuzzy set terms
    dist.near = linear(m=-1.0/20, b=1.0)
    dist.med = triangular(15, 125, c=70)
    dist.far = linear(m=1.0/1920, b=-1.0/24)

    dist.view()

    # (c)
    ang = DomainModified("angle of robot", -3.2, 3.2, res=0.1)

    # Add the fuzzy set terms
    ang.farl = linear(m=-1.0/2.8, b=-0.4/2.8)
    ang.medl = triangular(-1.2, 0)
    ang.near = triangular(-0.1, 0.1)
    ang.medr = triangular(0, 1.2)
    ang.farr = linear(m=1.0/2.8, b=-0.4/2.8)

    ang.view()

    # (d)
    vrot = DomainModified("rotational speed", -2.0, 2.0, res=0.1)

    # Add the fuzzy set terms
    vrot.hleft = singleton(-2)
    vrot.left = singleton(-1.5)
    vrot.none = singleton(0.0)
    vrot.right = singleton(1.5)
    vrot.hright = singleton(2)

    vrot.view()

    # (e)
    vtrans = DomainModified("translational speed", 0, 100, res=1)

    # Add the fuzzy set terms
    vtrans.stop = singleton(0) 
    vtrans.low = singleton(20)
    vtrans.medium = singleton(55)
    vtrans.high = singleton(100)

    vtrans.view()

    # Adding the rules for the collision avoidance FLC
    # Define the rules separately to keep track of what and how it was 
    # triggered
    R1 = RuleModified({(left.emer, right.emer, front.emer) : vrot.right})
    R2 = RuleModified({(left.emer, right.emer, front.far) : vrot.none})
    R3 = RuleModified({(left.emer, right.far) : vrot.hright})
    R4 = RuleModified({(right.emer, left.far, front.far) : vrot.hleft})
    R5 = RuleModified({(left.near, right.far) : vrot.right})
    R6 = RuleModified({(right.near, left.far) : vrot.left})

    # Define the whole system
    rules = RuleModified({
        (left.emer, right.emer, front.emer) : vrot.right,
        (left.emer, right.emer, front.far) : vrot.none,
        (left.emer, right.far) : vrot.hright,
        (right.emer, left.far, front.far) : vrot.hleft,
        (left.near, right.far) : vrot.right,
        (right.near, left.far) : vrot.left
    })

    values = {left: 20, right: 10, front: 300}
    # Rx = RuleModified({(left.emer, right.far) : vrot.hright})
    # print(Rx(values))
    
    print(R1(values), R2(values), R3(values), R4(values), R5(values), R6(values), "=>", rules(values))

    # Rx = RuleModified({(left.emer, right.emer, front.emer) : vrot.right})


if __name__ == "__main__":
    main()
