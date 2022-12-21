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
            # ==============================================================================
            # -- World ---------------------------------------------------------------
            # =============================================================================
            self.world = self.client.get_world()
            self.map = self.world.get_map()
            self._target_speed = 0.0
        finally:
            print('Thread simulation error')

    def run(self):
        while True:
            if self.stopped():
                return
            
            self.main_cycle()

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()

    def set_foggy_level(self,value, value2):
        weather = carla.WeatherParameters(
            fog_density = value*100,
            sun_altitude_angle = 90+180*(value2-1))
        self.world.set_weather(weather)

    def get_target_speed(self):
        target_speed = self._target_speed
        return (round(target_speed,1))

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
            agent.set_target_speed(80)
            # path = agent.trace_route(start_waypoint, end_waypoint) # Automatic path creation

            # --------------
            # Creation route
            # --------------

            route_trace = []
            for waypoint in target_waypoints:
                route_trace.append((waypoint, 4)) ## Follow Line = 4 
            
            agent.set_global_plan(route_trace)

            # --------------
            # Place a sensor
            # --------------
            # camera_bp = world.get_blueprint_library().find('sensor.other.collision')
            # camera_transform = carla.Transform(carla.Location(x=-8, z=3))
            # camera = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)

            # --------------
            # Fuzzy Calculator
            # --------------

            calculator = FuzzyCalculator(ego_vehicle) 

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

                velocity=ego_vehicle.get_velocity()
                speed= 3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
                self._target_speed = speed
                       
                #    Control
                input_control = calculator.fuzzy_system_output()
                # print(input_control[0])
                agent.set_target_speed(input_control[0])
                agent.set_offset(-3.5)
                #    Control
                ego_vehicle.apply_control(agent.run_step())

        finally:
            if ego_vehicle is not None:
                ego_vehicle.destroy()
                # for vehicle in self.world.get_actors().filter('*vehicle*'):
                #     if(vehicle.id != ego_vehicle.id):
                #         vehicle.destroy()
            stop_threads = True
            print('thread killed')