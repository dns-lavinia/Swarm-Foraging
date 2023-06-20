from fuzzy import RobotFuzzySystem

# Run this python script to view the fuzzy sets
def main():
    sys = RobotFuzzySystem()

    sys.left.view()
    sys.ang.view()
    sys.dist.view()
    sys.vrot.view()
    sys.vtrans.view()


if __name__ == "__main__":
    main()
