# Copyright (c) # Copyright (c) 2018-2020 CVC.
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
This module implements an agent that roams around a track following random
waypoints and avoiding other vehicles. The agent also responds to traffic lights.
It can also make use of the global route planner to follow a specifed route
"""
# ==============================================================================
# -- Find CARLA module ---------------------------------------------------------
# ==============================================================================
import sys
import glob
import os
import threading
import time

##### Fuzzy system
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
    """
    Fuzzzy system charged to obtain longitudinal and lateral tactical commands
    """

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

    def get_marking_lanes(self):
        waypoint = self._world.get_map().get_waypoint(self._vehicle.get_location(),project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Shoulder | carla.LaneType.Sidewalk))  
        if(self._debug_marking_lines):
            # Left, Current and Right lane markings
            print("L lane marking type: " + str(waypoint.left_lane_marking.type) + "  R lane marking type: " + str(waypoint.right_lane_marking.type))
        marking_lines = [waypoint.left_lane_marking.type, waypoint.right_lane_marking.type]
        return marking_lines
    
    def distanceFuzzification(self, distance):
        return 

    def speedFuzzification(self, speed):
        return

    def get_foggy_level(self):
        foggy_level= self._world.get_weather().fog_density 
        if(self._debug_foggy_level):
            # Left, Current and Right lane markings
            print("Foggy level: " + str(foggy_level/100.0))
        return (round(foggy_level/100.0,2))

    def get_brightness_level(self):
        brightness_level = self._world.get_weather().sun_altitude_angle 
        if(self._debug_brightness_level):
            # Left, Current and Right lane markings
            print("Brightness level: " + str((brightness_level + 90.0) / 180.0))
        return (round(((brightness_level + 90.0) / 180.0),2))

    def isACCActive(self):
        if(self._frontalDistance <= 20):
            # print("ACC active")
            return True
        else:
            # print("ACC disabled")
            return False

    def isRightLaneChangePossible(self):
        marking_lines=self.get_marking_lanes()
        return True

    def isLeftLaneChangePossible(self):
        marking_lines=self.get_marking_lanes()
        return True

    def fuzzy_system_output(self):
        ### Longitudinal Control ####
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

        ### Lateral Control ####
        if (self._maneuver_execution == False) :
            if (self.isACCActive()):
                self._target_offset = -3.5
            else: 
                self._target_offset = 0
        
        if(self._target_offset< self._offset):
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

    def Sistemeflou1(self, foggy_level, brightness_level):        
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

        # Aggregate all three output membership functions together
        aggregated = np.fmax(speed_activation_lo,
                            np.fmax(speed_activation_md, speed_activation_hi))

        # Calculate defuzzified result
        speed = fuzz.defuzz(x_speed, aggregated, 'centroid')
        speed_activation = fuzz.interp_membership(x_speed, aggregated, speed)  # for plot
        #print(speed)

        return (round(speed,1))

    def Visibility(self, foggy_level, brightness_level) : 
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
        # print(visibility_activation_hi)
        # Sortie floue, vector classes
        visibility_fuzzy = [max(visibility_activation_lo), max(visibility_activation_md), max(visibility_activation_hi)]

        # print(visibility_fuzzy)

        visibility0 = np.zeros_like(x_visibility)

        # Aggregate all three output membership functions together
        aggregated = np.fmax(visibility_activation_lo,
                            np.fmax(visibility_activation_md, visibility_activation_hi))

        # Calculate defuzzified result
        visibility = fuzz.defuzz(x_visibility, aggregated, 'centroid')
        visibility_activation = fuzz.interp_membership(x_visibility, aggregated, visibility)  # for plot

        return (visibility)

    def Vitesseintrinseque(self, conso_val, age_r_val, hate_val) : 
        x_conso = np.arange(0, 25.1, 0.1)
        x_age_r = np.arange(0, 25.1, 0.1)
        x_hate = np.arange(0, 1.1, 0.1)
        x_speed = np.arange(0, 200.1, 0.1)
        
        # Generate fuzzy membership functions
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

        conso_level = []
        age_r_level = []
        hate_level = []

        for i in range(3):
            conso_level.append(fuzz.interp_membership(x_conso, conso[i], conso_val))
            age_r_level.append(fuzz.interp_membership(x_age_r, age_r[i], age_r_val))
            hate_level.append(fuzz.interp_membership(x_hate, hate[i], hate_val))

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

        speed_activation_md = np.fmin(speed[1], active_rule_md_max)

        # 4 rules
        active_rule_hi_max = max(   active_rule[1][0][2],
                                    active_rule[2][0][1],
                                    active_rule[2][0][2],
                                    active_rule[2][1][2]  )

        speed_activation_hi = np.fmin(speed[2], active_rule_hi_max)

        # Aggregate all three output membership functions together
        aggregated = np.fmax(speed_activation_lo,
                            np.fmax(speed_activation_md, speed_activation_hi))
        
        # Calculate defuzzified result
        intrinsicSpeed = fuzz.defuzz(x_speed, aggregated, 'centroid')

        # intrinsequeSpeed_fuzzy = [max(speed_activation_lo), max(speed_activation_md), max(speed_activation_hi)]
        # print(intrinsequeSpeed_fuzzy)

        return intrinsicSpeed

    def AccessibleSpeed(self, intSpeed_val, visibility_val) : 

        x_visibility = np.arange(0,1.1,0.1)
        x_intSpeed = np.arange(0, 200.1, 0.1)
        x_accessibleSpeed = np.arange(0, 200.1, 0.1)
        
        # Generate fuzzy membership functions
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

        visibility_level = []
        intSpeed_level = []
        accessibleSpeed_level = []

        for i in range(3):
            visibility_level.append(fuzz.interp_membership(x_visibility, visibility[i], visibility_val))
            intSpeed_level.append(fuzz.interp_membership(x_intSpeed, intSpeed[i], intSpeed_val))

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


        speed_activation_lo = np.fmin(accessibleSpeed[0], active_rule_lo_max)

        # 2 rules
        active_rule_md_max = max(   active_rule[1][2],
                                    active_rule[2][1]   )

        speed_activation_md = np.fmin(accessibleSpeed[1], active_rule_md_max)

        # 1 rules
        active_rule_hi_max = active_rule[2][2]

        speed_activation_hi = np.fmin(accessibleSpeed[2], active_rule_hi_max)

        # Aggregate all three output membership functions together
        aggregated = np.fmax(speed_activation_lo,
                            np.fmax(speed_activation_md, speed_activation_hi))
        
        # Calculate defuzzified result
        accessibleSpeed_output = fuzz.defuzz(x_accessibleSpeed, aggregated, 'centroid')

        # intrinsequeSpeed_fuzzy = [max(speed_activation_lo), max(speed_activation_md), max(speed_activation_hi)]
        # print(intrinsequeSpeed_fuzzy)

        return accessibleSpeed_output

    def SpeedLimmit(self, LimitSpeed, AccessibleSpeed) : 
        if(AccessibleSpeed>=LimitSpeed):
            if ( self._behavior >= 0.7 ):
                return AccessibleSpeed
            return LimitSpeed
        else:
            return AccessibleSpeed




