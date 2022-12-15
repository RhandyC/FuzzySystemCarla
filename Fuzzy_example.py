

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz

def Sistemeflou1(foggy_level, brightness_level) :        
    print(foggy_level, brightness_level)
    x_foggy = np.arange(0, 1.05, 0.05)
    x_brightness = np.arange(0, 1.05, 0.05)        
    x_speed  = np.arange(0, 131, 1)        
    foggy_lo = fuzz.trimf(x_foggy, [0, 0, 0.5])        
    foggy_md = fuzz.trimf(x_foggy, [0, 0.5, 1])        
    foggy_hi = fuzz.trimf(x_foggy, [0.5, 1, 1])        
    brightness_lo = fuzz.trimf(x_brightness, [0, 0, 0.5])  
    brightness_md = fuzz.trimf(x_brightness, [0, 0.5, 1])  
    brightness_hi = fuzz.trimf(x_brightness, [0.5, 1, 1])        
    speed_lo = fuzz.trimf(x_speed, [0, 0, 65])        
    speed_md = fuzz.trimf(x_speed, [0, 65, 130])        
    speed_hi = fuzz.trimf(x_speed, [65, 130, 130])       
    
    # fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(8, 9))        
    # ax0.plot(x_foggy, foggy_lo, 'b', linewidth=1.5, label='Low')        
    # ax0.plot(x_foggy, foggy_md, 'g', linewidth=1.5, label='Medium')
    # ax0.plot(x_foggy, foggy_hi, 'r', linewidth=1.5, label='High')
    # ax0.set_title('Foggy level')
    # ax0.legend()

    # ax1.plot(x_brightness, brightness_lo, 'b', linewidth=1.5, label='Low')
    # ax1.plot(x_brightness, brightness_md, 'g', linewidth=1.5, label='Medium')
    # ax1.plot(x_brightness, brightness_hi, 'r', linewidth=1.5, label='High')
    # ax1.set_title('Brightness level')
    # ax1.legend()

    # ax2.plot(x_speed, speed_lo, 'b', linewidth=1.5, label='Low')
    # ax2.plot(x_speed, speed_md, 'g', linewidth=1.5, label='Medium')
    # ax2.plot(x_speed, speed_hi, 'r', linewidth=1.5, label='High')
    # ax2.set_title('Speed Level')
    # ax2.legend()

    # for ax in (ax0, ax1, ax2):
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.get_xaxis().tick_bottom()
    #     ax.get_yaxis().tick_left()

    # plt.tight_layout()
    # plt.show()
    
    # We need the activation of our fuzzy membership functions at these values.
    # The exact values 6.5 and 9.8 do not exist on our universes...
    # This is what fuzz.interp_membership exists for!
    current_foggy_level = foggy_level
    current_brightness_level = brightness_level
    foggy_level_lo = fuzz.interp_membership(x_foggy, foggy_lo, current_foggy_level)
    foggy_level_md = fuzz.interp_membership(x_foggy, foggy_md, current_foggy_level)
    foggy_level_hi = fuzz.interp_membership(x_foggy, foggy_hi, current_foggy_level)

    brightness_level_lo = fuzz.interp_membership(x_brightness, brightness_lo, current_brightness_level)
    brightness_level_md = fuzz.interp_membership(x_brightness, brightness_md, current_brightness_level)
    brightness_level_hi = fuzz.interp_membership(x_brightness, brightness_hi, current_brightness_level)


    # Now we take our rules and apply them. Rule 1 concerns bad food OR service.
    # The OR operator means we take the maximum of these two.
    active_rule1 = np.fmin(foggy_level_lo, brightness_level_hi)
    active_rule2 = np.fmin(foggy_level_lo, brightness_level_md)
    active_rule3 = np.fmin(foggy_level_lo, brightness_level_lo)

    active_rule4 = np.fmin(foggy_level_md, brightness_level_hi)
    active_rule5 = np.fmin(foggy_level_md, brightness_level_md)
    active_rule6 = np.fmin(foggy_level_md, brightness_level_lo)

    active_rule7 = np.fmin(foggy_level_hi, brightness_level_hi)
    active_rule8 = np.fmin(foggy_level_hi, brightness_level_md)
    active_rule9 = np.fmin(foggy_level_hi, brightness_level_lo)

    # # Now we apply this by clipping the top off the corresponding output
    # # membership function with `np.fmin`

    speed_activation_hi = np.fmin(max(active_rule1, active_rule2), speed_hi )  # removed entirely to 0
    speed_activation_md = np.fmin(active_rule3, speed_md)
    speed_activation_lo = np.fmin(max(active_rule3, active_rule4, active_rule5, active_rule6 ,active_rule7 ,active_rule8, active_rule9), speed_lo)

    speed0 = np.zeros_like(x_speed)

    # Visualize this
    # fig, ax0 = plt.subplots(figsize=(8, 3))

    # ax0.fill_between(x_speed, speed0, speed_activation_lo, facecolor='b', alpha=0.7)
    # ax0.plot(x_speed, speed_lo, 'b', linewidth=0.5, linestyle='--', )
    # ax0.fill_between(x_speed, speed0, speed_activation_md, facecolor='g', alpha=0.7)
    # ax0.plot(x_speed, speed_md, 'g', linewidth=0.5, linestyle='--')
    # ax0.fill_between(x_speed, speed0, speed_activation_hi, facecolor='r', alpha=0.7)
    # ax0.plot(x_speed, speed_hi, 'r', linewidth=0.5, linestyle='--')
    # ax0.set_title('Output membership activity')

    # # Turn off top/right axes
    # for ax in (ax0,):
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.get_xaxis().tick_bottom()
    #     ax.get_yaxis().tick_left()

    # plt.tight_layout()

    # plt.show()


    # Aggregate all three output membership functions together
    aggregated = np.fmax(speed_activation_lo,
                        np.fmax(speed_activation_md, speed_activation_hi))

    # Calculate defuzzified result
    speed = fuzz.defuzz(x_speed, aggregated, 'centroid')
    speed_activation = fuzz.interp_membership(x_speed, aggregated, speed)  # for plot
    #print(speed)

    # Visualize this
    # fig, ax0 = plt.subplots(figsize=(8, 3))

    # ax0.plot(x_speed, speed_lo, 'b', linewidth=0.5, linestyle='--', )
    # ax0.plot(x_speed, speed_md, 'g', linewidth=0.5, linestyle='--')
    # ax0.plot(x_speed, speed_hi, 'r', linewidth=0.5, linestyle='--')
    # ax0.fill_between(x_speed, speed0, aggregated, facecolor='Orange', alpha=0.7)
    # ax0.plot([speed, speed], [0, speed_activation], 'k', linewidth=1.5, alpha=0.9)
    # ax0.set_title('Aggregated membership and result (line)')

    # # Turn off top/right axes
    # for ax in (ax0,):
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.get_xaxis().tick_bottom()
    #     ax.get_yaxis().tick_left()

    # plt.tight_layout()
    # plt.show()
    return (speed)

def Sistemeflou2(foggy_level, brightness_level) : 
    x_foggy = np.arange(0, 1.05, 0.01)
    x_brightness = np.arange(0, 1.05, 0.01)        
    x_visibility  = np.arange(0, 1.05, 0.01)        
    foggy_lo = fuzz.trimf(x_foggy, [0, 0, 0.42])        
    foggy_md = fuzz.trimf(x_foggy, [0, 0.5, 0.92])        
    foggy_hi = fuzz.trimf(x_foggy, [0.58, 1, 1])        
    brightness_lo = fuzz.trimf(x_brightness, [0, 0, 1])  
    brightness_hi = fuzz.trimf(x_brightness, [0, 1, 1])        
    visibility_lo = fuzz.trimf(x_visibility, [0, 0, 0.42])        
    visibility_md = fuzz.trimf(x_visibility, [0, 0.5, 0.92])        
    visibility_hi = fuzz.trimf(x_visibility, [0.58, 1, 1])      

    current_foggy_level = foggy_level
    current_brightness_level = brightness_level
    foggy_level_lo = fuzz.interp_membership(x_foggy, foggy_lo, current_foggy_level)
    foggy_level_md = fuzz.interp_membership(x_foggy, foggy_md, current_foggy_level)
    foggy_level_hi = fuzz.interp_membership(x_foggy, foggy_hi, current_foggy_level)

    brightness_level_lo = fuzz.interp_membership(x_brightness, brightness_lo, current_brightness_level)
    brightness_level_hi = fuzz.interp_membership(x_brightness, brightness_hi, current_brightness_level)

     # Now we take our rules and apply them. Rule 1 concerns bad food OR service.
    # The OR operator means we take the maximum of these two.
    active_rule1 = np.fmin(foggy_level_lo, brightness_level_hi)
    active_rule2 = np.fmin(foggy_level_lo, brightness_level_lo)
    active_rule3 = np.fmin(foggy_level_md, brightness_level_hi)
    active_rule4 = np.fmin(foggy_level_md, brightness_level_lo)
    active_rule5 = np.fmin(foggy_level_hi, brightness_level_hi)
    active_rule6 = np.fmin(foggy_level_hi, brightness_level_lo)


    visibility_activation_hi = np.fmin(active_rule1, visibility_hi )  # removed entirely to 0
    visibility_activation_md = np.fmin(active_rule2, visibility_md)
    visibility_activation_lo = np.fmin(max(active_rule3, active_rule4, active_rule5, active_rule6), visibility_lo)

    # Sortie floue
    print("Hight",max(visibility_activation_hi))
    print("Medium",max(visibility_activation_md))
    print("Low",max(visibility_activation_lo))

    visibility0 = np.zeros_like(x_visibility)

    # Aggregate all three output membership functions together
    aggregated = np.fmax(visibility_activation_lo,
                        np.fmax(visibility_activation_md, visibility_activation_hi))

    # Calculate defuzzified result
    visibility = fuzz.defuzz(x_visibility, aggregated, 'centroid')
    visibility_activation = fuzz.interp_membership(x_visibility, aggregated, visibility)  # for plot

    # Visualize this
    # fig, ax0 = plt.subplots(figsize=(8, 3))

    # x_speed= x_visibility

    # ax0.plot(x_speed, visibility_lo, 'b', linewidth=0.5, linestyle='--', )
    # ax0.plot(x_speed, visibility_md, 'g', linewidth=0.5, linestyle='--')
    # ax0.plot(x_speed, visibility_hi, 'r', linewidth=0.5, linestyle='--')
    # ax0.fill_between(x_speed, visibility0, aggregated, facecolor='Orange', alpha=0.7)
    # ax0.plot([visibility, visibility], [0, visibility_activation], 'k', linewidth=1.5, alpha=0.9)
    # ax0.set_title('Aggregated membership and result (line)')

    # # Turn off top/right axes
    # for ax in (ax0,):
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.get_xaxis().tick_bottom()
    #     ax.get_yaxis().tick_left()

    # plt.tight_layout()
    # plt.show()

    return (visibility)


print(Sistemeflou2(0.29,0.509))

