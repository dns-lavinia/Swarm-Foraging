from fuzzy import DomainModified, RuleModified, singleton
from fuzzylogic.functions import triangular, linear

class FuzzySystem:
    def __init__(self):
        """Initialize all of the terms and sets needed for the system."""

        # (a) Fuzzy sets that are used for the perception of the distance for
        # the three zones (left, front, right)

        # (left)
        self.left = self.__init_percep_set("laser perception for left zone")

        # (right)
        self.right = self.__init_percep_set("laser perception for right zone")

        # (front)
        self.front = self.__init_percep_set("laser perception for front zone")

        # (d) Fuzzy set used for the rotational speed
        self.vrot = DomainModified("rotational speed", -2.0, 2.0, res=0.1)

        # Add the fuzzy set terms
        self.vrot.hleft = singleton(-2)
        self.vrot.left = singleton(-1.5)
        self.vrot.none = singleton(0.0)
        self.vrot.right = singleton(1.5)
        self.vrot.hright = singleton(2)

    def __init_percep_set(self, name):
        """This method should be used for the terms related to zones perception.
        

        Args:
            name (str): The name associated with the newly created domain

        Returns a `DomainModified` object.
        """

        percep = DomainModified(name, 0, 400, res=1)

        # Add the fuzzy set terms
        percep.near = linear(m=-1.0/55, b=1.0)
        percep.far = triangular(48, 150, c=100)
        percep.emer = linear(m=1.0/300, b=-1.0/3) 

        return percep

    def flc_avoidance(self, inp_left, inp_front, inp_right):
        input_data = {
            self.left: inp_left,
            self.front: inp_front,
            self.right: inp_right
        }
            
        # Adding the rules for the collision avoidance FLC
        # Define the rules separately to keep track of what and how it was 
        # triggered
        # Define the whole system
        rules = RuleModified({
            (self.left.emer, self.right.emer, self.front.emer) : self.vrot.right,
            (self.left.emer, self.right.emer, self.front.far) : self.vrot.none,
            (self.left.emer, self.right.far) : self.vrot.hright,
            (self.right.emer, self.left.far, self.front.far) : self.vrot.hleft,
            (self.left.near, self.right.far) : self.vrot.right,
            (self.right.near, self.left.far) : self.vrot.left
        })

        # TODO: if the output fo the rules is none, return vrot.none
        return rules(input_data)
    
    def flc_rendevouz(self):
        return None 
    
    def flc_combined(self):
        return None
