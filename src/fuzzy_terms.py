from fuzzylogic.functions import triangular, linear

from fuzzy import DomainModified, RuleModified, singleton
from flc import FuzzySystem

def draft():
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


def main():
    # Based on the LiDAR sensor readings, divide them into three zones, i.e.
    # left, front and right.
    # To quantize the information from three angular readings into one, the
    # closest distance to the object detected from that number of readings would
    # be considered 
    sys = FuzzySystem()

    print(sys.flc_avoidance(100, 100, 100))


if __name__ == "__main__":
    main()
