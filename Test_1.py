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

    # ==============================================================================
    # -- KeyboardControl -----------------------------------------------------------
    # =============================================================================

        
        # This will set the spectator at the origin of the map, with 0 degrees
        # pitch, yaw and roll - a good way to orient yourself in the map

        vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')
        
        # Get the map's spawn points
        spawn_points = world.get_map().get_spawn_points()

        # for i in range(0,50):
        #     world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(spawn_points))

        # --------------
        # Spawn ego vehicle
        # --------------
        ego_bp = world.get_blueprint_library().find('vehicle.tesla.model3')
        ego_bp.set_attribute('role_name','ego')
        print('\nEgo role_name is set')
        ego_color = random.choice(ego_bp.get_attribute('color').recommended_values)
        ego_bp.set_attribute('color',ego_color)
        print('\nEgo color is set')

        spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(spawn_points)

        if 0 < number_of_spawn_points:
            random.shuffle(spawn_points)
            ego_transform = spawn_points[0]
            ego_vehicle = world.spawn_actor(ego_bp,ego_transform)
            print('\nEgo is spawned')
        else: 
            logging.warning('Could not found any spawn points')

        # --------------
        # Spectator on ego position
        # --------------
        spectator = world.get_spectator()
        world_snapshot = world.wait_for_tick() 
        transform_ego = ego_vehicle.get_transform()
        spectator.set_transform(carla.Transform(transform_ego.location + carla.Location(z=8),
        carla.Rotation(pitch=-90)))


        map = world.get_map()
        spawn_points = world.get_map().get_spawn_points()
        waypoint_list = map.generate_waypoints(2.0)
        print(len(waypoint_list))
        # mark=str(waypoint_list[1].lane_id)
        # world.debug.draw_point(waypoint_list[1].transform.location,size=0.1, color=carla.Color(r=255, g=0, b=0), life_time=120.0)

        for x in (waypoint_list):
            world.debug.draw_point(x.transform.location,size=0.1, color=carla.Color(r=255, g=0, b=0), life_time=120.0)

        # This recipe shows the current traffic rules affecting the vehicle. 
        # Shows the current lane type and if a lane change can be done in the actual lane or the surrounding ones.

        # ...
        agent = BasicAgent(ego_vehicle, target_speed=20, opt_dict={"offset": 1})


        destination = random.choice(spawn_points).location
        agent.set_destination(destination)

        while True:
            a=spectator.get_transform()
            # time.sleep(0.5)
            # print(transform_ego.location-a.location ,"et ")
            
           # print(a.location)
            # print(a.rotation)
            
            if agent.done():
                print("The target has been reached, stopping the simulation")
                break
            ego_vehicle.apply_control(agent.run_step())

            #waypoint = world.get_map().get_waypoint(ego_vehicle.get_location(),project_to_road=True, lane_type=(carla.LaneType.Driving | carla.LaneType.Shoulder | carla.LaneType.Sidewalk))
            # print("Current lane type: " + str(waypoint.lane_type))
            # # Check current lane change allowed
            # print("Current Lane change:  " + str(waypoint.lane_change))
            # # Left and Right lane markings
            # print("L lane marking type: " + str(waypoint.left_lane_marking.type))
            # print("L lane marking change: " + str(waypoint.left_lane_marking.lane_change))
            # print("R lane marking type: " + str(waypoint.right_lane_marking.type))
            # print("R lane marking change: " + str(waypoint.right_lane_marking.lane_change))
    finally:
        if ego_vehicle is not None:
            ego_vehicle.destroy()

# -- main() -------------------------------------------------------------

if __name__ == '__main__':
    main()
