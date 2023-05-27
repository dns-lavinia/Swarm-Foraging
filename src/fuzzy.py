import math
import matplotlib.pyplot as plt
import numpy as np 

from fuzzylogic.functions import triangular, linear
from fuzzylogic.classes import Domain, Set, FuzzyWarning, Rule

class RuleModified(Rule):
    """Extends the `Rule` class by adding more functionality when it is called."""
    
    def __call__(self, args: "dict[Domain, float]", method="cog"):
        """Calculate the infered value based on different methods.
        Default is center of gravity (cog).

        This is a reimplementation of the original method that gives more 
        flexibility to a rule and accepts other methods for computing the infered
        value.

        Args:
            method(str): The method that is used for defuzzification. Accepted 
            inputs are `'cog'` or `'takagi-sugeno-0'`. Defaults to `'cog'`.

            `'takagi-sugeno-0'` means a zero order Sugeno system

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
        
        elif method == "tagaki-sugeno-0":
            # The Takagi-Sugeno weighted average is used as a deffuzification
            # method in this case, with the default value of 0, being a 
            # zero-order fuzzy model since the rule's consequent is a fuzzy
            # singleton

            assert (
                len({C.domain for C in self.conditions.values()}) == 1
            ), "For Takagi-Sugeno, all conditions must have the same target domain."

            # Given the input, store in a dict for each fuzzy term the value
            # of the membership function computed from the given input
            # 
            # f = Fuzzy term (e.g. dist.med, temp.high etc.)
            # f(args[f.domain]) membership value for the fuzzy term given an input
            # where the input is args[f.domain]
            actual_values = {f: f(args[f.domain]) for S in self.conditions.keys() for f in S}

            # Compute the weights 
            weights = []

            # For all of the terms of a fuzzy set
            for K, v in self.conditions.items():
                # For each fuzzy term k, if it is in the rule antecedents, store
                # its value in a list and get the minimum of them at the end
                x = min((actual_values[k] for k in K if k in actual_values), default=0)

                # If x is nonzero, then the fuzzy term is activated
                if x > 0:
                    # Compute the rule output level 
                    z = [x for x in v.domain.range if v.func(x) == 1][0]

                    if z is None:
                        raise FuzzyWarning("Singleton function not properly implemented.") 

                    # Append a tuple of the form (fuzzy term, x, z)
                    weights.append((v, x, z))
            
            # If nothing was activated, return None
            if not weights:
                return None 
            
            # Get the domain of the consequent
            target_domain = list(self.conditions.values())[0].domain
            output = sum(z * x for _, x, z in weights) / sum(x for _, x, _ in weights)

            return output
            
        else:
            raise FuzzyWarning(f'Unknown method for defuzzification: {method}.')


class DomainModified(Domain):
    """Extends the `Domain` class by adding a new way to plot all of the Sets
    that are part of the Domain better."""

    def view(self):
        """Plot all of the terms in the set."""
        fig = plt.figure()

        for s in self._sets.values():
            s.plot()

        # Add the names of the x and y axis
        plt.xlabel(self._name)
        plt.ylabel("Membership")

        # Show the fuzzy terms names
        leg = plt.legend(loc='lower right')

        fig.show()


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


class RobotFuzzySystem:
    def __init__(self):
        """Initialize all of the terms and sets needed for the system."""

        # Fuzzy sets that represent the perception of the distance for the three
        # zones (left, front, right)

        # (left)
        self.left = self.__init_percep_set(name="Laser perception for left zone")

        # (right)
        self.right = self.__init_percep_set(name="Laser perception for right zone")

        # (front)
        self.front = self.__init_percep_set(name="Laser perception for front zone")

        # Fuzzy set representing the distance to the goal 
        self.dist = DomainModified(name="Distance to goal", low=0, high=2000, res=5)
        self.dist.near = linear(m=-1.0/40, b=1.0)
        self.dist.med = triangular(low=30, high=200)
        self.dist.far = linear(m=3240.0/182, b=-18.0/182)

        # Fuzzy set representing the angle of the robot itself relative to the goal
        self.ang = DomainModified(name="Angle of robot", low=-3.2, high=3.2, res=0.1)
        self.ang.farl = linear(m=-1.0/2.4, b=-0.8/2.4)
        self.ang.medl = triangular(low=-1.2, high=0)
        self.ang.near = triangular(low=-0.1, high=0.1)
        self.ang.medr = triangular(low=0, high=1.2)
        self.ang.farr = linear(m=1.0/2.4, b=-0.8/2.4)

        # Fuzzy set representing the rotational speed
        self.vrot = DomainModified(name="Rotational speed", low=-2.0, high=2.0, res=0.1)
        self.vrot.hleft = singleton(-2)
        self.vrot.left = singleton(-1.5)
        self.vrot.none = singleton(0.0)
        self.vrot.right = singleton(1.5)
        self.vrot.hright = singleton(2)

        # Fuzzy set for the translational speed
        self.vtrans = DomainModified("Translational speed", low=0, high=100, res=1)
        self.vtrans.stop = singleton(0) 
        self.vtrans.low = singleton(20)
        self.vtrans.medium = singleton(55)
        self.vtrans.high = singleton(100)

    def __init_percep_set(self, name):
        """This method should be used for the terms related to zones perception.
        
        Args:
            name (str): The name associated with the newly created domain.

        Returns a `DomainModified` object.
        """

        percep = DomainModified(name, low=0, high=400, res=1)

        # Add the fuzzy set terms
        percep.near = linear(m=-1.0/55, b=1.0)
        percep.med = triangular(low=48, high=150, c=100)
        percep.far = triangular(low=100, high=350)
        percep.emer = linear(m=1.0/80.0, b=-4.0) 

        return percep

    def __get_avoidance_rules(self):
        """
        Returns:
            dict: Rules that are used for the FLC that deals with collision 
            avoidance.
        """

        return {
            (self.left.emer, self.right.emer, self.front.emer) : self.vrot.right,  # base
            (self.left.emer, self.right.emer, self.front.far) : self.vrot.none,  # base
            (self.left.emer, self.right.emer, self.front.med) : self.vrot.none,
            (self.left.emer, self.right.emer, self.front.near) : self.vrot.none,

            (self.left.emer, self.right.far) : self.vrot.hright,  # base
            (self.left.emer, self.right.med) : self.vrot.right,

            (self.right.emer, self.left.far) : self.vrot.hleft,  # base
            (self.right.emer, self.left.med) : self.vrot.left,
            
            (self.left.near, self.right.far) : self.vrot.right,  # base
            (self.left.med, self.right.far) : self.vrot.right,
            (self.left.med, self.right.emer) : self.vrot.right,

            (self.right.near, self.left.far) : self.vrot.left,  # base
            (self.right.med, self.left.far) : self.vrot.left,
            (self.right.med, self.left.emer) : self.vrot.left,
        }
    
    def __get_rendevous_rules_vrot(self):
        """
        Returns:
            dict: Rules that are used for the FLC that deals with the navigation
            towards the goal having `vrot` as consequent.
        """

        return {
            (self.ang.near,) : self.vrot.none,
            (self.ang.medl,) : self.vrot.right,
            (self.ang.medr,) : self.vrot.left,
            (self.ang.farl,) : self.vrot.hright,
            (self.ang.farr,) : self.vrot.hleft,
        }

    def __get_rendevous_rules_vtrans(self):
        """
        Returns:
            dict: Rules that are used for the FLC that deals with the navigation
            towards the goal having `vtrans` as consequent.
        """

        return {
            (self.dist.far,) : self.vtrans.high,
            (self.dist.med,) : self.vtrans.medium,
            (self.dist.near,) : self.vtrans.stop,
            (self.front.emer,) : self.vtrans.medium,
            (self.front.near,) : self.vtrans.medium 
        }
    
    def evaluate(self, inp_left, inp_front, inp_right, inp_ang, inp_dist):
        """Fuzzy logic controller that combines the rendevous and avoidance FLCs.
        
        Returns:
            [float, float]: List containing the defuzzified values for vtrans 
            (translational speed) and for vrot (rotational speed) in this order."""

        input_data = {
            self.left: inp_left,
            self.front: inp_front,
            self.right: inp_right,
            self.ang: inp_ang,
            self.dist: inp_dist
        }

        rendevous_rules_vrot = self.__get_rendevous_rules_vrot()
        rendevous_rules_vtrans = self.__get_rendevous_rules_vtrans()
        avoidance_rules = {}

        # Save in the new dict the avoidance rules with extended constraints
        for antecedents, consequent in self.__get_avoidance_rules().items():
            rule_updated = antecedents + (self.dist.far, self.dist.med,)
            avoidance_rules[rule_updated] = consequent
        
        rules_vrot = RuleModified((rendevous_rules_vrot | avoidance_rules))
        rules_vtrans = RuleModified(rendevous_rules_vtrans)

        print(f"Input data for FLC is:")
        print(f"\t left: {inp_left}")
        print(f"\t front: {inp_front}")
        print(f"\t right: {inp_right}")
        print(f"\t ang: {inp_ang}")


        vtras = rules_vtrans(input_data, method="tagaki-sugeno-0")
        vrot = rules_vrot(input_data, method="tagaki-sugeno-0")

        print(f"The resulted vrot is {vrot}")
        print("\n")

        # Returned the defuzzified results separate for vtrans and vrot
        return vtras, vrot