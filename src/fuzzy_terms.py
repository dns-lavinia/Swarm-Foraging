import math
import matplotlib.pyplot as plt
import numpy as np 

from fuzzylogic.classes import Domain, Set, FuzzyWarning
from fuzzylogic.functions import triangular, linear


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
    #(a)
    laser_percep = DomainModified("laser perception", 0, 400, res=1)

    # Add the fuzzy set terms
    laser_percep.left = linear(m=-1.0/55, b=1.0)
    laser_percep.front = triangular(48, 150, c=100)
    laser_percep.right = linear(m=1.0/300, b=-1.0/3) 

    laser_percep.view()

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


if __name__ == "__main__":
    main()

