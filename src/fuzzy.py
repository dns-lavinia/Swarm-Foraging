import math
import matplotlib.pyplot as plt
import numpy as np 

from fuzzylogic.classes import Domain, Set, FuzzyWarning, Rule

class RuleModified(Rule):
    """Extends the `Rule` class by adding more functionality when it is called."""
    
    def __call__(self, args: "dict[Domain, float]", method="cog"):
        """Calculate the infered value based on different methods.
        Default is center of gravity (cog).

        This is a reimplementation of the original method that gives more 
        flexibility to a rule and accepts other methods for computing the infered
        value.
        """
        assert len(args) >= max(
            len(c) for c in self.conditions.keys()
        ), "Number of values must correspond to the number of domains defined as conditions!"
        assert isinstance(args, dict), "Please make sure to pass in the values as a dictionary."
        
        # If the method used is center of gravity
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
        else:
            #TODO: implement the case in which the method is not cog
            pass


class DomainModified(Domain):
    """Extends the `Domain` class by adding a new way to plot all of the Sets
    that are part of the Domain better."""

    __slots__ = ["_name", "_low", "_high", "_res", "_sets", "_fig"]

    def __init__(self, name, low, high, *, res=1, sets: dict = None):
        super(DomainModified, self).__init__(name, low, high, res=res, sets=sets)

        # Use a figure instead of a normal plot
        self._fig = plt.figure()

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

def plot(set_obj):
    """Plot a Set only as much as it is needed (does not plot all of the values
    for which the membership function is 0).

    Args:
        set_obj (Set): An instance of the Set object.
    """

    if set_obj.domain is None:
        raise FuzzyWarning("No domain assigned, cannot plot")
        
    R = set_obj.domain.range
    V = [set_obj.func(x) for x in R]
    
    # Get the indices for all of the values that are not zero for V
    idxs = list(np.nonzero(V)[0])

    # If it is a singleton term, then plot it as is
    if len(idxs) == 1:
        x = (R[idxs[0]], R[idxs[0]])
        y = (0, 1)
        
        plt.plot(x, y, scaley=False, label=set_obj.name)
        return

    # Append start - 1 and end + 1 if possible
    if idxs[0] > 0 and V[idxs[0]] > 1e-10:
        idxs.insert(0, idxs[0] - 1)
    
    if idxs[-1] < len(V):
        idxs.append(idxs[-1] + 1)
    
    # Plot only a slice of the Set
    plt.plot(R[idxs[0]: idxs[-1] + 1], V[idxs[0]: idxs[-1] + 1], label=set_obj.name)


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

# Override the method that plots a Set so it looks smoother and better
Set.plot = plot