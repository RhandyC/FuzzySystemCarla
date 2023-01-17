"""
This module is made up of 5 fuzzy systems and 3 fuzzy arithmetic operations, 
the objective of this project is to be able to command a car at a tactical 
level. This module was developped by Rhandy CARDENAS and Loic TCHAMGOUE. 
The reference library used was skfuzzy https://pythonhosted.org/scikit-fuzzy/
"""
# ==============================================================================
# -- Find CARLA module ---------------------------------------------------------
# ==============================================================================
import sys
import glob
import os
import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
from enum import Enum

from agents.navigation.local_planner import LocalPlanner
from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.tools.misc import get_speed, is_within_distance, get_trafficlight_trigger_location

class FuzzyCalculator(object):
    def __init__(self):
        
        self._vehicle = None
        self._world = None
        self._map = None
        self._debug_marking_lines = False
        self._debug_foggy_level = False
        self._debug_brightness_level = False

        self._current_set_target_speed = 50.0 
        self._foggy_level = 0.0
        self._brightness_level = 1.0
        self._speed_limit = 0.0
        self._conso = 10.0
        self._age = 0.0
        self._behavior = 0.0
        self._target_speed = 0.0
        self._offset = 0.0
        self._target_offset = 0.0
        self._maneuver_execution = False  

        self._visibility = 0.0
        self._intrinsicSpeed = 0.0
        self._accessibleSpeed = 0.0

        self._frontalDistance = 50.0
        self._frontalRightDistance = 50.0
        self._frontalLeftDistance = 50.0
        self._rearRightDistance = 50.0
        self._rearLeftDistance = 50.0

        self._frontalSpeed = 1.0
        self._frontalRightSpeed = 1.0
        self._frontalLeftSpeed = 1.0
        self._rearRightSpeed = 1.0
        self._rearLeftSpeed = 1.0

    def set_vehicle(self, vehicle):
        self._vehicle = vehicle
        self._world = self._vehicle.get_world()
        self._map = self._world.get_map()
        self._speed_limit = self._vehicle.get_speed_limit()
    
    def recenter_camera(self):
        # --------------
        # Spectator on ego position
        # --------------
        spectator = self._world.get_spectator()
        transform_ego = self._vehicle.get_transform()
        spectator.set_transform(carla.Transform(transform_ego.location + carla.Location(z=50),
        carla.Rotation(pitch=-90)))

    def get_marking_lanes(self):
        waypoint = self._world.get_map().get_waypoint(self._vehicle.get_location(),project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Shoulder | carla.LaneType.Sidewalk))  
        if(self._debug_marking_lines):
            # Left, Current and Right lane markings
            print("L lane marking type: " + str(waypoint.left_lane_marking.type) + "  R lane marking type: " + str(waypoint.right_lane_marking.type))
        marking_lines = [waypoint.left_lane_marking.type, waypoint.right_lane_marking.type]
        return marking_lines
    
    def getLineMarkingLeft(self):
        markingLeft = self.get_marking_lanes()
        if (str(markingLeft[0])=="Solid"):
            return 1
        else:
            return 0

    def getLineMarkingRight(self):
        markingRight = self.get_marking_lanes()
        if (str(markingRight[1])=="Solid"):
            return 1
        else:
            return 0

    def get_foggy_level(self):
        foggy_level= self._world.get_weather().fog_density 
        if(self._debug_foggy_level):
            print("Foggy level: " + str(foggy_level/100.0))
        return (round(foggy_level/100.0,2))

    def get_brightness_level(self):
        brightness_level = self._world.get_weather().sun_altitude_angle 
        if(self._debug_brightness_level):
            print("Brightness level: " + str((brightness_level + 90.0) / 180.0))
        return (round(((brightness_level + 90.0) / 180.0),2))

    def isACCActive(self):
        if(self._frontalDistance <= 20):
            return True
        else:
            return False

    # --------------
    # Function called each iteration in order to calcul longitudinal and lateral targets
    # --------------

    def fuzzy_system_output(self):
        # --------------
        # Longitudinal Control
        # --------------
        if (self.isACCActive()):
            self._target_speed = self._frontalSpeed
        else:
            speed_limit = self._vehicle.get_speed_limit()
            self._foggy_level = self.get_foggy_level()
            self._brightness_level = self.get_brightness_level()
            self._visibility = self.Visibility(self._foggy_level ,self._brightness_level)
            self._intrinsicSpeed = self.Vitesseintrinseque(self._conso, self._age, self._behavior)
            self._accessibleSpeed = self.AccessibleSpeed(self._intrinsicSpeed, self._visibility)
            self._target_speed = self.SpeedLimmit(speed_limit, self._accessibleSpeed)

        # --------------
        # Lateral Control
        # --------------
        if (self._maneuver_execution == False) :
            if (self.isACCActive()):
                # --------------
                # Right Side
                # --------------
                d1 = self.distanceFuzzification(self._frontalRightDistance, range = 1.0)
                s1 = self.speedFuzzification(self._frontalRightSpeed,range = 1.0)
                tiv1 = self.caf_TIV(s1, d1)

                d2 = self.distanceFuzzification(self._rearRightDistance, range = 1.0)
                s2 = self.speedFuzzification(self._rearRightSpeed,range = 1.0)
                tiv2 = self.caf_TIV(s2, d2)

                mintiv1 = self.minTIV(tiv1, tiv2)

                right_level = self.CL_risk_level(mintiv1, self.getLineMarkingRight())

                # --------------
                # Left Side
                # --------------
                d3 = self.distanceFuzzification(self._frontalLeftDistance, range = 1.0)
                s3 = self.speedFuzzification(self._frontalLeftSpeed,range = 1.0)
                tiv3 = self.caf_TIV(s3, d3)

                d4 = self.distanceFuzzification(self._rearLeftDistance, range = 1.0)
                s4 = self.speedFuzzification(self._rearLeftSpeed,range = 1.0)
                tiv4 = self.caf_TIV(s4, d4)

                mintiv2 = self.minTIV(tiv3, tiv4)

                left_level = self.CL_risk_level(mintiv2, self.getLineMarkingLeft())

                # --------------
                # Making Decision
                # --------------
                decision = self.DecisionOffset(right_level, left_level, self._behavior)
                print(decision)
                # --------------
                # Change lane management
                # --------------
                if decision == "CLL":
                    self._target_offset = self._target_offset - 3.5
                elif decision == "KL":
                    self._target_offset = self._target_offset
                elif decision == "CRL":
                    self._target_offset = self._target_offset + 3.5
            else: 
                #### try to go to the line furthest to the right if possible
                if(self._frontalRightDistance >= 20 and self._rearRightDistance >=20):
                    self._target_offset = 0
        
        # --------------
        # Maneuver execution (CLL and CRL)
        # --------------
        if(self._target_offset < self._offset):
            self._maneuver_execution = True
            self._offset = self._offset - 0.05
            if(self._target_offset >= self._offset):
                self._maneuver_execution = False
        
        if(self._target_offset > self._offset):
            self._maneuver_execution = True
            self._offset = self._offset + 0.05
            if(self._target_offset <= self._offset):
                self._maneuver_execution = False

        print("offset: ",self._offset," target: ", self._target_offset )

        return [self._target_speed, self._offset]

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

    def Visibility(self, foggy_level, brightness_level) :
        # Domain of variables
        x_foggy = np.arange(0, 1.05, 0.01)
        x_brightness = np.arange(0, 1.05, 0.01)        
        x_visibility  = np.arange(0, 1.05, 0.01)        
        # Classes of variables with membership functions
        foggy_lo = fuzz.trimf(x_foggy, [0, 0, 0.25])        
        foggy_md = fuzz.trimf(x_foggy, [0.1, 0.25, 0.4])        
        foggy_hi = fuzz.trimf(x_foggy, [0.3, 1, 1])        
        brightness_lo = fuzz.trimf(x_brightness, [0, 0, 0.6])  
        brightness_hi = fuzz.trimf(x_brightness, [0.4, 1, 1])        
        visibility_lo = fuzz.trimf(x_visibility, [0, 0, 0.4])        
        visibility_md = fuzz.trimf(x_visibility, [0.3, 0.5, 0.7])        
        visibility_hi = fuzz.trimf(x_visibility, [0.6, 1, 1])      

        # Interpretation of crisp value inside the membership functions
        foggy_level_lo = fuzz.interp_membership(x_foggy, foggy_lo, foggy_level)
        foggy_level_md = fuzz.interp_membership(x_foggy, foggy_md, foggy_level)
        foggy_level_hi = fuzz.interp_membership(x_foggy, foggy_hi, foggy_level)
        brightness_level_lo = fuzz.interp_membership(x_brightness, brightness_lo, brightness_level)
        brightness_level_hi = fuzz.interp_membership(x_brightness, brightness_hi, brightness_level)

        # Rules
        active_rule1 = np.fmin(foggy_level_lo, brightness_level_hi)
        active_rule2 = np.fmin(foggy_level_lo, brightness_level_lo)
        active_rule3 = np.fmin(foggy_level_md, brightness_level_hi)
        active_rule4 = np.fmin(foggy_level_md, brightness_level_lo)
        active_rule5 = np.fmin(foggy_level_hi, brightness_level_hi)
        active_rule6 = np.fmin(foggy_level_hi, brightness_level_lo)

        # Triggering of rules
        visibility_activation_hi = np.fmin(active_rule1, visibility_hi ) 
        visibility_activation_md = np.fmin(max(active_rule2, active_rule3), visibility_md)
        visibility_activation_lo = np.fmin(max(active_rule4, active_rule5, active_rule6), visibility_lo)
        
        # Fuzzy ouput if needed
        visibility_fuzzy = [max(visibility_activation_lo), max(visibility_activation_md), max(visibility_activation_hi)]

        # Aggregate all three output membership functions together
        aggregated = np.fmax(visibility_activation_lo,
                            np.fmax(visibility_activation_md, visibility_activation_hi))

        # Calculate defuzzified result
        visibility = fuzz.defuzz(x_visibility, aggregated, 'centroid')

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

    def Vitesseintrinseque(self, conso_val, age_r_val, hate_val) : 
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

    def AccessibleSpeed(self, intSpeed_val, visibility_val) : 
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

        return accessibleSpeed_output

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
    #------------------------------------------------------------------------------------

    def SpeedLimmit(self, LimitSpeed, AccessibleSpeed) : 
        if(AccessibleSpeed >= LimitSpeed):
            if ( self._behavior >= 0.66 ):
                return AccessibleSpeed
            return LimitSpeed
        else:
            return AccessibleSpeed

    # ----------------------------------------------------------------------------------
    # Modules fuzzyfication
    # ----------------------------------------------------------------------------------
    # In order to make more realistic our system we decided to fuzzyfy our inputs, then
    # do a arithmetic fuzzy calculation. The following functions serve this purpose
    #
    #-----------------------------------------------------------------------------------

    def distanceFuzzification(self, distance, range = 1.0):
        # Notation kauffman IFT 
        return [distance - range, distance - range/2.0, distance + range/2.0, distance + range]

    def speedFuzzification(self, speed,range = 1.0):
        # Notation kauffman IFT 
        return [speed - range, speed - range/2.0, speed + range/2.0, speed + range] 

    # ----------------------------------------------------------------------------------
    # Modules CAF
    # ----------------------------------------------------------------------------------
    # One of the necessary inputs for the following systems is the intervehicular
    # time that will be calculated as follows. Then we need to choose the most 
    # restrictive TIV in other words the smallest.
    #
    #-----------------------------------------------------------------------------------

    def caf_TIV(self, speed, distance):
        if( speed[0] < 0.0 ):
            return [10.0,10.0,10.0,10.0]
        else:
            ### Calcul directe
            return [distance[0]/speed[3],distance[1]/speed[2],distance[2]/speed[1] ,distance[3]/speed[0]]
        
    def minTIV(self, tiv1, tiv2):
        ### Calcul directe         
        ## Notation kauffman IFT 
        vector_trapmf = [min(tiv1[0], tiv2[0]),min(tiv1[1], tiv2[1]),min(tiv1[2], tiv2[2]),min(tiv1[3], tiv2[3])]
        return vector_trapmf
    
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

    def CL_risk_level(self, tiv_val, line_marking_val) : 
        # Domain of variables
        x_tiv = np.arange(0,10.1,0.1)
        x_line_marking = np.arange(0, 1.1, 0.1)
        x_risk_level = np.arange(0, 1.1, 0.1)

        ### tiv_val has the form of a trapmf vector
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
        
        # Continuous = 1 , Broken = 0  
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
        cl_output = fuzz.defuzz(x_risk_level, aggregated, 'centroid')
        
        # Fuzzy ouput if needed
        cl_output_fuzzy = [max(risk_activation_lo), max(risk_activation_md), max(risk_activation_hi)]

        return cl_output
    
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

    def DecisionOffset (self, right_val, left_val, behavior_val):
        # Domain of variables
        x_right = np.arange(0, 1.1, 0.1)
        x_left = np.arange(0, 1.1, 0.1)
        x_behavior = np.arange(0, 1.1, 0.1)
        x_decision = np.arange(0, 1.1, 0.1)
        
        # Generate fuzzy membership functions using arrays (faster)
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

        # Interpretation of crisp value inside the membership functions using arrays 
        right_level = []
        left_level = []
        behavior_level = []

        for i in range(3):
            right_level.append(fuzz.interp_membership(x_right, right[i], right_val))
            left_level.append(fuzz.interp_membership(x_left, left[i], left_val))
            behavior_level.append(fuzz.interp_membership(x_behavior, behavior[i], behavior_val))

        # Rules using arrays
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

        # Triggering of rules
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
        # Triggering of rules
        desicion_activation_md = np.fmin(decision[1], active_rule_md_max)

        # 3 rules
        active_rule_hi_max = max(   active_rule[1][0][2],
                                    active_rule[2][0][2],
                                    active_rule[2][1][2]  )
        # Triggering of rules
        desicion_activation_hi = np.fmin(decision[2], active_rule_hi_max)

        # Aggregate all three output membership functions together
        aggregated = np.fmax(desicion_activation_lo,
                            np.fmax(desicion_activation_md, desicion_activation_hi))
        
        # Calculate defuzzified result
        desicionmaking = fuzz.defuzz(x_decision, aggregated, 'centroid')

        # Fuzzy ouput if needed
        desicionmaking_fuzzy = [max(desicion_activation_lo), max(desicion_activation_md), max(desicion_activation_hi)]

        # Find the best maneuver to choose
        result = np.where(desicionmaking_fuzzy == np.amax(desicionmaking_fuzzy))
        
        if len(result) > 1:
            print("Pas de desicion")
        else:
            if result[0]== 0:
                return ("CLL")
            elif result[0] == 1:
                return ("KL")
            elif result[0] == 2:
                return ("CRL")