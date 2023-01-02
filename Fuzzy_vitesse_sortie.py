import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
from Fuzzy_vitesseintrinseque import *
from Fuzzy_visibilite import *





# Generate universe variables
#   * Quality and brightnessice on subjective ranges [0, 10]
#   * Tip has a range of [0, 25] in units of percentage points
#max_speed = [0.0 , 0.4, 0.7]
#max_speed = speedint(conso_val,age_val,hate_val)
max_speed = speedint(1,0,1)

#visibility = [0, 0.5, 0.9]
#visibilite(foggy,brightness)

visibility = visibilite(0,1)


def vitesse_finale(visibility_activation, speed_activation) :

    x_finalspeed  = np.arange(0, 1.1, 0.1)
    """ foggy_r = 1-foggy

    x_foggy_r = np.arange(0, 1.1, 0.1)
    x_brightness = np.arange(0, 1.1, 0.1)
    


    # Generate fuzzy membership functions
    foggy_r_lo = fuzz.trimf(x_foggy_r, [0, 0, 0.5])
    foggy_r_md = fuzz.trimf(x_foggy_r, [0, 0.5, 1])
    foggy_r_hi = fuzz.trimf(x_foggy_r, [0.5, 1, 1])
    brightness_lo = fuzz.trimf(x_brightness, [0, 0, 0.5])
    brightness_md = fuzz.trimf(x_brightness, [0, 0.5, 1])
    brightness_hi = fuzz.trimf(x_brightness, [0.5, 1, 1])"""
    finalspeed_lo = fuzz.trimf(x_finalspeed, [0, 0, 0.5])
    finalspeed_md = fuzz.trimf(x_finalspeed, [0, 0.5, 1])
    finalspeed_hi = fuzz.trimf(x_finalspeed, [0.5, 1, 1])
    """""
    # Visualize these universes and membership functions
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(8, 9))

    ax0.plot(x_foggy_r, foggy_r_lo, 'b', linewidth=1.5, label='Bad')
    ax0.plot(x_foggy_r, foggy_r_md, 'g', linewidth=1.5, label='Decent')
    ax0.plot(x_foggy_r, foggy_r_hi, 'r', linewidth=1.5, label='Great')
    ax0.set_title('Foggyness reversed')
    ax0.legend()

    ax1.plot(x_brightness, brightness_lo, 'b', linewidth=1.5, label='Poor')
    ax1.plot(x_brightness, brightness_md, 'g', linewidth=1.5, label='Acceptable')
    ax1.plot(x_brightness, brightness_hi, 'r', linewidth=1.5, label='Amazing')
    ax1.set_title('Brightness')
    ax1.legend()

    ax2.plot(x_visibility, visibility_lo, 'b', linewidth=1.5, label='Low')
    ax2.plot(x_visibility, visibility_md, 'g', linewidth=1.5, label='Medium')
    ax2.plot(x_visibility, visibility_hi, 'r', linewidth=1.5, label='High')
    ax2.set_title('Visibility')
    ax2.legend()

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
    foggy_r_level_lo = fuzz.interp_membership(x_foggy_r, foggy_r_lo, foggy_r)
    foggy_r_level_md = fuzz.interp_membership(x_foggy_r, foggy_r_md, foggy_r)
    foggy_r_level_hi = fuzz.interp_membership(x_foggy_r, foggy_r_hi, foggy_r)

    brightness_level_lo = fuzz.interp_membership(x_brightness, brightness_lo, brightness)
    brightness_level_md = fuzz.interp_membership(x_brightness, brightness_md, brightness)
    brightness_level_hi = fuzz.interp_membership(x_brightness, brightness_hi, brightness)
 """
    # Now we take our rules and apply them. Rule 1 concerns bad food OR brightnessice.
    # The OR operator means we take the maximum of these two.
    active_rule11 = np.fmin(visibility_activation[0], speed_activation[0])
    active_rule12 = np.fmin(visibility_activation[0], speed_activation[1])
    active_rule13 = np.fmin(visibility_activation[0], speed_activation[2])

    active_rule21 = np.fmin(visibility_activation[1], speed_activation[0])
    active_rule22 = np.fmin(visibility_activation[1], speed_activation[1])
    active_rule23 = np.fmin(visibility_activation[1], speed_activation[2])

    active_rule31 = np.fmin(visibility_activation[2], speed_activation[0])
    active_rule32 = np.fmin(visibility_activation[2], speed_activation[1])
    active_rule33 = np.fmin(visibility_activation[2], speed_activation[2])


    # Now we apply this by clipping the top off the corresponding output
    # membership function with `np.fmin`

    finalspeed_activation = []
    active_rule_lo_max = max([active_rule11, active_rule12, active_rule13,active_rule21])

    finalspeed_activation.append(np.fmin(finalspeed_lo, active_rule_lo_max))


    #for active_rule_i in [ active_rule12, active_rule13,active_rule21] :

    #    active_rule_lo_max = np.fmax(active_rule_i,active_rule_lo_max)





    #visibility_activation_lo = active_rule_lo_max

    #visibility_activation_lo1 = np.fmax(active_rule11,active_rule12,visibility_lo)  # removed entirely to 0
    #visibility_activation_lo2 = np.fmax(active_rule13,active_rule21,visibility_lo)  # removed entirely to 0

    #visibility_activation_lo = np.fmax(visibility_activation_lo1, visibility_activation_lo2)  #, visibility_lo)  # removed entirely to 0

    #visibility_activation_md1 = np.fmax(active_rule22,active_rule23,visibility_md)  # removed entirely to 0
    #visibility_activation_md2 = np.fmax(active_rule31)  # removed entirely to 0


    active_rule_md_max = max([active_rule22, active_rule31,active_rule23])

    finalspeed_activation.append(np.fmin(finalspeed_md, active_rule_md_max))



    #active_rule_md_max = np.fmax(visibility_md, active_rule22)

    #for active_rule_j in [active_rule31,active_rule23,] :

    #    active_rule_md_max = np.fmax(active_rule_i,active_rule_lo_max)


    #visibility_activation_md = active_rule_md_max


    #visibility_activation_md = np.fmax(visibility_activation_md1,active_rule31,visibility_md)  # removed entirely to 0


    active_rule_hi_max = max([active_rule32, active_rule33])

    finalspeed_activation.append(np.fmin(finalspeed_hi, active_rule_hi_max))

    for i in range (3):
        finalspeed_activation[i] = max(finalspeed_activation[i])


    #active_rule_hi_max = np.fmax(visibility_md, active_rule32)

    #for active_rule_k in [active_rule33] :

    #    active_rule_hi_max = np.fmax(active_rule_i,active_rule_hi_max)


    #visibility_activation_hi = active_rule_hi_max

    #visibility_activation_hi = np.fmax(active_rule32,active_rule33, visibility_hi)  # removed entirely to 0

    """""
    # For rule 2 we connect acceptable brightnessice to medium tipping
    active_rule2 = np.fmin(foggy_r_level_md, brightness_level_hi)
    #visibility_activation_md = np.fmin(brightness_level_md, visibility_md)

    # For rule 3 we connect high brightnessice OR high food with high tipping
    active_rule3 = np.fmin(foggy_r_level_hi, brightness_level_hi)
    #visibility_activation_hi = np.fmin(active_rule3, visibility_hi)
    visibility0 = np.zeros_like(x_visibility)
      
    # Visualize this
    fig, ax0 = plt.subplots(figsize=(8, 3))

    ax0.fill_between(x_visibility, visibility0, visibility_activation_lo, facecolor='b', alpha=0.7)
    ax0.plot(x_visibility, visibility_lo, 'b', linewidth=0.5, linestyle='--', )
    ax0.fill_between(x_visibility, visibility0, visibility_activation_md, facecolor='g', alpha=0.7)
    ax0.plot(x_visibility, visibility_md, 'g', linewidth=0.5, linestyle='--')
    ax0.fill_between(x_visibility, visibility0, visibility_activation_hi, facecolor='r', alpha=0.7)
    ax0.plot(x_visibility, visibility_hi, 'r', linewidth=0.5, linestyle='--')
    ax0.set_title('Output membership activity')

    # Turn off top/right axes
    for ax in (ax0,):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.tight_layout()
    #plt.show()

    """
    return finalspeed_activation

vvs = vitesse_finale(visibility, max_speed)