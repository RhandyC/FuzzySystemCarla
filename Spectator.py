#!/usr/bin/env python

# Copyright (c) 2018 Intel Labs.
# authors: German Ros (german.ros@intel.com)
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.
###Holaaa

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

n=4
stop_threads = False

def callback(stop):
    global n
    while True:
        time.sleep(10)
        n=n+1
        if stop():
            break


def main():
# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================
    try:
        stop_threads = False
        client = carla.Client('localhost', 2000);
        client.set_timeout(10.0);

    # ==============================================================================
    # -- World ---------------------------------------------------------------
    # =============================================================================
        world = client.get_world()
    # ==============================================================================
    # -- KeyboardControl -----------------------------------------------------------
    # =============================================================================

        # --------------
        # Start and End Point
        # --------------
        map = world.get_map()
        start_waypoint = map.get_waypoint(carla.Location(x=-264.83,y=435.70,z=0.5),project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Sidewalk))
        end_waypoint = map.get_waypoint(carla.Location(x=-381.30,y=-5.77,z=0.5),project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Sidewalk))
        
        print(start_waypoint.transform.location)
        print(end_waypoint.transform.location)

        world.debug.draw_point(start_waypoint.transform.location,size=0.2, color=carla.Color(r=0, g=0, b=255), life_time=120.0)
        world.debug.draw_point(end_waypoint.transform.location,size=0.2, color=carla.Color(r=255, g=0, b=0), life_time=120.0)


        # --------------
        # Weather 
        # --------------
        weather = carla.WeatherParameters(
        fog_density =0.0,
        sun_altitude_angle =45)
        world.set_weather(weather)

        # --------------
        # Spawn ego vehicle
        # --------------
        ego_bp = world.get_blueprint_library().find('vehicle.tesla.model3')
        ego_bp.set_attribute('role_name','ego')
        print('\nEgo role_name is set')
        ego_color = random.choice(ego_bp.get_attribute('color').recommended_values)
        ego_bp.set_attribute('color',ego_color)
        print('\nEgo color is set')
        ego_transform = carla.Transform(start_waypoint.transform.location + carla.Location(z=0.5)) # Avoid collision
        ego_vehicle = world.spawn_actor(ego_bp,ego_transform)
        print('\nEgo is spawned')

        # --------------
        # Spectator on ego position
        # --------------
        spectator = world.get_spectator()
        transform_ego = ego_vehicle.get_transform()
        spectator.set_transform(carla.Transform(transform_ego.location + carla.Location(z=8),
        carla.Rotation(pitch=-90)))
        
        # --------------
        # Agents
        # --------------

        # agent = BasicAgent(ego_vehicle, opt_dict={"offset": -3.5})
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
            world.debug.draw_point(x.transform.location,size=0.1, color=carla.Color(r=0, g=255, b=0), life_time=120.0)

        # --------------
        # Thread for periodic function
        # --------------

        t1 = threading.Thread(target = callback, args =(lambda : stop_threads, ))
        t1.start()
        global n

        # --------------
        # Place a sensor
        # --------------
        camera_bp = world.get_blueprint_library().find('sensor.other.collision')
        camera_transform = carla.Transform(carla.Location(x=-8, z=3))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)

        # --------------
        # Fuzzy Calculator
        # --------------

        calculator = FuzzyCalculator(ego_vehicle) 

        # --------------
        # Main Loop
        # --------------
        while True:   

            #### Weather change, maybe put inside of a thread
            weather = carla.WeatherParameters(
            fog_density =0.0,
            sun_altitude_angle =90-n*8)
            world.set_weather(weather)
            # POV EGO
            # spectator.set_transform(camera.get_transform())

            if agent.done():
                print("The target has been reached, stopping the simulation")
                break

            #    Set Speed and Offset
            # agent.set_target_speed(n*10)
            # agent.set_offset(n/(-5))

            #    Print speed and offset

            # velocity=ego_vehicle.get_velocity()
            # speed= 3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
            # print("speed: ",speed, "offset:  ",n/(-5))

            #    Control
            input_control = calculator.fuzzy_system_output()

            #    Control
            ego_vehicle.apply_control(agent.run_step())
    finally:
        if ego_vehicle is not None:
            ego_vehicle.destroy()
        stop_threads = True
        print('thread killed')
            

# -- main() -------------------------------------------------------------

if __name__ == '__main__':
    main()
