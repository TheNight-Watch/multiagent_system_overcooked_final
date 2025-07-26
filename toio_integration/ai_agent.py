#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
High-level AI Agent API for controlling toio cubes.
This module provides a simplified interface for AI Agents to control toio cubes
without needing to know low-level details like coordinates or RGB values.
"""

import time
from typing import Dict, List, Optional, Tuple, Union
from controller import ToioController, CubeState
from toio.cube.api.motor import CubeLocation, Point


class ToioAIAgent:
    """
    A high-level agent interface for AI systems to control toio cubes.
    Provides semantic functions for locations, lights, and sounds.
    """
    
    def __init__(self, controller: Optional[ToioController] = None, num_cubes: int = 2, 
                 simulation_mode: bool = False, cube_names: Optional[List[str]] = None):
        """
        Initialize the AI Agent with a controller or create a new one
        
        Args:
            controller: Existing ToioController instance or None to create a new one
            num_cubes: Number of cubes to connect to if creating a new controller
            simulation_mode: Force simulation mode even if hardware might be available
            cube_names: Optional list of names to assign to cubes in order
        """
        try:
            if simulation_mode:
                # Create a controller with simulated cubes
                self.controller = ToioController(num_cubes=0)  # Connect to 0 real cubes
                # Then manually add simulated cubes
                for i in range(num_cubes):
                    cube_id = f"sim_cube_{i+1}"
                    # Create a simulated cube directly
                    self.controller._cubes[cube_id] = CubeState(
                        id=cube_id,
                        cube=None,
                        position=CubeLocation(point=Point(x=200, y=200), angle=0),
                        connected=True
                    )
                    print(f"Created simulated cube: {cube_id}")
            else:
                self.controller = controller if controller else ToioController(num_cubes=num_cubes)
        except Exception as e:
            print(f"Warning: Error during initialization: {e}")
            print("Falling back to simulation mode")
            # Create a controller with simulated cubes
            self.controller = ToioController(num_cubes=0)  # Connect to 0 real cubes
            # Then manually add simulated cubes
            for i in range(num_cubes):
                cube_id = f"sim_cube_{i+1}"
                # Create a simulated cube directly
                from toio.cube.api.motor import CubeLocation, Point
                from component.controller import CubeState
                self.controller._cubes[cube_id] = CubeState(
                    id=cube_id,
                    cube=None,
                    position=CubeLocation(point=Point(x=200, y=200), angle=0),
                    connected=True
                )
                print(f"Created simulated cube: {cube_id}")
                
        self.cubes = self.controller.get_cube_ids()
        
        # Dictionary mapping role names to cube IDs
        self.roles = {}
        
        # Dictionary mapping cube names to cube IDs (for named assignment)
        self.cube_names = {}
        
        # If cube names are provided, assign them to cubes in order
        if cube_names:
            self._assign_cube_names(cube_names)
        
        # Define location mappings (name -> coordinates)
        self.locations = {
            "kitchen": (150, 150),
            "living_room": (250, 250),
            "bedroom": (300, 150),
            "bathroom": (350, 250),
            "entrance": (200, 300),
            "dining_room": (200, 200),
            "office": (350, 350),
            "balcony": (100, 350),
            "center": (250, 250),
            "corner_top_left": (100, 100),
            "corner_top_right": (400, 100),
            "corner_bottom_left": (100, 400),
            "corner_bottom_right": (400, 400),
        }
        
        # Define light presets (name -> RGB)
        self.lights = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "purple": (255, 0, 255),
            "cyan": (0, 255, 255),
            "white": (255, 255, 255),
            "off": (0, 0, 0),
            "orange": (255, 165, 0),
            "pink": (255, 192, 203),
            "warm_white": (255, 223, 170),
            "cool_white": (220, 237, 255),
        }
        
        # Define sound presets (name -> sound ID)
        self.sounds = {
            "success": 1,
            "error": 2,
            "alert": 3,
            "notification": 4,
            "happy": 5,
            "sad": 6,
            "startup": 7,
            "shutdown": 8,
            "beep": 9,
            "chime": 10,
        }
        
        print(f"ToioAIAgent initialized with {len(self.cubes)} cubes")
        
        # Set default colors for cubes to easily identify them
        if len(self.cubes) > 0:
            self.set_light(self.cubes[0], "blue")
        if len(self.cubes) > 1:
            self.set_light(self.cubes[1], "green")
    
    def _assign_cube_names(self, cube_names: List[str]) -> None:
        """
        Internal method to assign names to cubes in order
        
        Args:
            cube_names: List of names to assign to cubes
        """
        for i, name in enumerate(cube_names):
            if i < len(self.cubes):
                cube_id = self.cubes[i]
                self.cube_names[name] = cube_id
                print(f"Assigned name '{name}' to cube {cube_id}")
            else:
                print(f"Warning: More names provided than available cubes. Skipping '{name}'")
    
    def assign_cube_name(self, name: str, cube_id: str) -> bool:
        """
        Assign a name to a specific cube
        
        Args:
            name: Name to assign to the cube
            cube_id: ID of the cube
            
        Returns:
            True if successful, False otherwise
        """
        if cube_id not in self.cubes:
            print(f"Error: Cube {cube_id} not found")
            return False
        
        # If this name is already assigned to another cube, unassign it
        if name in self.cube_names and self.cube_names[name] != cube_id:
            old_cube_id = self.cube_names[name]
            print(f"Warning: Name '{name}' was already assigned to cube {old_cube_id}")
        
        self.cube_names[name] = cube_id
        print(f"Assigned name '{name}' to cube {cube_id}")
        return True
    
    def get_cube_by_name(self, name: str) -> Optional[str]:
        """
        Get cube ID by cube name
        
        Args:
            name: Name of the cube
            
        Returns:
            Cube ID or None if name not found
        """
        if name not in self.cube_names:
            print(f"Error: No cube with name '{name}'")
            return None
        return self.cube_names[name]
    
    def assign_role_by_name(self, role_name: str, cube_name: str) -> bool:
        """
        Assign a role to a cube by its name
        
        Args:
            role_name: Name of the role to assign
            cube_name: Name of the cube to assign the role to
            
        Returns:
            True if successful, False otherwise
        """
        cube_id = self.get_cube_by_name(cube_name)
        if not cube_id:
            return False
        
        return self.assign_role(role_name, cube_id)
    
    def get_all_cube_names(self) -> Dict[str, str]:
        """
        Get all cube name assignments
        
        Returns:
            Dictionary mapping cube names to cube IDs
        """
        return self.cube_names.copy()
            
    def assign_role(self, role_name: str, cube_id: str) -> bool:
        """
        Assign a role to a specific cube
        
        Args:
            role_name: Name of the role to assign
            cube_id: ID of the cube to assign the role to
            
        Returns:
            True if successful, False otherwise
        """
        if cube_id not in self.cubes:
            print(f"Error: Cube {cube_id} not found")
            return False
            
        # If this role is already assigned to another cube, unassign it
        if role_name in self.roles and self.roles[role_name] != cube_id:
            old_cube_id = self.roles[role_name]
            print(f"Warning: Role '{role_name}' was already assigned to cube {old_cube_id}")
        
        # Assign the new role
        self.roles[role_name] = cube_id
        print(f"Assigned role '{role_name}' to cube {cube_id}")
        return True
    
    def assign_roles_with_names(self, role_assignments: Dict[str, str]) -> bool:
        """
        Assign multiple roles to cubes by their names in one call
        
        Args:
            role_assignments: Dictionary mapping role names to cube names
            
        Returns:
            True if all assignments successful, False if any failed
        """
        success = True
        for role_name, cube_name in role_assignments.items():
            if not self.assign_role_by_name(role_name, cube_name):
                success = False
        return success
        
    def get_cube_by_role(self, role_name: str) -> Optional[str]:
        """
        Get the cube ID for a given role
        
        Args:
            role_name: Name of the role
            
        Returns:
            Cube ID or None if the role is not assigned
        """
        if role_name not in self.roles:
            print(f"Error: No cube assigned to role '{role_name}'")
            return None
            
        return self.roles[role_name]
    
    def get_role(self, cube_id: str) -> Optional[str]:
        """
        Get the role assigned to a cube
        
        Args:
            cube_id: ID of the cube
            
        Returns:
            Role name or None if the cube has no assigned role
        """
        for role, cid in self.roles.items():
            if cid == cube_id:
                return role
        return None
        
    def get_all_roles(self) -> Dict[str, str]:
        """
        Get all role assignments
        
        Returns:
            Dictionary mapping role names to cube IDs
        """
        return self.roles.copy()
        
    def go_to_by_role(self, role_name: str, location: str) -> bool:
        """
        Move a cube with a specific role to a named location
        
        Args:
            role_name: Name of the role
            location: Name of the location (e.g., "kitchen")
            
        Returns:
            True if the move was successful, False otherwise
        """
        cube_id = self.get_cube_by_role(role_name)
        if not cube_id:
            return False
            
        return self.go_to(cube_id, location)
    
    def set_light_by_role(self, role_name: str, light: str) -> bool:
        """
        Set the light of a cube with a specific role
        
        Args:
            role_name: Name of the role
            light: Name of the light preset (e.g., "red")
            
        Returns:
            True if successful, False otherwise
        """
        cube_id = self.get_cube_by_role(role_name)
        if not cube_id:
            return False
            
        return self.set_light(cube_id, light)
    
    def play_sound_by_role(self, role_name: str, sound: str) -> bool:
        """
        Play a sound on a cube with a specific role
        
        Args:
            role_name: Name of the role
            sound: Name of the sound preset (e.g., "success")
            
        Returns:
            True if successful, False otherwise
        """
        cube_id = self.get_cube_by_role(role_name)
        if not cube_id:
            return False
            
        return self.play_sound(cube_id, sound)
        
    def get_position_name_by_role(self, role_name: str) -> Optional[str]:
        """
        Get the current named location of a cube with a specific role
        
        Args:
            role_name: Name of the role
            
        Returns:
            Name of the current location or None if not at a known location
        """
        cube_id = self.get_cube_by_role(role_name)
        if not cube_id:
            return None
            
        return self.get_position_name(cube_id)
    
    def go_to(self, cube_id: str, location: str) -> bool:
        """
        Move a cube to a named location
        
        Args:
            cube_id: ID of the cube to move
            location: Name of the location (e.g., "kitchen")
            
        Returns:
            True if the move was successful, False otherwise
        """
        if location not in self.locations:
            print(f"Unknown location: {location}")
            return False
            
        x, y = self.locations[location]
        print(f"Moving cube {cube_id} to {location} ({x}, {y})")
        
        return self.controller.move_to(cube_id, x, y)
    
    def set_light(self, cube_id: str, light: str) -> bool:
        """
        Set a cube's light to a named color
        
        Args:
            cube_id: ID of the cube
            light: Name of the light preset (e.g., "red")
            
        Returns:
            True if successful, False otherwise
        """
        if light not in self.lights:
            print(f"Unknown light preset: {light}")
            return False
            
        r, g, b = self.lights[light]
        print(f"Setting cube {cube_id} light to {light} ({r}, {g}, {b})")
        
        self.controller.set_led(cube_id, r, g, b)
        return True
    
    def play_sound(self, cube_id: str, sound: str) -> bool:
        """
        Play a named sound on a cube
        
        Args:
            cube_id: ID of the cube
            sound: Name of the sound preset (e.g., "success")
            
        Returns:
            True if successful, False otherwise
        """
        if sound not in self.sounds:
            print(f"Unknown sound preset: {sound}")
            return False
            
        sound_id = self.sounds[sound]
        print(f"Playing {sound} sound on cube {cube_id}")
        
        self.controller.play_sound(cube_id, sound_id)
        return True
    
    def add_location(self, name: str, x: int, y: int) -> None:
        """
        Add a new named location
        
        Args:
            name: Name for the location
            x: X coordinate
            y: Y coordinate
        """
        self.locations[name] = (x, y)
        print(f"Added location '{name}' at coordinates ({x}, {y})")
    
    def add_light(self, name: str, r: int, g: int, b: int) -> None:
        """
        Add a new named light preset
        
        Args:
            name: Name for the light preset
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        self.lights[name] = (r, g, b)
        print(f"Added light preset '{name}' with RGB({r}, {g}, {b})")
    
    def add_sound(self, name: str, sound_id: int) -> None:
        """
        Add a new named sound preset
        
        Args:
            name: Name for the sound preset
            sound_id: Sound ID (1-10)
        """
        if not 1 <= sound_id <= 10:
            print(f"Warning: Sound ID {sound_id} is out of range (1-10)")
        
        self.sounds[name] = sound_id
        print(f"Added sound preset '{name}' with ID {sound_id}")
    
    def get_position_name(self, cube_id: str) -> Optional[str]:
        """
        Get the current named location of a cube
        
        Args:
            cube_id: ID of the cube
            
        Returns:
            Name of the current location or None if not at a known location
        """
        position = self.controller.get_position(cube_id)
        if not position:
            return None
            
        # Check if the cube is at a known location
        for location_name, (loc_x, loc_y) in self.locations.items():
            # Check if we're within a reasonable distance of the location
            distance = ((position.point.x - loc_x) ** 2 + (position.point.y - loc_y) ** 2) ** 0.5
            if distance < 30:  # Within 30 units
                return location_name
                
        return None
    
    def get_all_locations(self) -> Dict[str, Tuple[int, int]]:
        """
        Get all available named locations
        
        Returns:
            Dictionary of location names to coordinates
        """
        return self.locations
    
    def get_all_lights(self) -> Dict[str, Tuple[int, int, int]]:
        """
        Get all available light presets
        
        Returns:
            Dictionary of light names to RGB values
        """
        return self.lights
    
    def get_all_sounds(self) -> Dict[str, int]:
        """
        Get all available sound presets
        
        Returns:
            Dictionary of sound names to sound IDs
        """
        return self.sounds
    
    def get_cubes(self) -> List[str]:
        """
        Get IDs of all connected cubes
        
        Returns:
            List of cube IDs
        """
        return self.controller.get_cube_ids()
    
    def close(self) -> None:
        """Close the connection to all cubes"""
        self.controller.close()
        print("Disconnected from all cubes")


def run_demo():
    """Run a simple demo of the ToioAIAgent"""
    print("🤖 Toio AI Agent API Demo")
    print("-" * 50)
    
    # Initialize the agent
    agent = ToioAIAgent(num_cubes=2)
    
    try:
        cubes = agent.get_cubes()
        if not cubes:
            print("No cubes connected. Exiting.")
            return
        
        # Print all available locations
        print("\nAvailable locations:")
        for name, (x, y) in agent.get_all_locations().items():
            print(f"- {name}: ({x}, {y})")
        
        # Demo with first cube
        cube_id = cubes[0]
        
        # Move to kitchen with success light and sound
        print(f"\nMoving {cube_id} to kitchen...")
        success = agent.go_to(cube_id, "kitchen")
        if success:
            agent.set_light(cube_id, "green")
            agent.play_sound(cube_id, "success")
            print(f"Now at: {agent.get_position_name(cube_id)}")
        else:
            agent.set_light(cube_id, "red")
            agent.play_sound(cube_id, "error")
        
        time.sleep(2)
        
        # Move to living room
        print(f"\nMoving {cube_id} to living room...")
        success = agent.go_to(cube_id, "living_room")
        if success:
            agent.set_light(cube_id, "blue")
            agent.play_sound(cube_id, "chime")
            print(f"Now at: {agent.get_position_name(cube_id)}")
        
        # If we have a second cube, demonstrate it too
        if len(cubes) > 1:
            cube_id2 = cubes[1]
            
            # Move to entrance
            print(f"\nMoving {cube_id2} to entrance...")
            success = agent.go_to(cube_id2, "entrance")
            if success:
                agent.set_light(cube_id2, "purple")
                agent.play_sound(cube_id2, "notification")
                print(f"Now at: {agent.get_position_name(cube_id2)}")
        
        print("\nDemo complete!")
        
    finally:
        # Always close the agent to disconnect properly
        agent.close()


if __name__ == "__main__":
    run_demo()
