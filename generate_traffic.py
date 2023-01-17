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


def main():
# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================
    try:
        client = carla.Client('localhost', 2000);
        client.set_timeout(10.0);

    # ==============================================================================
    # -- World ---------------------------------------------------------------
    # ==============================================================================

        world = client.get_world()
    #   print(client.get_available_maps());
        map = world.get_map()

    # --------------
    # Detect zone to spawn vehicles
    # --------------
        waypoints = map.generate_waypoints(distance=2.0)
        main_filtered_waypoints = []
        second_filtered_waypoints = []
        target_waypoints = []

        # for waypoint in waypoints:
        #     if(waypoint.lane_id == -3 and waypoint.road_id == 41):
        #         target_waypoints.append(waypoint)
        
        for waypoint in waypoints:
            if(waypoint.lane_id == -4 and waypoint.road_id == 45):
                target_waypoints.append(waypoint)

        for waypoint in waypoints:
            if(waypoint.road_id == 22):
                main_filtered_waypoints.append(waypoint)
            if(waypoint.road_id == 23):
                main_filtered_waypoints.append(waypoint)
            if(waypoint.road_id == 45):
                main_filtered_waypoints.append(waypoint)

        for waypoint in waypoints:
            for x in range(30,51):
                if(waypoint.road_id == x & x!=45):
                    second_filtered_waypoints.append(waypoint)
    
        main_spawn_points = []
        second_spawn_points = []
        target_waypoints_spawn = []

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
        vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')
        # # Get the map's spawn points
        for waypoint in main_filtered_waypoints:
            main_spawn_points.append(carla.Transform(waypoint.transform.location + carla.Location(z=0.5)))

        for waypoint in second_filtered_waypoints:
            second_spawn_points.append(carla.Transform(waypoint.transform.location + carla.Location(z=0.5)))

        for waypoint in target_waypoints:
            target_waypoints_spawn.append(carla.Transform(waypoint.transform.location + carla.Location(z=0.5)))

    

    # Spawn 50 vehicles randomly distributed throughout the map 
    # for each spawn point, we choose a random vehicle from the blueprint library
        for i in range(0,20):
            world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(target_waypoints_spawn))
        
        # for i in range(0,20):
        #     world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(main_spawn_points))
        # for i in range(0,20):
        #     world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(second_spawn_points))

        for vehicle in world.get_actors().filter('*vehicle*'):
            vehicle.set_autopilot(True)

        for vehicle in world.get_actors().filter('*vehicle*'):
            vehicle.set_autopilot(True)

        while True:
            print ('test traffic')

    finally:
        for vehicle in world.get_actors().filter('*vehicle*'):
            vehicle.destroy()
        print ('Traffic deleted')
        a=2

# -- main() -------------------------------------------------------------

if __name__ == '__main__':
    main()
