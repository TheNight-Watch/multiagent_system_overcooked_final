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
            timeout=5,  # 5 second timeout
            movement_type=movement_type,
            speed=Speed(
                max=115,  # Slightly faster for more reliable movement
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
