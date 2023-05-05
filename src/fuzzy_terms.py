import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def main():
    plot_sets()


def plot_sets():
    # (a)
    percept = ctrl.Antecedent(np.arange(0, 401, 1), 'percept')

    percept['near'] = fuzz.trimf(percept.universe, [0, 0, 55])
    percept['far'] = fuzz.trimf(percept.universe, [48, 100, 150])
    percept['emer'] = fuzz.trimf(percept.universe, [100, 400, 400])

    percept.view()

    # (b)
    dist = ctrl.Antecedent(np.arange(0, 2010, 10), "dist")

    dist["near"] = fuzz.trimf(dist.universe, [0, 0, 20])
    dist["med"] = fuzz.trimf(dist.universe, [10, 100, 125])
    dist["far"] = fuzz.trimf(dist.universe, [100, 2000, 2000])

    dist.view()

    # (c)
    ang = ctrl.Antecedent(np.arange(-3, 3, 0.2), "ang")

    ang["farl"] = fuzz.trimf(ang.universe, [-3, -3, -0.4])
    ang["medl"] = fuzz.trimf(ang.universe, [-1.2, -0.6, 0])
    ang["near"] = fuzz.trimf(ang.universe, [-0.2, 0, 0.2])
    ang["medr"] = fuzz.trimf(ang.universe, [0, 0.6, 1.2])
    ang["farr"] = fuzz.trimf(ang.universe, [0.4, 3, 3])

    ang.view()

    # (d) 
    # TODO: research and represent it better
    vrot = ctrl.Antecedent(np.arange(-2, 2, 0.1), "vrot")

    
    vrot["left"] = fuzz.trapmf(vrot.universe, [-1.5, -1.5, -1.3, -1.3])
    vrot["none"] = fuzz.trapmf(vrot.universe, [0, 0, 0.2, 0.2])
    vrot["right"] = fuzz.trapmf(vrot.universe, [1.5, 1.5, 1.7, 1.7])
    vrot["hright"] = fuzz.trapmf(vrot.universe, [1.8, 1.8, 2, 2])

    vrot.view()

    # (e)
    # TODO: research and represent it better
    vtrans = ctrl.Antecedent(np.arange(0, 100, 1), "vtrans")

    vtrans["stop"] = fuzz.trapmf(vtrans.universe, [0, 0, 2, 2])
    vtrans["low"] = fuzz.trapmf(vtrans.universe, [20, 20, 22, 22])
    vtrans["med"] = fuzz.trapmf(vtrans.universe, [55, 55, 57, 57])
    vtrans["high"] = fuzz.trapmf(vtrans.universe, [98, 98, 100, 100])

    vtrans.view()


if __name__ == "__main__":
    main()