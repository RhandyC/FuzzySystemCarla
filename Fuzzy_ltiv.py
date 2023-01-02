import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt


# ltiv = [lbacktiv, lfronttiv]

ltiv_val = [0.7,0.6]
lltype = 1
def ltiv(ltiv_val, lltype) :

    ltiv_min = min(ltiv_val)

    x_ltiv = np.arange(0,1.1,0.1)
    x_dll = np.arange(0, 1.1, 0.1) #Degre Liberté Left (lane)

    # Generate fuzzy membership functions
    ltiv = []
    ltiv.append (fuzz.trapmf(x_ltiv, [0, 0, 0,0.4]))
    ltiv.append (fuzz.trapmf(x_ltiv, [0.2 , 0.3,0.6, 0.8]))
    ltiv.append (fuzz.trapmf(x_ltiv, [0.5, 0.8,1, 1]))

    dll=[]
    dll.append(fuzz.trapmf(x_dll, [0, 0, 0, 0.4]))
    dll.append(fuzz.trapmf(x_dll, [0.2, 0.3,0.6, 0.8]))
    dll.append(fuzz.trapmf(x_dll, [0.5, 0.8,1, 1]))


    # Visualize these universes and membership functions
    fig, (ax0, ax1) = plt.subplots(nrows=2, figsize=(8, 9))

    ax0.plot(x_ltiv, ltiv[0], 'b', linewidth=1.5, label='Danger')
    ax0.plot(x_ltiv, ltiv[1], 'g', linewidth=1.5, label='Decent')
    ax0.plot(x_ltiv, ltiv[2], 'r', linewidth=1.5, label='Safe')
    ax0.set_title('Left TIV')
    ax0.legend()

    ax1.plot(x_dll, dll[0], 'b', linewidth=1.5, label='Danger')
    ax1.plot(x_dll, dll[1], 'g', linewidth=1.5, label='Decent')
    ax1.plot(x_dll, dll[2], 'r', linewidth=1.5, label='Safe')
    ax1.set_title('Degré de liberté Left')
    ax1.legend()


    ltiv_level = []
    active_rule = [0,0,0]

    for i in range(3):

        ltiv_level.append(fuzz.interp_membership(x_ltiv, ltiv[i], ltiv_min))
        active_rule[i] = np.fmin(ltiv_level[i],lltype)
        
    ldl_activation = [] #Left Degre de liberte

    ldl_activation.append( max(np.fmin(dll[0], active_rule[0])))

    ldl_activation.append( max(np.fmin(dll[1], active_rule[1])))

    ldl_activation.append(max(np.fmin(dll[2], active_rule[2])))

    ldl_activation2 = min(ltiv_min, lltype)

    return ldl_activation2

left_tiv = ltiv(ltiv_val, lltype)

left_ti = ltiv(ltiv_val, lltype)
