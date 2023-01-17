"""Example of automatic vehicle control from client side."""

from __future__ import print_function

from agents.navigation.basic_agent import BasicAgent
from Fuzzy_calculator import FuzzyCalculator

import argparse
import collections
import datetime
import glob
import logging
import math
import os
import numpy.random as random
import re
import sys
import weakref
import time
import threading
import queue

try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_q
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError(
        'cannot import numpy, make sure numpy package is installed')

# ==============================================================================
# -- Find CARLA module ---------------------------------------------------------
# ==============================================================================
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# ==============================================================================
# -- Add PythonAPI for release mode --------------------------------------------
# ==============================================================================
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/carla')
except IndexError:
    pass

import carla
from carla import ColorConverter as cc


class ThreadSimulation (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        try:
            self.stop_threads = False
            self.client = carla.Client('localhost', 2000);
            self.client.set_timeout(10.0);
            # ========================================================================
            # -- World ---------------------------------------------------------------
            # ========================================================================
            self.world = self.client.get_world()
            self.map = self.world.get_map()
            self._target_speed = 0.0
            self._speed_limit = 0.0
            self.calculator = FuzzyCalculator()
            self.detectedVehicle = False

            # =============================================================================
            # -- Speed Calculation --------------------------------------------------------
            # =============================================================================

            self.speedFrontVehicle = 1.0
            self.lastSpeedFrontVehicle = 1.0

            self.speedFrontRightVehicle = 1.0
            self.lastSpeedFrontRightVehicle = 1.0

            self.speedFrontLeftVehicle = 1.0
            self.lastSpeedFrontLeftVehicle = 1.0

            self.speedRearRightVehicle = 1.0
            self.lastSpeedRearRightVehicle = 1.0

            self.speedRearLeftVehicle = 1.0
            self.lastSpeedRearLeftVehicle = 1.0

            # =============================================================================
            # -- Distance Calculation ----------------------------------------------------------
            # =============================================================================

            self._frontalDistance = 50.0
            self._last_frontalDistance = 50.0

            self._frontalRightDistance = 50.0
            self._last_frontalRightDistance = 50.0

            self._frontalLeftDistance = 50.0
            self._last_frontalLeftDistance = 50.0

            self._rearRightDistance = 50.0
            self._last_rearRightDistance = 50.0

            self._rearLeftDistance = 50.0
            self._last_rearLeftDistance = 50.0

            self.t = threading.Thread(target=self.update_TIV)
            self.stop_threads_secondary = False
            self.t.start()

        finally:
            print('Thread simulation')

    def update_TIV(self):
        while True:
            if self.stop_threads_secondary:
                print ("Secondary Thread killed")
                break
            else:
                if(self._frontalDistance == self._last_frontalDistance):
                    realFrontalDistance = 100.0 
                else:
                    self._last_frontalDistance = self._frontalDistance
                    realFrontalDistance = self._frontalDistance

                if(self._frontalRightDistance == self._last_frontalRightDistance):
                    realFrontalRightDistance = 100.0 
                else:
                    self._last_frontalRightDistance = self._frontalRightDistance
                    realFrontalRightDistance = self._frontalRightDistance

                if(self._frontalLeftDistance == self._last_frontalLeftDistance):
                    realFrontalLeftDistance = 100.0 
                else:
                    self._last_frontalLeftDistance = self._frontalLeftDistance
                    realFrontalLeftDistance = self._frontalLeftDistance

                if(self._rearRightDistance == self._last_rearRightDistance):
                    realRearRightDistance = 100.0 
                else:
                    self._last_rearRightDistance = self._rearRightDistance
                    realRearRightDistance = self._rearRightDistance

                if(self._rearLeftDistance == self._last_rearLeftDistance):
                    realRearLeftDistance = 100.0 
                else:
                    self._last_rearLeftDistance = self._rearLeftDistance
                    realRearLeftDistance = self._rearLeftDistance
                
                ###### Speed ########

                if(self.speedFrontVehicle == self.lastSpeedFrontVehicle):
                    realSpeedFrontVehicle = 1.0 
                else:
                    self.lastSpeedFrontVehicle = self.speedFrontVehicle
                    realSpeedFrontVehicle = self.speedFrontVehicle

                if(self.speedFrontRightVehicle == self.lastSpeedFrontRightVehicle):
                    realSpeedFrontRightVehicle = 1.0 
                else:
                    self.lastSpeedFrontRightVehicle = self.speedFrontRightVehicle
                    realSpeedFrontRightVehicle = self.speedFrontRightVehicle

                if(self.speedFrontLeftVehicle == self.lastSpeedFrontLeftVehicle):
                    realSpeedFrontLeftVehicle = 1.0 
                else:
                    self.lastSpeedFrontLeftVehicle = self.speedFrontLeftVehicle
                    realSpeedFrontLeftVehicle = self.speedFrontLeftVehicle

                if(self.speedRearRightVehicle == self.lastSpeedRearRightVehicle):
                    realSpeedRearRightVehicle = 1.0 
                else:
                    self.lastSpeedRearRightVehicle = self.speedRearRightVehicle
                    realSpeedRearRightVehicle = self.speedRearRightVehicle

                if(self.speedRearLeftVehicle == self.lastSpeedRearLeftVehicle):
                    realSpeedRearLeftVehicle = 1.0 
                else:
                    self.lastSpeedRearLeftVehicle = self.speedRearLeftVehicle
                    realSpeedRearLeftVehicle = self.speedRearLeftVehicle
                
            #### Update Calculator Values ######
            self.calculator._frontalDistance = realFrontalDistance
            self.calculator._frontalRightDistance = realFrontalRightDistance
            self.calculator._frontalLeftDistance = realFrontalLeftDistance
            self.calculator._rearRightDistance = realRearRightDistance
            self.calculator._rearLeftDistance = realRearLeftDistance 

            self.calculator._frontalSpeed = realSpeedFrontVehicle
            self.calculator._frontalRightSpeed = (self._target_speed - realSpeedFrontRightVehicle)/3.6
            self.calculator._frontalLeftSpeed = (self._target_speed - realSpeedFrontLeftVehicle)/3.6
            self.calculator._rearRightSpeed = (realSpeedRearRightVehicle - self._target_speed)/3.6
            self.calculator._rearLeftSpeed = (realSpeedRearLeftVehicle - self._target_speed)/3.6

            time.sleep(0.010) ## verify each 10 miliseconds

    def run(self):
        while True:
            if self.stopped():
                return
            
            self.main_cycle()

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()

    def center_camera(self):
        self.calculator.recenter_camera()

    def set_foggy_level(self,value, value2):
        weather = carla.WeatherParameters(
            fog_density = value*100,
            sun_altitude_angle = 90+180*(value2-1))
        self.world.set_weather(weather)
    
    def set_extern_inputs(self, conso, age, behavior):
        self.calculator._conso = conso
        self.calculator._age = age
        self.calculator._behavior = behavior

    def get_target_speed(self):
        target_speed = self._target_speed
        return (round(target_speed,1))
    
    def get_outputs_fuzzy_systems(self):
        speedLimit = self._speed_limit
        return [speedLimit, round(self.calculator._foggy_level,2), round(self.calculator._brightness_level,2), round(self.calculator._conso,1), round(self.calculator._age, 1), round(self.calculator._behavior, 1), round(self.calculator._target_speed,2), round(self.calculator._visibility,2), round(self.calculator._intrinsicSpeed, 1), round(self.calculator._accessibleSpeed,1)]

    def front_detection(self,data):
        velocity = data.other_actor.get_velocity()
        speed = 3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
        self.speedFrontVehicle = speed
        self._frontalDistance = data.distance
    
    def left_front_detection(self,data):
        velocity = data.other_actor.get_velocity()
        speed = 3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
        self.speedFrontLeftVehicle = speed
        self._frontalLeftDistance = data.distance
        
    def left_rear_detection(self,data):
        velocity = data.other_actor.get_velocity()
        speed = 3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
        self.speedRearLeftVehicle = speed
        self._rearLeftDistance = data.distance
        
    def right_front_detection(self,data):
        velocity = data.other_actor.get_velocity()
        speed = 3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
        self.speedFrontRightVehicle = speed
        self._frontalRightDistance = data.distance
    
    def right_rear_detection(self,data):
        velocity = data.other_actor.get_velocity()
        speed = 3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
        self.speedRearRightVehicle = speed
        self._rearRightDistance = data.distance

    def main_cycle(self):
        try:
            # --------------
            # Strategical Level, Path definition
            # --------------
            waypoints = self.map.generate_waypoints(distance=2.0)
            target_waypoints = []
            reverse_path = [] # Some waypoints could be in the opposite direction 

            for waypoint in waypoints:
                if(waypoint.lane_id == -4 and waypoint.road_id == 45):
                    target_waypoints.append(waypoint)
            for waypoint in waypoints:
                if(waypoint.lane_id == -1 and waypoint.road_id == 136):
                    target_waypoints.append(waypoint)
            for waypoint in waypoints:
                if(waypoint.lane_id == -3 and waypoint.road_id == 22):
                    target_waypoints.append(waypoint)
            for waypoint in waypoints:
                if(waypoint.lane_id == -1 and waypoint.road_id == 1594):
                    target_waypoints.append(waypoint)
            for waypoint in waypoints:
                if(waypoint.lane_id == 6 and waypoint.road_id == 37):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []
            for waypoint in waypoints:
                if(waypoint.lane_id == 6 and waypoint.road_id == 761):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []
            for waypoint in waypoints:
                if(waypoint.lane_id == 6 and waypoint.road_id == 36):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []
            for waypoint in waypoints:
                if(waypoint.lane_id == 6 and waypoint.road_id == 862):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []
            for waypoint in waypoints:
                if(waypoint.lane_id == 6 and waypoint.road_id == 35):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []
            for waypoint in waypoints:
                if(waypoint.lane_id == 6 and waypoint.road_id == 43):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []
            for waypoint in waypoints:
                if(waypoint.lane_id == 6 and waypoint.road_id == 266):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []
            for waypoint in waypoints:
                if(waypoint.lane_id == 6 and waypoint.road_id == 42):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []
            for waypoint in waypoints:
                if(waypoint.lane_id == 6 and waypoint.road_id == 50):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []
            for waypoint in waypoints:
                if(waypoint.lane_id == 3 and waypoint.road_id == 1162):
                    reverse_path.append(waypoint)
            reverse_path.reverse()
            target_waypoints.extend(reverse_path)
            reverse_path = []

            for waypoint in waypoints:
                if(waypoint.lane_id == -3 and waypoint.road_id == 23):
                    target_waypoints.append(waypoint)    

            # --------------
            # Path Visualisation
            # --------------

            for waypoint in target_waypoints:
                self.world.debug.draw_string(waypoint.transform.location, 'O', draw_shadow=False,
                                            color=carla.Color(r=0, g=255, b=0), life_time=120,
                                            persistent_lines=True)

            # --------------
            # Start and End Point
            # --------------
            start_waypoint = target_waypoints[0]
            end_waypoint = target_waypoints[-1]

            # start_waypoint = self.map.get_waypoint(carla.Location(x=-264.83,y=435.70,z=0.5),project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Sidewalk))
            # end_waypoint = self.map.get_waypoint(carla.Location(x=-381.30,y=-5.77,z=0.5),project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Sidewalk))
            
            print(start_waypoint.transform.location)
            print(end_waypoint.transform.location)

            self.world.debug.draw_point(start_waypoint.transform.location,size=0.2, color=carla.Color(r=0, g=0, b=255), life_time=120.0)
            self.world.debug.draw_point(end_waypoint.transform.location,size=0.2, color=carla.Color(r=255, g=0, b=0), life_time=120.0)

            # --------------
            # Weather 
            # --------------
            weather = carla.WeatherParameters(
            fog_density =0.0,
            sun_altitude_angle =45)
            self.world.set_weather(weather)

            # --------------
            # Spawn ego vehicle
            # --------------
            ego_bp = self.world.get_blueprint_library().find('vehicle.tesla.model3')
            ego_bp.set_attribute('role_name','ego')
            print('\nEgo role_name is set')
            ego_color = random.choice(ego_bp.get_attribute('color').recommended_values)
            ego_bp.set_attribute('color',ego_color)
            print('\nEgo color is set')
            ego_transform = carla.Transform(start_waypoint.transform.location + carla.Location(z=0.5),carla.Rotation(yaw = 90)) # Avoid collision
            ego_vehicle = self.world.spawn_actor(ego_bp,ego_transform)
            print('\nEgo is spawned')

            # --------------
            # Spectator on ego position
            # --------------
            spectator = self.world.get_spectator()
            transform_ego = ego_vehicle.get_transform()
            spectator.set_transform(carla.Transform(transform_ego.location + carla.Location(z=8),
            carla.Rotation(pitch=-90)))
            
            # --------------
            # Agents
            # --------------

            agent = BasicAgent(ego_vehicle, opt_dict={"offset": 0})
            destination = end_waypoint.transform.location
            agent.set_destination(destination)
            agent.set_target_speed(50)
            agent.ignore_vehicles(active=True)
            # path = agent.trace_route(start_waypoint, end_waypoint) # Automatic path creation

            # --------------
            # Creation route
            # --------------

            route_trace = []
            for waypoint in target_waypoints:
                route_trace.append((waypoint, 4)) ## Follow Line = 4 
            
            agent.set_global_plan(route_trace)

            # --------------
            # Place front sensor 
            # --------------
            sensor_bp = self.world.get_blueprint_library().find('sensor.other.obstacle')
            sensor_bp.set_attribute('only_dynamics', 'True')
            sensor_bp.set_attribute('distance', '30.0')

            sensor_bp2 = self.world.get_blueprint_library().find('sensor.other.obstacle')
            sensor_bp2.set_attribute('only_dynamics', 'True')
            sensor_bp2.set_attribute('distance', '30.0')

            front_transform = carla.Transform(carla.Location(z = 0.5))
            front_sensor = self.world.spawn_actor(sensor_bp, front_transform, attach_to=ego_vehicle)
            # data = queue.Queue()
            # front_sensor.listen(data.put)
            front_sensor.listen(lambda data1: self.front_detection(data1))

            # --------------
            # Place left sensors 
            # --------------
            left_front_transform = carla.Transform(carla.Location(y=-3.5, z=0.5))
            left_front_sensor = self.world.spawn_actor(sensor_bp, left_front_transform, attach_to=ego_vehicle)
            left_front_sensor.listen(lambda data2: self.left_front_detection(data2))

            left_rear_transform = carla.Transform(carla.Location(y=-3.5, z=0.5), carla.Rotation(yaw = 180))
            left_rear_sensor = self.world.spawn_actor(sensor_bp2, left_rear_transform, attach_to=ego_vehicle)
            left_rear_sensor.listen(lambda data3: self.left_rear_detection(data3))

            # --------------
            # Place right sensors 
            # --------------

            right_front_transform = carla.Transform(carla.Location(y=3.5, z=0.5))
            right_front_sensor = self.world.spawn_actor(sensor_bp, right_front_transform, attach_to=ego_vehicle)
            right_front_sensor.listen(lambda data4: self.right_front_detection(data4))

            right_rear_transform = carla.Transform(carla.Location(y=3.5, z=0.5), carla.Rotation(yaw = -180))
            right_rear_sensor = self.world.spawn_actor(sensor_bp2, right_rear_transform, attach_to=ego_vehicle)
            right_rear_sensor.listen(lambda data5: self.right_rear_detection(data5))

            # camera_bp = world.get_blueprint_library().find('sensor.other.collision')
            # camera_transform = carla.Transform(carla.Location(x=-8, z=3))
            # camera = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)

            # --------------
            # Fuzzy Calculator
            # --------------
            self.calculator.set_vehicle(ego_vehicle) 
            # calculator = FuzzyCalculator(ego_vehicle) 

            # --------------
            # Detect zone to spawn vehicles
            # --------------
            # waypoints = self.map.generate_waypoints(distance=2.0)
            # main_filtered_waypoints = []
            # second_filtered_waypoints = []
            # for waypoint in waypoints:
            #     if(waypoint.road_id == 22):
            #         main_filtered_waypoints.append(waypoint)
            #     if(waypoint.road_id == 23):
            #         main_filtered_waypoints.append(waypoint)
            #     if(waypoint.road_id == 45):
            #         main_filtered_waypoints.append(waypoint)

            # for waypoint in waypoints:
            #     for x in range(30,51):
            #         if(waypoint.road_id == x & x!=45):
            #             second_filtered_waypoints.append(waypoint)
            
            # main_spawn_points = []
            # second_spawn_points = []

            # Debug visuel
            # for waypoint in main_filtered_waypoints:
            #     world.debug.draw_string(waypoint.transform.location, 'O', draw_shadow=False,
            #                                 color=carla.Color(r=255, g=0, b=0), life_time=life_time,
            #                                 persistent_lines=True)  
            # for waypoint in second_filtered_waypoints:
            #     world.debug.draw_string(waypoint.transform.location, 'O', draw_shadow=False,
            #                                 color=carla.Color(r=0, g=0, b=255), life_time=life_time,
            #                                 persistent_lines=True)
            
                       
            # Get the blueprint library and filter for the vehicle blueprints
            # vehicle_blueprints = self.world.get_blueprint_library().filter('*vehicle*')
            # # Get the map's spawn points
            # for waypoint in main_filtered_waypoints:
            #     main_spawn_points.append(carla.Transform(waypoint.transform.location + carla.Location(z=0.5)))

            # for waypoint in second_filtered_waypoints:
            #     second_spawn_points.append(carla.Transform(waypoint.transform.location + carla.Location(z=0.5)))

            

            # Spawn 50 vehicles randomly distributed throughout the map 
            # for each spawn point, we choose a random vehicle from the blueprint library

            # for i in range(0,20):
            #    self.world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(main_spawn_points))
            # for i in range(0,20):
            #    self.world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(second_spawn_points))

            # for vehicle in self.world.get_actors().filter('*vehicle*'):
            #     if(vehicle.id != ego_vehicle.id):
            #         vehicle.set_autopilot(True)

            # --------------
            # Main Loop
            # --------------
        
            while True:
                if self.stopped():
                    return

                if agent.done():
                    print("The target has been reached, stopping the simulation")
                    break

                velocity = ego_vehicle.get_velocity()
                speed = 3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
                self._target_speed = speed

                self._speed_limit = ego_vehicle.get_speed_limit()
                
                #    Control
                input_control = self.calculator.fuzzy_system_output()
                # print(input_control[0])
                agent.set_target_speed(input_control[0])
                agent.set_offset(input_control[1])
                #    Control
                ego_vehicle.apply_control(agent.run_step())

        finally:
            front_sensor.destroy()
            left_front_sensor.destroy()
            left_rear_sensor.destroy()
            right_front_sensor.destroy()
            right_rear_sensor.destroy()

            if ego_vehicle is not None:
                ego_vehicle.destroy()
                # for vehicle in self.world.get_actors().filter('*vehicle*'):
                #     if(vehicle.id != ego_vehicle.id):
                #         vehicle.destroy()
            self.stop_threads_secondary = True
            stop_threads = True
            print('Thread Simulation killed')