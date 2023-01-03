import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt




# Generate universe variables
#   * Quality and brightnessice on subjective ranges [0, 10]
#   * Tip has a range of [0, 25] in units of percentage points
ltiv  = [0.1, 0.5,0]
ativ = [0.9,0.3,0.0]
rtiv = [0.0,0.4,0.2]          #Hâte du chauffeur
def manoeuvres(ltiv,ativ,rtiv) :
    """
    age_r_val = 1-age_val

    x_conso = np.arange(0,1.1,0.1)
    x_age_r = np.arange(0, 1.1, 0.1)
    x_hate = np.arange(0, 1.1, 0.1)
    x_speed = np.arange(0, 1.1, 0.1)


    # Generate fuzzy membership functions
    conso = []
    conso.append (fuzz.trimf(x_conso, [0, 0, 0.5]))
    conso.append (fuzz.trimf(x_conso, [0 , 0.5, 1]))
    conso.append (fuzz.trimf(x_conso, [0.5, 1, 1]))

    age_r = []
    age_r.append (fuzz.trimf(x_age_r, [0, 0, 0.5]))
    age_r.append (fuzz.trimf(x_age_r, [0 , 0.5, 1]))
    age_r.append (fuzz.trimf(x_age_r, [0.5, 1, 1]))

    hate = []
    hate.append (fuzz.trimf(x_hate, [0, 0, 0.5]))
    hate.append(fuzz.trimf(x_hate, [0 , 0.5, 1]))
    hate.append(fuzz.trimf(x_hate, [0.5, 1, 1]))

    speed=[]
    speed.append(fuzz.trimf(x_speed, [0, 0, 0.5]))
    speed.append(fuzz.trimf(x_speed, [0 , 0.5, 1]))
    speed.append(fuzz.trimf(x_speed, [0.5, 1, 1]))

    # Visualize these universes and membership functions
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(8, 9))

    ax0.plot(x_conso, conso[0], 'b', linewidth=1.5, label='Bad')
    ax0.plot(x_conso, conso[1], 'g', linewidth=1.5, label='Decent')
    ax0.plot(x_conso, conso[2], 'r', linewidth=1.5, label='Great')
    ax0.set_title('Conso')
    ax0.legend()

    ax1.plot(x_age_r, age_r[0], 'b', linewidth=1.5, label='Bad')
    ax1.plot(x_age_r, age_r[1], 'g', linewidth=1.5, label='Decent')
    ax1.plot(x_age_r, age_r[2], 'r', linewidth=1.5, label='Great')
    ax1.set_title('Age reversed')
    ax1.legend()

    ax2.plot(x_hate, hate[0], 'b', linewidth=1.5, label='Low')
    ax2.plot(x_hate, hate[1], 'g', linewidth=1.5, label='Medium')
    ax2.plot(x_hate, hate[2], 'r', linewidth=1.5, label='High')
    ax2.set_title('Hâte')
    ax2.legend()

    # ax3.plot(x_speed, speed[0], 'b', linewidth=1.5, label='Poor')
    # ax3.plot(x_speed, speed[1], 'g', linewidth=1.5, label='Acceptable')
    # ax3.plot(x_speed, speed[2], 'r', linewidth=1.5, label='Amazing')
    # ax3.set_title('Vitesse intrinseque')
    # ax3.legend()



    # Turn off top/right axes
    for ax in (ax0, ax1, ax2):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

    plt.tight_layout()

    # We need the activation of our fuzzy membership functions at these values.
    # The exact values 6.5 and 9.8 do not exist on our universes...
    # This is what fuzz.interp_membership exists for!

    conso_level = []
    age_r_level = []
    hate_level = []


    for i in range(3):

        conso_level.append(fuzz.interp_membership(x_conso, conso[i], conso_val))
        age_r_level.append(fuzz.interp_membership(x_age_r, age_r[i], age_r_val))
        hate_level.append(fuzz.interp_membership(x_hate, hate[i], hate_val))



    # foggy_r_level_lo = fuzz.interp_membership(x_conso, conso_lo, foggy_r)
    # foggy_r_level_md = fuzz.interp_membership(x_conso, conso_md, foggy_r)
    # foggy_r_level_hi = fuzz.interp_membership(x_conso, conso_hi, foggy_r)


    # foggy_r_level = []
    # foggy_r_level.append(foggy_r_level_lo)
    # foggy_r_level.append(foggy_r_level_md)
    # foggy_r_level.append(foggy_r_level_hi)


    # brightness_level_lo = fuzz.interp_membership(x_hate, hate_lo, hate)
    # brightness_level_md = fuzz.interp_membership(x_hate, hate_md, hate)
    # brightness_level_hi = fuzz.interp_membership(x_hate, hate_hi, hate)

    # brightness_level = []
    # brightness_level.append(brightness_level_lo)
    # brightness_level.append(brightness_level_md)
    # brightness_level.append(brightness_level_hi)

    # Now we take our rules and apply them. Rule 1 concerns bad food OR brightnessice.
    # The OR operator means we take the maximum of these two.

    #i=0
    j=0
    #acitve_rule = [[0,0,0,0,0,0,0,0,0,0,0] * 3 for i in range(3)]
    #acitve_rule = [[0] * 11 for i in range(3)]
    #active_rule = [[[0]*11,[0]*11,[0]*11]*3]
    #,[[],[],[]],[[],[],[],[]]]
    """
    active_rule = [[[0 for k in range(11)] for j in range(3)] for i in range(3)]

    #active_rule= [[],[],[]]
    
    for i in range (3) :
        for j in range (3):
            for k in range (3):
                active_rule[i][j][k] = np.fmin(ltiv[i], ativ[j])
                active_rule[i][j][k] = np.fmin(active_rule[i][j][k],rtiv[k])

                #print(active_rule)
                #j +=1
    

    manvr =[0,0,0]

    indexes_ovt = ((2,0,0),(2,0,1),(2,0,2),(2,1,0),(2,1,1),(2,1,2),(2,2,0),(2,2,1),(2,2,2),(1,0,0),(1,1,0),(1,1,1))
    active_rules_ovt = [active_rule[i][j][k] for (i,j,k) in indexes_ovt]
    OVT = max(max(active_rule[0]))

    #manvr.append(np.fmin(speed[0], active_rule_lo_max))

    KL = max(max(active_rule[1]))

    #manvr.append(np.fmin(speed[1], active_rule_md_max))

    YLD = max(max(active_rule[2]))

    #manvr.append(np.fmin(speed[2], active_rule_hi_max))

    #for i in range (3):
    #    speed_activation[i] = max(speed_activation[i])

    manvr= [OVT,KL,YLD]
    
    return manvr

man1 =manoeuvres(ltiv, ativ,rtiv)

man2 =manoeuvres(0.5, ativ,rtiv)