import asyncio
import threading
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# 使用绝对导入来引用已安装的toio库，避免与本地toio/目录冲突
import sys
from pathlib import Path

# 确保导入已安装的toio库，而不是本地的toio目录
try:
    # 从已安装的toio.py库中导入
    import toio.scanner as toio_scanner
    import toio.cube as toio_cube
    from toio.scanner import BLEScanner
    from toio.cube import ToioCoreCube, IdInformation
    from toio.cube.api.id_information import PositionId
    from toio.cube.api.motor import (
        MovementType, Speed, SpeedChangeType, TargetPosition, CubeLocation, 
        Point, RotationOption, ResponseMotorControlTarget, MotorResponseCode,
        ResponseMotorControlMultipleTargets
    )
    from toio.cube.api.indicator import IndicatorParam, Color
except ImportError as e:
    print(f"❌ 无法导入toio.py库: {e}")
    print("❌ 请确保已正确安装toio.py: pip install toio-py")
    raise


@dataclass
class CubeState:
    """Holds the current state of a Toio cube"""
    id: str
    cube: ToioCoreCube
    position: Optional[CubeLocation] = None
    connected: bool = True


class ToioController:
    """
    A synchronous controller for toio core cubes that abstracts away the 
    asyncio-based toio-py library.
    """
    
    def __init__(self, num_cubes: int = 1, connect_timeout: float = 10.0):
        """
        Initialize the controller and connect to the specified number of cubes.
        
        Args:
            num_cubes: Number of cubes to connect to
            connect_timeout: Timeout in seconds for the connection process
        """
        self._cubes: Dict[str, CubeState] = {}
        self._event_loop = None
        self._thread = None
        self._running = False
        self._position_callbacks = {}
        self._motor_callbacks = {}
        
        # Target reservation system to prevent multiple cubes targeting same area
        self._reserved_targets: Dict[str, Tuple[int, int]] = {}  # cube_id -> (x, y)
        self._target_lock = threading.Lock()
        
        # Start the background thread with async event loop
        self._start_background_loop()
        
        # Connect to cubes
        try:
            self._connect_cubes(num_cubes, connect_timeout)
        except Exception as e:
            print(f"Warning: Failed to connect to cubes: {e}")
            print("Controller will continue in simulation mode.")
            # Create simulated cubes for testing without real hardware
            self._create_simulated_cubes(num_cubes)
        
    def _start_background_loop(self):
        """Start a background thread with an asyncio event loop"""
        self._running = True
        
        def run_event_loop():
            """Run the event loop in the background thread"""
            asyncio.set_event_loop(asyncio.new_event_loop())
            self._event_loop = asyncio.get_event_loop()
            
            async def keep_running():
                while self._running:
                    await asyncio.sleep(0.1)
            
            self._event_loop.run_until_complete(keep_running())
            
        self._thread = threading.Thread(target=run_event_loop, daemon=True)
        self._thread.start()
        
        # Wait for event loop to be ready
        while self._event_loop is None:
            time.sleep(0.1)
    
    def _create_simulated_cubes(self, num_cubes: int):
        """Create simulated cubes for testing without real hardware"""
        for i in range(num_cubes):
            cube_id = f"sim_cube_{i+1}"
            # Use a mock cube (None) that won't try to connect
            self._cubes[cube_id] = self._create_simulated_cube(cube_id)
            print(f"Created simulated cube: {cube_id}")
            
    def _create_simulated_cube(self, cube_id: str) -> CubeState:
        """Create a single simulated cube"""
        # 只在真实硬件不可用时创建仿真cube
        return CubeState(
            id=cube_id,
            cube=None,
            position=CubeLocation(point=Point(x=200, y=200), angle=0),
            connected=True
        )
    
    def _connect_cubes(self, num_cubes: int, timeout: float = 10.0):
        """Connect to the specified number of cubes"""
        if num_cubes <= 0:
            return
        
        future = asyncio.run_coroutine_threadsafe(
            self._async_connect_cubes(num_cubes, timeout), self._event_loop
        )
        
        try:
            # Wait for the connection to complete with timeout
            future.result(timeout=timeout + 5.0)  # Add 5 seconds to the scan timeout
        except Exception as e:
            # Cancel the future if it's still running
            future.cancel()
            raise e
    
    async def _async_connect_cubes(self, num_cubes: int, timeout: float = 10.0):
        """Asynchronously connect to the specified number of cubes"""
        print(f"Scanning for {num_cubes} toio cubes...")
        
        try:
            # Scan for cubes
            dev_list = await BLEScanner.scan(num=num_cubes, sort="rssi", timeout=timeout)
            
            if len(dev_list) == 0:
                raise RuntimeError("No toio cubes found during scan")
                
            if len(dev_list) < num_cubes:
                print(f"Warning: Only found {len(dev_list)} cubes out of {num_cubes} requested")
            
            # Connect to each cube
            for i, device in enumerate(dev_list[:num_cubes]):
                cube_id = f"cube_{i+1}"
                
                try:
                    cube = ToioCoreCube(device.interface)
                    await cube.connect()
                    
                    # Create cube state
                    self._cubes[cube_id] = CubeState(id=cube_id, cube=cube)
                    print(f"Connected to cube: {cube_id}")
                    
                    # Set up position notification handler
                    await self._setup_position_tracking(cube_id, cube)
                except Exception as e:
                    print(f"Failed to connect to {cube_id}: {e}")
        
        except Exception as e:
            print(f"Error during cube discovery: {e}")
            raise
    
    async def _setup_position_tracking(self, cube_id: str, cube: ToioCoreCube):
        """Set up position tracking for a cube"""
        if cube is None:  # Skip for simulated cubes
            return
            
        # Create a callback for this specific cube
        async def position_callback(payload: bytearray):
            id_info = IdInformation.is_my_data(payload)
            if isinstance(id_info, PositionId):
                cube_state = self._cubes.get(cube_id)
                if cube_state:
                    cube_state.position = id_info.center
        
        # Store the callback for later cleanup
        self._position_callbacks[cube_id] = position_callback
        
        # Register the notification handler
        await cube.api.id_information.register_notification_handler(position_callback)
        
        # Create a motor callback to track movement success
        async def motor_callback(payload: bytearray):
            motor_response = cube.api.motor.is_my_data(payload)
            if isinstance(motor_response, ResponseMotorControlTarget):
                # Store the success/failure for the most recent move command
                if cube_id in self._motor_callbacks:
                    # Success if response code is SUCCESS (0x00) or SUCCESS_WITH_OVERWRITE (0x05)
                    self._motor_callbacks[cube_id] = (
                        motor_response.response_code == MotorResponseCode.SUCCESS or
                        motor_response.response_code == MotorResponseCode.SUCCESS_WITH_OVERWRITE
                    )
        
        # Register the motor notification handler
        await cube.api.motor.register_notification_handler(motor_callback)
    
    def close(self):
        """Disconnect from all cubes and shut down the controller"""
        if not self._running:
            return
        
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._async_close(), self._event_loop
            )
            
            # Wait for disconnection to complete with a timeout
            future.result(timeout=5.0)
        except Exception as e:
            print(f"Warning: Error during disconnect: {e}")
        finally:
            # Stop the background thread
            self._running = False
            if self._thread:
                self._thread.join(timeout=2.0)
                self._thread = None
    
    async def _async_close(self):
        """Asynchronously disconnect from all cubes"""
        for cube_id, cube_state in self._cubes.items():
            if cube_state.connected and cube_state.cube is not None:
                try:
                    # Unregister notification handlers
                    if cube_id in self._position_callbacks:
                        await cube_state.cube.api.id_information.unregister_notification_handler(
                            self._position_callbacks[cube_id]
                        )
                        
                    # Disconnect
                    await cube_state.cube.disconnect()
                    print(f"Disconnected from cube: {cube_id}")
                except Exception as e:
                    print(f"Error disconnecting from {cube_id}: {e}")
                finally:
                    cube_state.connected = False
        
        self._cubes.clear()
        self._position_callbacks.clear()
        self._motor_callbacks.clear()
    
    def get_cubes(self) -> Dict[str, CubeState]:
        """Return a dictionary of connected cubes"""
        return {
            cube_id: cube_state 
            for cube_id, cube_state in self._cubes.items() 
            if cube_state.connected
        }
    
    def get_cube_ids(self) -> List[str]:
        """Return a list of connected cube IDs"""
        return list(self.get_cubes().keys())
    
    def move_to(
        self, 
        cube_id: str, 
        x: int, 
        y: int, 
        angle: int = 0,
        movement_type: MovementType = MovementType.Linear
    ) -> bool:
        """
        Move a cube to the specified position on the mat.
        
        Args:
            cube_id: ID of the cube to move
            x: X coordinate to move to
            y: Y coordinate to move to
            angle: Angle to rotate to (0-360 degrees)
            movement_type: Type of movement (Linear, Curve, etc.)
            
        Returns:
            True if the move was successful, False otherwise
        """
        cube_state = self._cubes.get(cube_id)
        if not cube_state or not cube_state.connected:
            print(f"Error: Cube {cube_id} not found or not connected")
            return False
            
        # If this is a simulated cube, just update the position and return success
        if cube_state.cube is None:
            print(f"Simulating movement of {cube_id} to ({x}, {y}, {angle}°)")
            cube_state.position = CubeLocation(point=Point(x=x, y=y), angle=angle)
            time.sleep(1)  # Simulate movement time
            return True
        
        # Set up for receiving move completion status
        self._motor_callbacks[cube_id] = None
        
        # Run the move command
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._async_move_to(cube_state.cube, x, y, angle, movement_type),
                self._event_loop
            )
            
            # Wait for the move command to be sent
            future.result(timeout=2.0)
            
            # Wait for move to complete (max 10 seconds)
            for _ in range(100):
                if cube_id in self._motor_callbacks and self._motor_callbacks[cube_id] is not None:
                    return self._motor_callbacks[cube_id]
                time.sleep(0.1)
                
            # Timeout - assume failure
            return False
            
        except Exception as e:
            print(f"Error moving cube {cube_id}: {e}")
            return False
    
    async def _async_move_to(
        self, 
        cube: ToioCoreCube, 
        x: int, 
        y: int, 
        angle: int, 
        movement_type: MovementType
    ):
        """Asynchronously move a cube to the specified position"""
        await cube.api.motor.motor_control_target(
            timeout=8,  # Increased timeout for slower movement
            movement_type=movement_type,
            speed=Speed(
                max=100,  # Reduced speed for safer collision avoidance
                speed_change_type=SpeedChangeType.AccelerationAndDeceleration
            ),
            target=TargetPosition(
                cube_location=CubeLocation(
                    point=Point(x=x, y=y), 
                    angle=angle
                ),
                rotation_option=RotationOption.AbsoluteOptimal,
            ),
        )
    
    def set_led(self, cube_id: str, r: int, g: int, b: int):
        """
        Set the LED color of a cube.
        
        Args:
            cube_id: ID of the cube
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        cube_state = self._cubes.get(cube_id)
        if not cube_state or not cube_state.connected:
            print(f"Error: Cube {cube_id} not found or not connected")
            return
            
        # If this is a simulated cube, just print the action
        if cube_state.cube is None:
            print(f"Simulating LED color for {cube_id}: RGB({r},{g},{b})")
            return
        
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._async_set_led(cube_state.cube, r, g, b),
                self._event_loop
            )
            
            future.result(timeout=2.0)
        except Exception as e:
            print(f"Error setting LED for cube {cube_id}: {e}")
    
    async def _async_set_led(self, cube: ToioCoreCube, r: int, g: int, b: int):
        """Asynchronously set the LED color of a cube"""
        color = Color(r=r, g=g, b=b)
        indicator_param = IndicatorParam(duration_ms=0, color=color)
        await cube.api.indicator.turn_on(indicator_param)
    
    def play_sound(self, cube_id: str, sound_effect: int, volume: int = 100):
        """
        Play a sound effect on a cube.
        
        Args:
            cube_id: ID of the cube
            sound_effect: Sound effect ID to play
            volume: Volume level (0-255)
        """
        cube_state = self._cubes.get(cube_id)
        if not cube_state or not cube_state.connected:
            print(f"Error: Cube {cube_id} not found or not connected")
            return
            
        # If this is a simulated cube, just print the action
        if cube_state.cube is None:
            print(f"Simulating sound effect {sound_effect} for {cube_id}")
            return
        
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._async_play_sound(cube_state.cube, sound_effect, volume),
                self._event_loop
            )
            
            future.result(timeout=2.0)
        except Exception as e:
            print(f"Error playing sound for cube {cube_id}: {e}")
    
    async def _async_play_sound(self, cube: ToioCoreCube, sound_effect: int, volume: int = 100):
        """Asynchronously play a sound effect on a cube"""
        await cube.api.sound.play_sound_effect(sound_effect, volume)
    
    def get_position(self, cube_id: str) -> Optional[CubeLocation]:
        """
        Get the current position of a cube.
        
        Args:
            cube_id: ID of the cube
            
        Returns:
            Current position of the cube, or None if unknown
        """
        cube_state = self._cubes.get(cube_id)
        if not cube_state or not cube_state.connected:
            print(f"Error: Cube {cube_id} not found or not connected")
            return None
        
        return cube_state.position
    
    def get_all_positions(self) -> Dict[str, Tuple[int, int]]:
        """
        Get current positions of all cubes.
        
        Returns:
            Dictionary mapping cube_id to (x, y) coordinates
        """
        positions = {}
        for cube_id, cube_state in self._cubes.items():
            if cube_state.connected and cube_state.position:
                pos = cube_state.position
                if hasattr(pos, 'point'):
                    positions[cube_id] = (pos.point.x, pos.point.y)
                else:
                    positions[cube_id] = (200, 200)  # Default position
        return positions
    
    def _check_path_collision(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                            exclude_cube: str, cube_size: int = 50) -> bool:
        """
        Check if the direct path from start to end would collide with other cubes.
        Considers the physical volume of cubes (25x25 pixels each).
        
        Args:
            start_pos: Starting position (x, y)
            end_pos: Target position (x, y)
            exclude_cube: Cube ID to exclude from collision check
            cube_size: Physical size of each cube in pixels (default: 25x25)
            
        Returns:
            True if collision detected, False if path is clear
        """
        other_positions = self.get_all_positions()
        
        # Remove the moving cube from collision check
        if exclude_cube in other_positions:
            del other_positions[exclude_cube]
        
        if not other_positions:
            return False  # No other cubes to collide with
        
        # Calculate safety radius considering cube physical size
        # Each cube is 25x25, so we need at least 25 pixels clearance plus some buffer
        safety_radius = cube_size + 15  # 25 + 15 = 40 pixels total safety distance
        
        # Check 1: Path collision with existing cube positions
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        
        for cube_id, (cube_x, cube_y) in other_positions.items():
            # Check if the moving cube's path intersects with the stationary cube's volume
            if self._path_intersects_cube_volume(start_pos, end_pos, (cube_x, cube_y), cube_size):
                print(f"⚠️  Path collision detected with {cube_id} volume at ({cube_x}, {cube_y})")
                return True
        
        # Check 2: Target position collision (multiple cubes targeting same area)
        for cube_id, (cube_x, cube_y) in other_positions.items():
            # Check if target cube volume overlaps with existing cube volume
            if self._cube_volumes_overlap(end_pos, (cube_x, cube_y), cube_size):
                print(f"⚠️  Target volume collision detected: target ({end_x}, {end_y}) overlaps with {cube_id} at ({cube_x}, {cube_y})")
                return True
        
        # Check 3: Reserved targets collision
        with self._target_lock:
            for reserved_cube, (reserved_x, reserved_y) in self._reserved_targets.items():
                if reserved_cube == exclude_cube:
                    continue
                if self._cube_volumes_overlap(end_pos, (reserved_x, reserved_y), cube_size):
                    print(f"⚠️  Target conflicts with reserved target of {reserved_cube} at ({reserved_x}, {reserved_y})")
                    return True
        
        return False
    
    def _path_intersects_cube_volume(self, path_start: Tuple[int, int], path_end: Tuple[int, int], 
                                   cube_center: Tuple[int, int], cube_size: int) -> bool:
        """
        Check if a path line intersects with a cube's physical volume.
        
        Args:
            path_start: Path start position (x, y)
            path_end: Path end position (x, y)
            cube_center: Center position of the cube (x, y)
            cube_size: Size of the cube (assuming square)
            
        Returns:
            True if path intersects cube volume, False otherwise
        """
        cube_x, cube_y = cube_center
        half_size = cube_size // 2
        
        # Define cube boundaries
        cube_left = cube_x - half_size
        cube_right = cube_x + half_size
        cube_top = cube_y - half_size
        cube_bottom = cube_y + half_size
        
        # Check if the line segment intersects with the cube rectangle
        return self._line_intersects_rectangle(
            path_start, path_end,
            cube_left, cube_top, cube_right, cube_bottom
        )
    
    def _cube_volumes_overlap(self, pos1: Tuple[int, int], pos2: Tuple[int, int], cube_size: int) -> bool:
        """
        Check if two cube volumes overlap.
        
        Args:
            pos1: Position of first cube (x, y)
            pos2: Position of second cube (x, y)
            cube_size: Size of each cube
            
        Returns:
            True if volumes overlap, False otherwise
        """
        x1, y1 = pos1
        x2, y2 = pos2
        half_size = cube_size // 2
        
        # Check if rectangles overlap
        return not (x1 + half_size < x2 - half_size or  # pos1 is to the left of pos2
                   x1 - half_size > x2 + half_size or   # pos1 is to the right of pos2
                   y1 + half_size < y2 - half_size or   # pos1 is above pos2
                   y1 - half_size > y2 + half_size)     # pos1 is below pos2
    
    def _line_intersects_rectangle(self, line_start: Tuple[int, int], line_end: Tuple[int, int],
                                 rect_left: int, rect_top: int, rect_right: int, rect_bottom: int) -> bool:
        """
        Check if a line segment intersects with a rectangle.
        
        Args:
            line_start: Start point of line (x, y)
            line_end: End point of line (x, y)
            rect_left, rect_top, rect_right, rect_bottom: Rectangle boundaries
            
        Returns:
            True if line intersects rectangle, False otherwise
        """
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Check if either endpoint is inside the rectangle
        if (rect_left <= x1 <= rect_right and rect_top <= y1 <= rect_bottom) or \
           (rect_left <= x2 <= rect_right and rect_top <= y2 <= rect_bottom):
            return True
        
        # Check if line intersects any of the four rectangle edges
        # Top edge
        if self._line_segments_intersect((x1, y1), (x2, y2), (rect_left, rect_top), (rect_right, rect_top)):
            return True
        # Bottom edge
        if self._line_segments_intersect((x1, y1), (x2, y2), (rect_left, rect_bottom), (rect_right, rect_bottom)):
            return True
        # Left edge
        if self._line_segments_intersect((x1, y1), (x2, y2), (rect_left, rect_top), (rect_left, rect_bottom)):
            return True
        # Right edge
        if self._line_segments_intersect((x1, y1), (x2, y2), (rect_right, rect_top), (rect_right, rect_bottom)):
            return True
        
        return False
    
    def _line_segments_intersect(self, p1: Tuple[int, int], p2: Tuple[int, int], 
                               p3: Tuple[int, int], p4: Tuple[int, int]) -> bool:
        """
        Check if two line segments intersect.
        
        Args:
            p1, p2: First line segment endpoints
            p3, p4: Second line segment endpoints
            
        Returns:
            True if segments intersect, False otherwise
        """
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    def _point_to_line_distance(self, point: Tuple[int, int], 
                              line_start: Tuple[int, int], line_end: Tuple[int, int]) -> float:
        """
        Calculate the shortest distance from a point to a line segment.
        
        Args:
            point: Point coordinates (x, y)
            line_start: Line start coordinates (x, y)
            line_end: Line end coordinates (x, y)
            
        Returns:
            Distance from point to line segment
        """
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Vector from line_start to line_end
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            # Line start and end are the same point
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        
        # Parameter t represents position along the line
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        # Closest point on line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Distance from point to closest point on line
        return ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5
    
    def _find_waypoint(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                      exclude_cube: str) -> Tuple[int, int]:
        """
        Find a safe waypoint to avoid collisions.
        
        Args:
            start_pos: Starting position (x, y)
            end_pos: Target position (x, y)
            exclude_cube: Cube ID to exclude from collision check
            
        Returns:
            Waypoint coordinates (x, y)
        """
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        
        # Calculate perpendicular offset
        dx = end_x - start_x
        dy = end_y - start_y
        length = (dx * dx + dy * dy) ** 0.5
        
        if length == 0:
            return end_pos
        
        # Normalized perpendicular vector
        perp_x = -dy / length
        perp_y = dx / length
        
        # Try offsets to both sides
        offset_distance = 80  # Distance to move perpendicular to the line
        
        # Waypoint is at the midpoint, offset perpendicular to the line
        mid_x = (start_x + end_x) // 2
        mid_y = (start_y + end_y) // 2
        
        # Try right side first
        waypoint1 = (int(mid_x + perp_x * offset_distance), int(mid_y + perp_y * offset_distance))
        waypoint2 = (int(mid_x - perp_x * offset_distance), int(mid_y - perp_y * offset_distance))
        
        # Choose the waypoint that's safer (fewer nearby cubes)
        positions = self.get_all_positions()
        if exclude_cube in positions:
            del positions[exclude_cube]
        
        def waypoint_safety(wp):
            min_dist = float('inf')
            for cube_pos in positions.values():
                dist = ((wp[0] - cube_pos[0]) ** 2 + (wp[1] - cube_pos[1]) ** 2) ** 0.5
                min_dist = min(min_dist, dist)
            return min_dist
        
        if waypoint_safety(waypoint1) >= waypoint_safety(waypoint2):
            chosen_waypoint = waypoint1
        else:
            chosen_waypoint = waypoint2
        
        # Ensure waypoint is within reasonable bounds (toio mat is typically 400x400)
        chosen_waypoint = (
            max(50, min(400, chosen_waypoint[0])),
            max(50, min(400, chosen_waypoint[1]))
        )
        
        print(f"🔄 Calculated waypoint: {chosen_waypoint}")
        return chosen_waypoint
    
    def _reserve_target(self, cube_id: str, target_pos: Tuple[int, int], cube_size: int = 50) -> bool:
        """
        Reserve a target position for a cube to prevent conflicts.
        Uses volume-based collision detection considering cube physical size.
        
        Args:
            cube_id: ID of the cube requesting the reservation
            target_pos: Target position (x, y)
            cube_size: Physical size of each cube in pixels
            
        Returns:
            True if reservation successful, False if target area is already reserved
        """
        with self._target_lock:
            # Check if target volume conflicts with existing reservations
            for reserved_cube, reserved_pos in self._reserved_targets.items():
                if reserved_cube == cube_id:
                    continue  # Skip self
                
                if self._cube_volumes_overlap(target_pos, reserved_pos, cube_size):
                    print(f"🚫 Target reservation failed: {cube_id} target {target_pos} volume overlaps with {reserved_cube} target {reserved_pos}")
                    return False
            
            # Check if target volume conflicts with current cube positions
            current_positions = self.get_all_positions()
            for other_cube, other_pos in current_positions.items():
                if other_cube == cube_id:
                    continue  # Skip self
                
                if self._cube_volumes_overlap(target_pos, other_pos, cube_size):
                    print(f"🚫 Target reservation failed: {cube_id} target {target_pos} volume overlaps with {other_cube} current position {other_pos}")
                    return False
            
            # Reserve the target
            self._reserved_targets[cube_id] = target_pos
            print(f"📌 Target reserved: {cube_id} -> {target_pos}")
            return True
    
    def _release_target(self, cube_id: str):
        """
        Release a cube's target reservation.
        
        Args:
            cube_id: ID of the cube to release reservation for
        """
        with self._target_lock:
            if cube_id in self._reserved_targets:
                released_target = self._reserved_targets.pop(cube_id)
                print(f"🔓 Target released: {cube_id} released {released_target}")
    
    def _find_alternative_target(self, original_target: Tuple[int, int], cube_id: str, 
                                cube_size: int = 100) -> Tuple[int, int]:
        """
        Find an alternative target position near the original target.
        Uses volume-based collision detection considering cube physical size.
        
        Args:
            original_target: Original target position (x, y)
            cube_id: ID of the cube needing alternative target
            cube_size: Physical size of each cube in pixels
            
        Returns:
            Alternative target position (x, y)
        """
        orig_x, orig_y = original_target
        
        # Calculate minimum safe distance (cube size + buffer)
        min_distance = cube_size + 10  # 25 + 10 = 35 pixels minimum
        
        # Try positions in a spiral pattern around the original target
        for radius in range(min_distance, min_distance * 4, 10):
            for angle_deg in range(0, 360, 30):  # Check every 30 degrees
                angle_rad = angle_deg * 3.14159 / 180
                alt_x = int(orig_x + radius * (angle_rad ** 0.5))  # Use sqrt for spiral
                alt_y = int(orig_y + radius * (1 - angle_rad ** 0.5))
                
                # Ensure within bounds (considering cube size)
                half_size = cube_size // 2
                alt_x = max(half_size + 10, min(400 - half_size - 10, alt_x))
                alt_y = max(half_size + 10, min(400 - half_size - 10, alt_y))
                
                alt_target = (alt_x, alt_y)
                
                # Check if this alternative target can be reserved
                if self._reserve_target(cube_id, alt_target, cube_size):
                    print(f"🔄 Alternative target found for {cube_id}: {original_target} -> {alt_target}")
                    return alt_target
        
        # If no alternative found, return original (will need waypoint navigation)
        print(f"⚠️  No alternative target found for {cube_id}, will use waypoint navigation")
        return original_target

    def move_to_safe(self, cube_id: str, x: int, y: int, angle: int = 0) -> bool:
        """
        Move a cube to the specified position with collision avoidance.
        Uses curve movement and dynamic collision checking.
        
        Args:
            cube_id: ID of the cube to move
            x: X coordinate to move to
            y: Y coordinate to move to
            angle: Angle to rotate to (0-360 degrees)
            
        Returns:
            True if the move was successful, False otherwise
        """
        cube_state = self._cubes.get(cube_id)
        if not cube_state or not cube_state.connected:
            print(f"Error: Cube {cube_id} not found or not connected")
            return False
        
        # Get current position
        current_pos = self.get_position(cube_id)
        if not current_pos or not hasattr(current_pos, 'point'):
            print(f"Error: Cannot get current position for {cube_id}")
            return False
        
        start_pos = (current_pos.point.x, current_pos.point.y)
        original_target = (x, y)
        
        print(f"🎯 {cube_id}: Planning safe move from {start_pos} to {original_target}")
        
        # Step 1: Check for immediate collision at target
        if self._target_has_collision(original_target, cube_id):
            print(f"🚫 Target position {original_target} is occupied, finding alternative...")
            alternative_target = self._find_safe_alternative_target(original_target, cube_id)
            if alternative_target:
                x, y = alternative_target
                print(f"🔄 Using alternative target: {alternative_target}")
            else:
                print(f"❌ No safe alternative target found for {cube_id}")
                return False
        
        end_pos = (x, y)
        
        try:
            # Step 2: Reserve the target to prevent other cubes from targeting it
            if not self._reserve_target(cube_id, end_pos):
                print(f"⚠️  Could not reserve target {end_pos}, proceeding with caution")
            
            # Step 3: Plan and execute safe movement
            return self._execute_safe_movement(cube_id, start_pos, end_pos, angle)
            
        finally:
            # Always release the target reservation when movement is complete
            self._release_target(cube_id)
    
    def _target_has_collision(self, target_pos: Tuple[int, int], exclude_cube: str, cube_size: int = 50) -> bool:
        """
        Check if a target position would cause collision with existing cubes or reservations.
        
        Args:
            target_pos: Target position to check
            exclude_cube: Cube to exclude from check
            cube_size: Size of cube in pixels
            
        Returns:
            True if collision detected, False if safe
        """
        # Check collision with current cube positions
        current_positions = self.get_all_positions()
        for cube_id, pos in current_positions.items():
            if cube_id == exclude_cube:
                continue
            if self._cube_volumes_overlap(target_pos, pos, cube_size):
                return True
        
        # Check collision with reserved targets
        with self._target_lock:
            for reserved_cube, reserved_pos in self._reserved_targets.items():
                if reserved_cube == exclude_cube:
                    continue
                if self._cube_volumes_overlap(target_pos, reserved_pos, cube_size):
                    return True
        
        return False
    
    def _find_safe_alternative_target(self, original_target: Tuple[int, int], cube_id: str, 
                                    cube_size: int = 50) -> Optional[Tuple[int, int]]:
        """
        Find a safe alternative target using a more systematic approach.
        
        Args:
            original_target: Original target position
            cube_id: Cube needing alternative target
            cube_size: Size of cube in pixels
            
        Returns:
            Safe alternative target or None if not found
        """
        orig_x, orig_y = original_target
        min_distance = cube_size + 15  # Minimum safe distance
        
        # Try concentric circles around the original target
        for radius in range(min_distance, min_distance * 3, 5):
            # Try 8 directions around the circle
            for angle_deg in [0, 45, 90, 135, 180, 225, 270, 315]:
                angle_rad = angle_deg * 3.14159 / 180
                alt_x = int(orig_x + radius * (angle_rad ** 0.5))
                alt_y = int(orig_y + radius * (1 - angle_rad ** 0.5))
                
                # Ensure within bounds
                half_size = cube_size // 2
                if (half_size + 10 <= alt_x <= 400 - half_size - 10 and 
                    half_size + 10 <= alt_y <= 400 - half_size - 10):
                    
                    alt_target = (alt_x, alt_y)
                    if not self._target_has_collision(alt_target, cube_id, cube_size):
                        return alt_target
        
        return None
    
    def _execute_safe_movement(self, cube_id: str, start_pos: Tuple[int, int], 
                             end_pos: Tuple[int, int], angle: int) -> bool:
        """
        Execute movement with real-time collision avoidance.
        
        Args:
            cube_id: ID of cube to move
            start_pos: Starting position
            end_pos: Target position
            angle: Target angle
            
        Returns:
            True if movement successful, False otherwise
        """
        # Check if direct path is safe
        if not self._check_path_collision(start_pos, end_pos, cube_id):
            print(f"✅ Direct path is clear for {cube_id}")
            # Use curve movement for smoother collision avoidance
            return self.move_to(cube_id, end_pos[0], end_pos[1], angle, MovementType.Curve)
        
        # Path is blocked, use multi-waypoint navigation
        print(f"🚧 Direct path blocked for {cube_id}, calculating safe route...")
        
        waypoints = self._calculate_safe_route(start_pos, end_pos, cube_id)
        if not waypoints:
            print(f"❌ Could not calculate safe route for {cube_id}")
            return False
        
        # Execute movement through waypoints
        current_pos = start_pos
        for i, waypoint in enumerate(waypoints):
            print(f"📍 {cube_id}: Moving to waypoint {i+1}/{len(waypoints)}: {waypoint}")
            
            # Use curve movement for smoother navigation
            success = self.move_to(cube_id, waypoint[0], waypoint[1], 0, MovementType.Curve)
            if not success:
                print(f"❌ Failed to reach waypoint {i+1} for {cube_id}")
                return False
            
            # Update current position and wait briefly
            current_pos = waypoint
            time.sleep(0.3)  # Shorter delay for smoother movement
        
        # Final move to target with desired angle
        print(f"🎯 {cube_id}: Final move to destination {end_pos}")
        return self.move_to(cube_id, end_pos[0], end_pos[1], angle, MovementType.Curve)
    
    def _calculate_safe_route(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                            cube_id: str, cube_size: int = 50) -> List[Tuple[int, int]]:
        """
        Calculate a safe route with multiple waypoints to avoid collisions.
        
        Args:
            start_pos: Starting position
            end_pos: Target position
            cube_id: ID of moving cube
            cube_size: Size of cube in pixels
            
        Returns:
            List of waypoints for safe navigation
        """
        # Get positions of other cubes
        other_positions = self.get_all_positions()
        if cube_id in other_positions:
            del other_positions[cube_id]
        
        if not other_positions:
            return []  # No obstacles, direct path should work
        
        # Find the primary obstacle
        primary_obstacle = self._find_primary_obstacle(start_pos, end_pos, other_positions, cube_size)
        if not primary_obstacle:
            return []
        
        obstacle_pos = primary_obstacle
        
        # Calculate waypoints that go around the obstacle
        waypoints = self._calculate_avoidance_waypoints(start_pos, end_pos, obstacle_pos, cube_size)
        
        # Validate waypoints don't create new collisions
        validated_waypoints = []
        for waypoint in waypoints:
            if not self._target_has_collision(waypoint, cube_id, cube_size):
                validated_waypoints.append(waypoint)
            else:
                # Try to adjust waypoint slightly
                adjusted = self._adjust_waypoint(waypoint, cube_id, cube_size)
                if adjusted:
                    validated_waypoints.append(adjusted)
        
        return validated_waypoints
    
    def _find_primary_obstacle(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                             other_positions: Dict[str, Tuple[int, int]], cube_size: int) -> Optional[Tuple[int, int]]:
        """
        Find the primary obstacle that blocks the direct path.
        
        Args:
            start_pos: Starting position
            end_pos: Target position
            other_positions: Positions of other cubes
            cube_size: Size of cube in pixels
            
        Returns:
            Position of primary obstacle or None
        """
        min_distance = float('inf')
        primary_obstacle = None
        
        for cube_id, pos in other_positions.items():
            if self._path_intersects_cube_volume(start_pos, end_pos, pos, cube_size):
                # Calculate distance from start to this obstacle
                distance = ((start_pos[0] - pos[0]) ** 2 + (start_pos[1] - pos[1]) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    primary_obstacle = pos
        
        return primary_obstacle
    
    def _calculate_avoidance_waypoints(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                                     obstacle_pos: Tuple[int, int], cube_size: int) -> List[Tuple[int, int]]:
        """
        Calculate waypoints to navigate around an obstacle.
        
        Args:
            start_pos: Starting position
            end_pos: Target position
            obstacle_pos: Position of obstacle to avoid
            cube_size: Size of cube in pixels
            
        Returns:
            List of waypoints
        """
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        obs_x, obs_y = obstacle_pos
        
        # Calculate avoidance distance (cube size + safety margin)
        avoidance_distance = cube_size + 20
        
        # Calculate vector from start to end
        dx = end_x - start_x
        dy = end_y - start_y
        
        # Calculate perpendicular vectors for left and right avoidance
        length = (dx * dx + dy * dy) ** 0.5
        if length == 0:
            return []
        
        perp_x = -dy / length
        perp_y = dx / length
        
        # Calculate two possible avoidance routes (left and right)
        left_waypoint = (
            int(obs_x + perp_x * avoidance_distance),
            int(obs_y + perp_y * avoidance_distance)
        )
        right_waypoint = (
            int(obs_x - perp_x * avoidance_distance),
            int(obs_y - perp_y * avoidance_distance)
        )
        
        # Choose the waypoint that's closer to the direct path
        def distance_to_line(point):
            return self._point_to_line_distance(point, start_pos, end_pos)
        
        if distance_to_line(left_waypoint) <= distance_to_line(right_waypoint):
            chosen_waypoint = left_waypoint
        else:
            chosen_waypoint = right_waypoint
        
        # Ensure waypoint is within bounds
        chosen_waypoint = (
            max(cube_size // 2 + 10, min(400 - cube_size // 2 - 10, chosen_waypoint[0])),
            max(cube_size // 2 + 10, min(400 - cube_size // 2 - 10, chosen_waypoint[1]))
        )
        
        return [chosen_waypoint]
    
    def _adjust_waypoint(self, waypoint: Tuple[int, int], cube_id: str, 
                        cube_size: int, max_attempts: int = 8) -> Optional[Tuple[int, int]]:
        """
        Try to adjust a waypoint to avoid collisions.
        
        Args:
            waypoint: Original waypoint
            cube_id: ID of moving cube
            cube_size: Size of cube in pixels
            max_attempts: Maximum adjustment attempts
            
        Returns:
            Adjusted waypoint or None if no safe position found
        """
        wp_x, wp_y = waypoint
        adjustment_distance = cube_size // 2 + 5
        
        # Try adjustments in 8 directions
        for i in range(max_attempts):
            angle = i * 45 * 3.14159 / 180  # 45-degree increments
            adj_x = int(wp_x + adjustment_distance * (angle ** 0.5))
            adj_y = int(wp_y + adjustment_distance * (1 - angle ** 0.5))
            
            # Ensure within bounds
            if (cube_size // 2 + 10 <= adj_x <= 400 - cube_size // 2 - 10 and
                cube_size // 2 + 10 <= adj_y <= 400 - cube_size // 2 - 10):
                
                adjusted_waypoint = (adj_x, adj_y)
                if not self._target_has_collision(adjusted_waypoint, cube_id, cube_size):
                    return adjusted_waypoint
        
        return None
