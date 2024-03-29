"""
This module is made up of 5 fuzzy systems and 3 fuzzy arithmetic operations, 
the objective of this project is to be able to command a car at a tactical 
level. This module was developped by Rhandy CARDENAS and Loic TCHAMGOUE. 
The reference library used was skfuzzy https://pythonhosted.org/scikit-fuzzy/
"""

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz

# ----------------------------------------------------------------------------------
# Modules fuzzyfication
# ----------------------------------------------------------------------------------
# In order to make more realistic our system we decided to fuzzyfy our inputs, then
# do a arithmetic fuzzy calculation. The following functions serve this purpose
#
#---------------------

def distanceFuzzification(distance,range = 1.0):
    # x_distance = np.arange(0, 100.0, 0.01)
    # fuzzy_distance = fuzz.trapmf(x_distance, [distance - range, distance - range/2.0, distance + range/2.0, distance + range])
    # plt.plot(x_distance, fuzzy_distance, 'b', linewidth=0.5, linestyle='--', )
    # plt.show()
    return [distance - range, distance - range/2.0, distance + range/2.0, distance + range]

def speedFuzzification(speed,range = 1.0):
    # x_speed = np.arange(0, 20.0, 0.01)
    # fuzzy_speed = fuzz.trapmf(x_speed, [speed - range, speed - range/2.0, speed + range/2.0, speed + range])
    # plt.plot(x_speed, fuzzy_speed, 'b', linewidth=0.5, linestyle='--', )
    # plt.show()
    return [speed - range, speed - range/2.0, speed + range/2.0, speed + range] 

# ----------------------------------------------------------------------------------
# Modules CAF
# ----------------------------------------------------------------------------------
# One of the necessary inputs for the following systems is the intervehicular
# time that will be calculated as follows. Then we need to choose the most 
# restrictive TIV in other words the smallest.
#
#-----------------------------------------------------------------------------------

def caf_TIV(speed, distance):
    if( (speed[1]+speed[2])/2 < 0 ):
            return [10.0,10.0,10.0,10.0]
    x_tiv = np.arange(0, 10.1, 0.01)
    ### Calcul directe
    fuzzy_tiv = fuzz.trapmf(x_tiv, [distance[0]/speed[3],distance[1]/speed[2],distance[2]/speed[1] ,distance[3]/speed[0]])

    ### Classes TIV
    tiv_lo = fuzz.trapmf(x_tiv, [0, 0, 1.0, 1.5])        
    tiv_md = fuzz.trapmf(x_tiv, [1.0, 2.0, 3.0, 4.0])        
    tiv_hi = fuzz.trapmf(x_tiv, [3.5, 4.0, 10.0, 10.0])       

    ## Level classes 
    level_tiv_lo = max(np.fmin(tiv_lo, fuzzy_tiv))
    level_tiv_md = max(np.fmin(tiv_md, fuzzy_tiv))
    level_tiv_hi = max(np.fmin(tiv_hi, fuzzy_tiv))

    # print("Low: ", level_tiv_lo, " Medium: ", level_tiv_md, " High: ", level_tiv_hi)
    # plt.plot(x_tiv, tiv_lo, 'g', linewidth=0.5, linestyle='--')                
    # plt.plot(x_tiv, tiv_md, 'r', linewidth=0.5, linestyle='--')                
    # plt.plot(x_tiv, tiv_hi, 'c', linewidth=0.5, linestyle='--')                
    # plt.plot(x_tiv, fuzzy_tiv, 'b', linewidth=0.5, linestyle='--')                
    # plt.show()
    return [distance[0]/speed[3],distance[1]/speed[2],distance[2]/speed[1] ,distance[3]/speed[0], fuzzy_tiv]

def minTIV(tiv1, tiv2):
    x_tiv = np.arange(0, 10.1, 0.01)
    ### Calcul directe
    vector_trapmf = [min(tiv1[0], tiv2[0]),min(tiv1[1], tiv2[1]),min(tiv1[2], tiv2[2]),min(tiv1[3], tiv2[3])]
    fuzzy_tiv = fuzz.trapmf(x_tiv , vector_trapmf)
    # plt.plot(x_tiv, fuzzy_tiv, 'b', linewidth=0.5, linestyle='--', )
    # plt.show()
    return vector_trapmf

# ----------------------------------------------------------------------------------
# First fuzzy system - Visibility
# ----------------------------------------------------------------------------------
# The main objective of this system is to provide a degree of visibility according to 
# the information retrieved from the simulation environment.
#
# Inputs (Crisp values):
#           - Fogginess 
#           - Brightness 
# Outputs (Crisp value):
#           - Visibility 
#------------------------------------------------------------------------------------

def Visibility(foggy_level, brightness_level) : 
    x_foggy = np.arange(0, 1.05, 0.01)
    x_brightness = np.arange(0, 1.05, 0.01)        
    x_visibility  = np.arange(0, 1.05, 0.01)        
    foggy_lo = fuzz.trimf(x_foggy, [0, 0, 0.25])        
    foggy_md = fuzz.trimf(x_foggy, [0.1, 0.25, 0.4])        
    foggy_hi = fuzz.trimf(x_foggy, [0.3, 1, 1])        
    brightness_lo = fuzz.trimf(x_brightness, [0, 0, 0.6])  
    brightness_hi = fuzz.trimf(x_brightness, [0.4, 1, 1])        
    visibility_lo = fuzz.trimf(x_visibility, [0, 0, 0.4])        
    visibility_md = fuzz.trimf(x_visibility, [0.3, 0.5, 0.7])        
    visibility_hi = fuzz.trimf(x_visibility, [0.6, 1, 1])      

    current_foggy_level = foggy_level
    current_brightness_level = brightness_level
    foggy_level_lo = fuzz.interp_membership(x_foggy, foggy_lo, current_foggy_level)
    foggy_level_md = fuzz.interp_membership(x_foggy, foggy_md, current_foggy_level)
    foggy_level_hi = fuzz.interp_membership(x_foggy, foggy_hi, current_foggy_level)

    brightness_level_lo = fuzz.interp_membership(x_brightness, brightness_lo, current_brightness_level)
    brightness_level_hi = fuzz.interp_membership(x_brightness, brightness_hi, current_brightness_level)

    # Rules
    active_rule1 = np.fmin(foggy_level_lo, brightness_level_hi)
    active_rule2 = np.fmin(foggy_level_lo, brightness_level_lo)
    active_rule3 = np.fmin(foggy_level_md, brightness_level_hi)
    active_rule4 = np.fmin(foggy_level_md, brightness_level_lo)
    active_rule5 = np.fmin(foggy_level_hi, brightness_level_hi)
    active_rule6 = np.fmin(foggy_level_hi, brightness_level_lo)

    visibility_activation_hi = np.fmin(active_rule1, visibility_hi )  # removed entirely to 0
    visibility_activation_md = np.fmin(max(active_rule2, active_rule3), visibility_md)
    visibility_activation_lo = np.fmin(max(active_rule4, active_rule5, active_rule6), visibility_lo)

    # Sortie floue, vector classes
    visibility_fuzzy = [max(visibility_activation_lo), max(visibility_activation_md), max(visibility_activation_hi)]

    print("Fuzzy Visibility : ", visibility_fuzzy)

    visibility0 = np.zeros_like(x_visibility)

    # Aggregate all three output membership functions together
    aggregated = np.fmax(visibility_activation_lo,
                        np.fmax(visibility_activation_md, visibility_activation_hi))

    # Calculate defuzzified result
    visibility = fuzz.defuzz(x_visibility, aggregated, 'centroid')
    visibility_activation = fuzz.interp_membership(x_visibility, aggregated, visibility)  # for plot

    print("Visibility: ", visibility)

    # Visualize this
    fig, ax0 = plt.subplots(figsize=(8, 3))

    x_speed= x_visibility

    ax0.plot(x_speed, visibility_lo, 'b', linewidth=0.5, linestyle='--')
    ax0.plot(x_speed, visibility_md, 'g', linewidth=0.5, linestyle='--')
    ax0.plot(x_speed, visibility_hi, 'r', linewidth=0.5, linestyle='--')
    ax0.fill_between(x_speed, visibility0, aggregated, facecolor='Orange', alpha=0.7)
    ax0.plot([visibility, visibility], [0, visibility_activation], 'k', linewidth=1.5, alpha=0.9)
    ax0.set_title('Aggregated membership and result (line) -- Visibility')

    # Turn off top/right axes
    for ax in (ax0,):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

    plt.tight_layout()
    plt.show()

    return (visibility)

# ----------------------------------------------------------------------------------
# Second fuzzy system - Intrinsic Speed
# ----------------------------------------------------------------------------------
# The main objective of this system is to obtain the speed at which a 
# car could move according to its features and the way of driving.
#
# Inputs (Crisp values):
#           - Fuel consumption 
#           - Age of vehicle
#           - Driver's behavior 
# Outputs (Crisp value):
#           - Intrinsic speed
#------------------------------------------------------------------------------------

def Vitesseintrinseque(conso_val, age_r_val, hate_val) : 
    # Domain of variables
    x_conso = np.arange(0, 25.1, 0.1)
    x_age_r = np.arange(0, 25.1, 0.1)
    x_hate = np.arange(0, 1.1, 0.1)
    x_speed = np.arange(0, 200.1, 0.1)
    
    # Generate fuzzy membership functions using arrays (faster)
    conso = []
    conso.append (fuzz.trimf(x_conso, [0, 0, 12.5]))
    conso.append (fuzz.trimf(x_conso, [0 , 12.5, 25]))
    conso.append (fuzz.trimf(x_conso, [12.5, 25, 25]))

    age_r = []
    age_r.append (fuzz.trimf(x_age_r, [0, 0, 12.5]))
    age_r.append (fuzz.trimf(x_age_r, [0 , 12.5, 25]))
    age_r.append (fuzz.trimf(x_age_r, [12.5, 25, 25]))

    hate = []
    hate.append (fuzz.trimf(x_hate, [0, 0, 0.5]))
    hate.append(fuzz.trimf(x_hate, [0 , 0.5, 1]))
    hate.append(fuzz.trimf(x_hate, [0.5, 1, 1]))

    speed=[]
    speed.append(fuzz.trimf(x_speed, [0, 0, 100]))
    speed.append(fuzz.trimf(x_speed, [0 , 100, 200]))
    speed.append(fuzz.trimf(x_speed, [100, 200, 200]))

    # Interpretation of crisp value inside the membership functions using arrays 
    conso_level = []
    age_r_level = []
    hate_level = []

    for i in range(3):
        conso_level.append(fuzz.interp_membership(x_conso, conso[i], conso_val))
        age_r_level.append(fuzz.interp_membership(x_age_r, age_r[i], age_r_val))
        hate_level.append(fuzz.interp_membership(x_hate, hate[i], hate_val))

    # Rules using arrays 
    active_rule = [[[0 for k in range(3)] for j in range(3)] for i in range(3)]

    for i in range (3) :
        for j in range (3):
            for k in range (3):
                active_rule[i][j][k] = np.fmin(conso_level[i], age_r_level[j])
                active_rule[i][j][k] = np.fmin(active_rule[i][j][k],hate_level[k])

    # 10 rules
    active_rule_lo_max = max(   active_rule[0][1][0],
                                active_rule[0][1][1],
                                active_rule[0][1][2],
                                active_rule[0][2][0],
                                active_rule[0][2][1],
                                active_rule[0][2][2],
                                active_rule[1][1][0],
                                active_rule[1][2][0],
                                active_rule[1][2][1],
                                active_rule[1][2][2]   )
    # Triggering of rules
    speed_activation_lo = np.fmin(speed[0], active_rule_lo_max)

    # 13 rules
    active_rule_md_max = max(   active_rule[0][0][0],
                                active_rule[0][0][1],
                                active_rule[0][0][2],
                                active_rule[1][0][0],
                                active_rule[1][0][1],
                                active_rule[1][1][1],
                                active_rule[1][1][2],
                                active_rule[2][0][0],
                                active_rule[2][1][0],
                                active_rule[2][1][1],
                                active_rule[2][2][0],
                                active_rule[2][2][1],
                                active_rule[2][2][2]     )
    # Triggering of rules
    speed_activation_md = np.fmin(speed[1], active_rule_md_max)

    # 4 rules
    active_rule_hi_max = max(   active_rule[1][0][2],
                                active_rule[2][0][1],
                                active_rule[2][0][2],
                                active_rule[2][1][2]  )
    # Triggering of rules
    speed_activation_hi = np.fmin(speed[2], active_rule_hi_max)

    # Aggregate all three output membership functions together
    aggregated = np.fmax(speed_activation_lo,
                        np.fmax(speed_activation_md, speed_activation_hi))
    
    # Calculate defuzzified result
    intrinsicSpeed = fuzz.defuzz(x_speed, aggregated, 'centroid')

    # Fuzzy ouput if needed
    intrinsequeSpeed_fuzzy = [max(speed_activation_lo), max(speed_activation_md), max(speed_activation_hi)]
    print("Fuzzy Intrinsic Speed : ",intrinsequeSpeed_fuzzy)
    print("Intrinsic Speed : ",intrinsicSpeed)

    # Visualize this
    fig, ax0 = plt.subplots(figsize=(8, 3))
    
    speed0 = np.zeros_like(x_speed)
    speed_activation = fuzz.interp_membership(x_speed, aggregated, intrinsicSpeed)  # for plot

    ax0.plot(x_speed, speed[0], 'b', linewidth=0.5, linestyle='--')
    ax0.plot(x_speed, speed[1], 'g', linewidth=0.5, linestyle='--')
    ax0.plot(x_speed, speed[2], 'r', linewidth=0.5, linestyle='--')
    ax0.fill_between(x_speed, speed0, aggregated, facecolor='Orange', alpha=0.7)
    ax0.plot([intrinsicSpeed, intrinsicSpeed], [0, speed_activation], 'k', linewidth=1.5, alpha=0.9)
    ax0.set_title('Aggregated membership and result (line) -- Intrinsic Speed')

    # Turn off top/right axes
    for ax in (ax0,):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

    plt.tight_layout()
    plt.show()

    return intrinsicSpeed

# ----------------------------------------------------------------------------------
# Third fuzzy system - Accesible Speed
# ----------------------------------------------------------------------------------
# The main objective of this module is to combine the visibility and the 
# limit speed of the vehicle to obtain a coherent speed in the driving context.
#
# Inputs (Crisp values):
#           - Intrinsic Speed
#           - Visibility
# Outputs (Crisp value):
#           - Accessible speed
#------------------------------------------------------------------------------------

def AccessibleSpeed(intSpeed_val, visibility_val) : 
    # Domain of variables
    x_visibility = np.arange(0,1.1,0.1)
    x_intSpeed = np.arange(0, 200.1, 0.1)
    x_accessibleSpeed = np.arange(0, 200.1, 0.1)

    # Generate fuzzy membership functions using arrays (faster)
    visibility  = []
    visibility.append (fuzz.trimf(x_visibility, [0, 0, 0.5]))
    visibility.append (fuzz.trimf(x_visibility, [0 , 0.5, 1]))
    visibility.append (fuzz.trimf(x_visibility, [0.5, 1, 1]))

    intSpeed = []
    intSpeed.append(fuzz.trimf(x_intSpeed, [0, 0, 100]))
    intSpeed.append(fuzz.trimf(x_intSpeed, [0 , 100, 200]))
    intSpeed.append(fuzz.trimf(x_intSpeed, [100, 200, 200]))

    accessibleSpeed = []
    accessibleSpeed.append(fuzz.trimf(x_accessibleSpeed, [0, 0, 100]))
    accessibleSpeed.append(fuzz.trimf(x_accessibleSpeed, [0 , 100, 200]))
    accessibleSpeed.append(fuzz.trimf(x_accessibleSpeed, [100, 200, 200]))

    # Interpretation of crisp value inside the membership functions using arrays 
    visibility_level = []
    intSpeed_level = []
    accessibleSpeed_level = []

    for i in range(3):
        visibility_level.append(fuzz.interp_membership(x_visibility, visibility[i], visibility_val))
        intSpeed_level.append(fuzz.interp_membership(x_intSpeed, intSpeed[i], intSpeed_val))

    # Rules using arrays 
    active_rule = [[0 for k in range(3)] for j in range(3)]

    for i in range (3) :
        for j in range (3):
            active_rule[i][j] = np.fmin(visibility_level[i], intSpeed_level[j])

    # 6 rules
    active_rule_lo_max = max(   active_rule[0][0],
                                active_rule[0][1],
                                active_rule[0][2],
                                active_rule[1][0],
                                active_rule[1][1],
                                active_rule[2][0]   )

    # Triggering of rules
    speed_activation_lo = np.fmin(accessibleSpeed[0], active_rule_lo_max)

    # 2 rules
    active_rule_md_max = max(   active_rule[1][2],
                                active_rule[2][1]   )

    # Triggering of rules
    speed_activation_md = np.fmin(accessibleSpeed[1], active_rule_md_max)

    # 1 rules
    active_rule_hi_max = active_rule[2][2]

    # Triggering of rules
    speed_activation_hi = np.fmin(accessibleSpeed[2], active_rule_hi_max)

    # Aggregate all three output membership functions together
    aggregated = np.fmax(speed_activation_lo,
                        np.fmax(speed_activation_md, speed_activation_hi))
    
    # Calculate defuzzified result
    accessibleSpeed_output = fuzz.defuzz(x_accessibleSpeed, aggregated, 'centroid')

    # Fuzzy ouput if needed
    intrinsequeSpeed_fuzzy = [max(speed_activation_lo), max(speed_activation_md), max(speed_activation_hi)]

    print("Fuzzy Accesible Speed : ", intrinsequeSpeed_fuzzy)
    print("Accesible Speed : ",accessibleSpeed_output)

    # Visualize this
    fig, ax0 = plt.subplots(figsize=(8, 3))
    
    speed0 = np.zeros_like(x_accessibleSpeed)
    speed_activation = fuzz.interp_membership(x_accessibleSpeed, aggregated, accessibleSpeed_output)  # for plot

    ax0.plot(x_accessibleSpeed, accessibleSpeed[0], 'b', linewidth=0.5, linestyle='--')
    ax0.plot(x_accessibleSpeed, accessibleSpeed[1], 'g', linewidth=0.5, linestyle='--')
    ax0.plot(x_accessibleSpeed, accessibleSpeed[2], 'r', linewidth=0.5, linestyle='--')
    ax0.fill_between(x_accessibleSpeed, speed0, aggregated, facecolor='Orange', alpha=0.7)
    ax0.plot([accessibleSpeed_output, accessibleSpeed_output], [0, speed_activation], 'k', linewidth=1.5, alpha=0.9)
    ax0.set_title('Aggregated membership and result (line) -- Accessible Speed')

    # Turn off top/right axes
    for ax in (ax0,):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

    plt.tight_layout()
    plt.show()

    return accessibleSpeed_output

# ----------------------------------------------------------------------------------
# Fourth fuzzy system - Risk Level of performing a lane change
# ----------------------------------------------------------------------------------
# The objective of this module is to assess the risk of or the 
# possibility of executing a lane change. We considere the differents vehicules around
# the ego_vehcule and the type of line marking
#
# Inputs :
#           - TIV (fuzzy value IFT)
#           - Line Marking (crips value)
# Outputs :
#           - Possibility to perform a Lane change (crisp value)
#------------------------------------------------------------------------------------

def CL_risk_level(tiv_val, line_marking_val) : 
    ## Domaine
    x_tiv = np.arange(0,10.1,0.1)
    x_line_marking = np.arange(0, 1.1, 0.1)
    x_risk_level = np.arange(0, 1.1, 0.1)

    #TIV has the form of a trapmf vector
    ### Calcul directe
    fuzzy_tiv = fuzz.trapmf(x_tiv, tiv_val)

    # Generate fuzzy membership functions
    tiv  = []
    tiv.append (fuzz.trapmf(x_tiv, [0, 0, 1.0, 1.5])) 
    tiv.append (fuzz.trapmf(x_tiv, [1.0, 2.0, 3.0, 4.0]))
    tiv.append (fuzz.trapmf(x_tiv, [3.5, 4.0, 10.0, 10.0]))

    line_marking = []
    line_marking.append(fuzz.trapmf(x_line_marking, [0, 0, 0.5, 0.5]))
    line_marking.append(fuzz.trapmf(x_line_marking, [0.5 , 0.5, 1, 1]))

    risk_level = []
    risk_level.append(fuzz.trimf(x_risk_level, [0, 0, 0]))
    risk_level.append(fuzz.trimf(x_risk_level, [0 , 0, 1 ]))
    risk_level.append(fuzz.trimf(x_risk_level, [0, 1, 1]))

    tiv_level = []
    line_marking_level = []
    risk_level_level = []

    for i in range(2):
        line_marking_level.append(fuzz.interp_membership(x_line_marking, line_marking[i], line_marking_val))
    
    for i in range(3):
        tiv_level.append(max(np.fmin(tiv[i], fuzzy_tiv)))

    active_rule = [[0 for k in range(2)] for j in range(3)]

    for i in range (3) :
        for j in range (2):
            active_rule[i][j] = np.fmin(tiv_level[i], line_marking_level[j])
    # Continuous =1 , Broken = 0  
    # 3 rules
    active_rule_lo_max = max(   active_rule[0][1],
                                active_rule[1][1],
                                active_rule[2][1]   )


    risk_activation_lo = np.fmin(risk_level[0], active_rule_lo_max)

    # 1 rules
    active_rule_md_max = active_rule[0][0]

    risk_activation_md = np.fmin(risk_level[1], active_rule_md_max)

    # 2 rules
    active_rule_hi_max = max(   active_rule[1][0],
                                active_rule[2][0]   )

    risk_activation_hi = np.fmin(risk_level[2], active_rule_hi_max)

    # Aggregate all three output membership functions together
    aggregated = np.fmax(risk_activation_lo,
                        np.fmax(risk_activation_md, risk_activation_hi))
    
    # Calculate defuzzified result
    gauche_output = fuzz.defuzz(x_risk_level, aggregated, 'centroid')
    
    # gauche_output_fuzzy = [max(risk_activation_lo), max(risk_activation_md), max(risk_activation_hi)]
    # print(gauche_output)
    # print(gauche_output_fuzzy)
    # plt.plot(x_risk_level, aggregated, 'b', linewidth=0.5, linestyle='--' )
    # plt.plot(x_risk_level, risk_level[0], 'g', linewidth=0.5, linestyle='--' )
    # plt.plot(x_risk_level, risk_level[1], 'r', linewidth=0.5, linestyle='--' )
    # plt.plot(x_risk_level, risk_level[2], 'c', linewidth=0.5, linestyle='--' )
    # plt.show()
    return gauche_output

# ----------------------------------------------------------------------------------
# Fifth fuzzy system - Lateral Desicion
# ----------------------------------------------------------------------------------
# The objective of this module is the final decision of the lateral maneuver to perform.
# Considering the possibility or impossibility of going to the left or right lane 
# and the behavior of the driver
#
# Inputs (Crisp Values):
#           - Possibility Right
#           - Possibility Left
#           - Driver's behavior
# Outputs (Crisp Values):
#           - Decision : Keep Lane, Change Left Lane, Change Righ Lane
#------------------------------------------------------------------------------------

def DecisionOffset (right_val, left_val, behavior_val):
    x_right = np.arange(0, 1.1, 0.1)
    x_left = np.arange(0, 1.1, 0.1)
    x_behavior = np.arange(0, 1.1, 0.1)
    x_decision = np.arange(0, 1.1, 0.1)
    
    # Generate fuzzy membership functions
    right = []
    right.append(fuzz.trimf(x_right, [0, 0, 0]))
    right.append(fuzz.trimf(x_right, [0 , 0, 1 ]))
    right.append(fuzz.trimf(x_right, [0, 1, 1]))

    left = []
    left.append(fuzz.trimf(x_left, [0, 0, 0]))
    left.append(fuzz.trimf(x_left, [0 , 0, 1 ]))
    left.append(fuzz.trimf(x_left, [0, 1, 1]))

    behavior = []
    behavior.append (fuzz.trimf(x_behavior, [0, 0, 0.5]))
    behavior.append(fuzz.trimf(x_behavior, [0 , 0.5, 1]))
    behavior.append(fuzz.trimf(x_behavior, [0.5, 1, 1]))

    decision=[]
    decision.append(fuzz.trimf(x_decision, [0, 0 , 0]))
    decision.append(fuzz.trimf(x_decision, [0.5 , 0.5, 0.5]))
    decision.append(fuzz.trimf(x_decision, [1, 1 , 1]))

    # decision.append(fuzz.trapmf(x_decision, [0, 0, 0.33 , 0.33]))
    # decision.append(fuzz.trapmf(x_decision, [0.33 , 0.33 , 0.66 , 0.66]))
    # decision.append(fuzz.trapmf(x_decision, [0.66, 0.66, 1 , 1]))

    right_level = []
    left_level = []
    behavior_level = []

    for i in range(3):
        right_level.append(fuzz.interp_membership(x_right, right[i], right_val))
        left_level.append(fuzz.interp_membership(x_left, left[i], left_val))
        behavior_level.append(fuzz.interp_membership(x_behavior, behavior[i], behavior_val))

    active_rule = [[[0 for k in range(3)] for j in range(3)] for i in range(3)]

    for i in range (3) :
        for j in range (3):
            for k in range (3):
                active_rule[i][j][k] = np.fmin(right_level[i], left_level[j])
                active_rule[i][j][k] = np.fmin(active_rule[i][j][k],behavior_level[k])

    # 14 rules
    active_rule_lo_max = max(   active_rule[0][1][1],
                                active_rule[0][1][2],
                                active_rule[0][2][0],
                                active_rule[0][2][1],
                                active_rule[0][2][2],
                                active_rule[1][1][1],
                                active_rule[1][1][2],
                                active_rule[1][2][0],
                                active_rule[1][2][1],
                                active_rule[1][2][2],
                                active_rule[2][1][1],
                                active_rule[2][2][0],
                                active_rule[2][2][1],
                                active_rule[2][2][2]  )


    desicion_activation_lo = np.fmin(decision[0], active_rule_lo_max)

    # 10 rules
    active_rule_md_max = max(   active_rule[0][0][0],
                                active_rule[0][0][1],
                                active_rule[0][0][2],
                                active_rule[0][1][0],
                                active_rule[1][0][0],
                                active_rule[1][0][1],
                                active_rule[1][1][0],
                                active_rule[2][0][0],
                                active_rule[2][0][1],
                                active_rule[2][1][0]    )

    desicion_activation_md = np.fmin(decision[1], active_rule_md_max)

    # 3 rules
    active_rule_hi_max = max(   active_rule[1][0][2],
                                active_rule[2][0][2],
                                active_rule[2][1][2]  )

    desicion_activation_hi = np.fmin(decision[2], active_rule_hi_max)

    # Aggregate all three output membership functions together
    aggregated = np.fmax(desicion_activation_lo,
                        np.fmax(desicion_activation_md, desicion_activation_hi))
    
    # Calculate defuzzified result
    desicionmaking = fuzz.defuzz(x_decision, aggregated, 'centroid')

    desicionmaking_fuzzy = [max(desicion_activation_lo), max(desicion_activation_md), max(desicion_activation_hi)]
    print(desicionmaking_fuzzy)

    result = np.where(desicionmaking_fuzzy == np.amax(desicionmaking_fuzzy))
    
    if len(result) > 1:
        print("Pas de desicion")
    else:
        if result[0]== 0:
            print("CLL")
        elif result[0] == 1:
            print("KL")
        elif result[0] == 2:
            print("CRL")

    return desicionmaking

# ----------------------------------------------------------------------------------
# Module Limit Speed
# ----------------------------------------------------------------------------------
# The main objective of this module is to limit the speed, taking into 
# account the legal speed and the behavior of the driver.
#
# Inputs (Crisp values):
#           - Limit Speed
#           - Accesible Speed
# Outputs (Crisp value):
#           - Target Speed
#--------------------------------------------------------------

def SpeedLimmit(LimitSpeed, AccessibleSpeed, Behavior): 
    if(AccessibleSpeed >= LimitSpeed):
        if ( Behavior >= 0.66 ):
            print("Target Speed : ", AccessibleSpeed)
            return AccessibleSpeed
        print("Target Speed : ",LimitSpeed)
        return LimitSpeed
    else:
        print("Target Speed : ",AccessibleSpeed)
        return AccessibleSpeed


## 1er UseCase Longitudinal
visibility = Visibility(foggy_level = 0.4, brightness_level = 0.3)
v_intr = Vitesseintrinseque(conso_val = 15, age_r_val = 0.0, hate_val = 0.6)
acc_speed = AccessibleSpeed(v_intr, visibility)
LimitSpeed = 30
Behavior = 0.2
limit_speed = SpeedLimmit(LimitSpeed, acc_speed, Behavior) 

## 2eme  UseCase Lateral
# d = distanceFuzzification(20)
# s = speedFuzzification(10)
# tiv1 = caf_TIV(s, d)
# print (tiv1)

# d2 = distanceFuzzification(100)
# s2 = speedFuzzification(10)
# tiv2 = caf_TIV(s2, d2)

# vector = minTIV(tiv1, tiv2)

# right_posibility = CL_risk_level(vector, 0)

# d3 = distanceFuzzification(20)
# s3 = speedFuzzification(10)
# tiv3 = caf_TIV(s3, d3)
# print (tiv3)

# d4 = distanceFuzzification(100)
# s4 = speedFuzzification(10)
# tiv4 = caf_TIV(s4, d4)

# vector2 = minTIV(tiv3, tiv4)

# left_posibility = CL_risk_level(vector2, 0)

# DecisionOffset(right_posibility, left_posibility, Behavior)


