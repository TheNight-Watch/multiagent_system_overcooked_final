# Toio Core Cube API Reference

This document provides a comprehensive overview of the APIs available through the `toio-py` library for controlling toio core cubes.

## Table of Contents

- [Battery API](#battery-api)
- [Button API](#button-api)
- [Configuration API](#configuration-api)
- [ID Information API](#id-information-api)
- [Indicator API](#indicator-api)
- [Motor API](#motor-api)
- [Sensor API](#sensor-api)
- [Sound API](#sound-api)

## Battery API

The Battery API allows you to check the battery level of the cube.

```python
async def read() -> Optional[BatteryInformation]
```

Reads the battery level. Returns a `BatteryInformation` object containing:
- `battery_level`: Battery level from 0 to 100

## Button API

The Button API lets you check the state of the button on top of the cube.

```python
async def read() -> Optional[ButtonInformation]
```

Reads the button state. Returns a `ButtonInformation` object containing:
- `state`: `ButtonState.PRESSED` or `ButtonState.RELEASED`

## ID Information API

The ID Information API provides information about the cube's position on a toio mat or when it's placed on a toio card.

```python
async def read() -> Optional[IdInformationResponseType]
```

Returns one of these response types:
- `PositionId`: Contains the cube's position on the mat
  - `center`: CubeLocation with point (x, y) and angle
  - `sensor`: CubeLocation with point (x, y) and angle
- `StandardId`: Contains the ID of a toio card
  - `value`: ID value
  - `angle`: Angle
- `PositionIdMissed`: Indicates the cube was removed from a mat
- `StandardIdMissed`: Indicates the cube was removed from a card

## Indicator API

The Indicator API controls the LED on top of the cube.

```python
async def turn_on(param: IndicatorParam)
```
Turns on the LED with specified color and duration.
- `param`: `IndicatorParam` containing:
  - `duration_ms`: Duration in milliseconds (0 for indefinite)
  - `color`: `Color` object with RGB values (0-255)

```python
async def repeated_turn_on(repeat: int, param_list: List[IndicatorParam])
```
Repeats a sequence of LED colors.
- `repeat`: Number of repetitions (0 for infinite)
- `param_list`: List of `IndicatorParam` for the sequence

```python
async def turn_off_all()
```
Turns off all LEDs.

```python
async def turn_off(indicator_id: int)
```
Turns off a specific LED.

## Motor API

The Motor API controls the movement of the cube.

```python
async def motor_control(left: int, right: int, duration_ms: Optional[int] = None)
```
Controls motors directly by specifying left and right motor speeds.
- `left`: Left motor speed (-255 to 255)
- `right`: Right motor speed (-255 to 255)
- `duration_ms`: Optional duration in milliseconds

```python
async def motor_control_target(timeout: int, movement_type: MovementType, speed: Speed, target: TargetPosition)
```
Moves the cube to a specified position on the mat.
- `timeout`: Timeout in seconds
- `movement_type`: Movement pattern (`MovementType.Linear`, `MovementType.Curve`, or `MovementType.CurveWithoutReverse`)
- `speed`: `Speed` object with max speed and acceleration type
- `target`: `TargetPosition` with target coordinates and rotation option

```python
async def motor_control_multiple_targets(timeout: int, movement_type: MovementType, speed: Speed, mode: WriteMode, target_list: List[TargetPosition])
```
Moves the cube through a sequence of positions.
- `timeout`: Timeout in seconds
- `movement_type`: Movement pattern
- `speed`: Speed parameters
- `mode`: `WriteMode.Overwrite` or `WriteMode.Append`
- `target_list`: List of target positions

```python
async def motor_control_acceleration(translation: int, acceleration: int, rotation_velocity: int, rotation_direction: AccelerationRotation, cube_direction: AccelerationDirection, priority: AccelerationPriority, duration_ms: int)
```
Controls motor with acceleration parameters.

### Motor Response Codes

When controlling motor movement, you can check the response code:

- `SUCCESS`: Operation completed successfully
- `ERROR_TIMEOUT`: Operation timed out
- `ERROR_ID_MISSED`: Position ID could not be detected
- `ERROR_INVALID_PARAMETER`: Invalid parameter
- `ERROR_INVALID_CUBE_STATE`: Invalid cube state
- `SUCCESS_WITH_OVERWRITE`: Operation completed successfully with overwrite
- `ERROR_NOT_SUPPORTED`: Operation not supported
- `ERROR_FAILED_TO_APPEND`: Failed to append operation

## Sensor API

The Sensor API provides access to the cube's sensors.

```python
async def read() -> Optional[SensorResponseType]
```
Reads sensor information.

```python
async def request_motion_information()
```
Requests motion detection information.

```python
async def request_posture_angle_information(data_type: PostureDataType)
```
Requests posture angle information.
- `data_type`: Type of data to return (`Euler`, `Quaternions`, or `HighPrecisionEuler`)

```python
async def request_magnetic_sensor_information()
```
Requests magnetic sensor information.

### Sensor Response Types

- `MotionDetectionData`: Contains information about:
  - `horizontal`: Horizontal detection
  - `collision`: Collision detection
  - `double_tap`: Double-tap detection
  - `posture`: Posture (Top, Bottom, Rear, Front, Right, Left)
  - `shake`: Shake level (0-10)
  
- `PostureAngleEulerData`: Contains Euler angles:
  - `roll`: X-axis rotation
  - `pitch`: Y-axis rotation
  - `yaw`: Z-axis rotation
  
- `MagneticSensorData`: Contains magnetic field information:
  - `state`: Magnet state
  - `strength`: Magnetic force strength
  - `x`, `y`, `z`: Magnetic force direction

## Sound API

The Sound API controls the cube's sounds.

```python
async def play_sound_effect(sound_id: SoundId, volume: int)
```
Plays a built-in sound effect.
- `sound_id`: ID of the sound effect (0-10)
- `volume`: Volume (0-255)

```python
async def play_midi(repeat: int, midi_notes: List[MidiNote])
```
Plays MIDI notes.
- `repeat`: Number of repetitions (0 for infinite)
- `midi_notes`: List of `MidiNote` objects containing:
  - `duration_ms`: Duration in milliseconds
  - `note`: MIDI note (0-127, or 128 for no sound)
  - `volume`: Volume (0-255)

```python
async def stop()
```
Stops all sounds.

## Configuration API

The Configuration API allows you to configure various settings of the cube.

```python
async def request_protocol_version()
```
Requests the BLE protocol version.

```python
async def set_id_notification(interval_ms: int, condition: NotificationCondition)
```
Sets ID notification settings.
- `interval_ms`: Notification interval in milliseconds
- `condition`: When to notify (`Always`, `ChangeDetection`, or `Periodic`)

```python
async def set_magnetic_sensor(function_type: MagneticSensorFunction, interval_ms: int, condition: MagneticSensorCondition)
```
Sets magnetic sensor settings.
- `function_type`: Type of function (`Disable`, `MagnetState`, or `MagneticForce`)
- `interval_ms`: Notification interval in milliseconds
- `condition`: When to notify (`Always` or `ChangeDetection`)

```python
async def set_posture_angle_detection(detection_type: PostureAngleDetectionType, interval_ms: int, condition: PostureAngleDetectionCondition)
```
Sets posture angle detection settings.
- `detection_type`: Type of detection (`Euler`, `Quaternions`, or `HighPrecisionEuler`)
- `interval_ms`: Notification interval in milliseconds
- `condition`: When to notify (`Always` or `ChangeDetection`)
