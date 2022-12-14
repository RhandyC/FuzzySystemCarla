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
        #self.speed_cal.Sistemeflou1(value, value2)

    def get_target_speed(self):
        target_speed = self._target_speed
        return (round(target_speed,1))

    def main_cycle(self):
        try:
            # stop_threads = False
            # client = carla.Client('localhost', 2000);
            # client.set_timeout(10.0);
            # # ==============================================================================
            # # -- World ---------------------------------------------------------------
            # # =============================================================================
            # world = client.get_world()
            # --------------
            # Start and End Point
            # --------------
            # map = world.get_map()
            start_waypoint = self.map.get_waypoint(carla.Location(x=-264.83,y=435.70,z=0.5),project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Sidewalk))
            end_waypoint = self.map.get_waypoint(carla.Location(x=-381.30,y=-5.77,z=0.5),project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Sidewalk))
            
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
            ego_transform = carla.Transform(start_waypoint.transform.location + carla.Location(z=0.5)) # Avoid collision
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
            agent.set_target_speed(40)
            path = agent.trace_route(start_waypoint, end_waypoint)

            # --------------
            # Path Visualisation
            # --------------

            i = 0 # waypoints in  the first column
            waypoint_list = [fila[i] for fila in path]
            print(waypoint_list[0].transform.location) ## Fitted Start Point
            
            for x in (waypoint_list):
                self.world.debug.draw_point(x.transform.location,size=0.1, color=carla.Color(r=0, g=255, b=0), life_time=120.0)

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
                print(input_control[0])
                agent.set_target_speed(input_control[0])
                #    Control
                ego_vehicle.apply_control(agent.run_step())

        finally:
            if ego_vehicle is not None:
                ego_vehicle.destroy()
            stop_threads = True
            print('thread killed')