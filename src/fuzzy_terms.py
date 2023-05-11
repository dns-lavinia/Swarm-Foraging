from fuzzy import RobotFuzzySystem

def main():
    # Based on the LiDAR sensor readings, divide them into three zones, i.e.
    # left, front and right.
    # To quantize the information from three angular readings into one, the
    # closest distance to the object detected from that number of readings would
    # be considered 
    sys = RobotFuzzySystem()

    print(sys.flc_combined(100, 102, 103, 500, -2))


if __name__ == "__main__":
    main()
