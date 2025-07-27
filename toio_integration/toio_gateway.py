# edge/toio_gateway.py

import asyncio
import json
import logging
import os
from typing import Dict, Optional

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from toio.cube import ToioCoreCube
from toio.cube.api.id_information import IdInformation, PositionId
from toio.cube.api.motor import MovementType, RotationOption, Speed, TargetPosition
from toio.scanner import BLEScanner
# 导入 BleakError 以便进行特定的异常捕获
from bleak.exc import BleakError

# 1. 配置日志系统
logger = logging.getLogger("toio_gateway")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s",
)

# 2. 加载配置
TOIO_NAMES_CONFIG = "toio_names_config.json"
TOIO_NAMES_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), TOIO_NAMES_CONFIG)

if not os.path.exists(TOIO_NAMES_CONFIG_PATH):
    logging.error(f"错误：配置文件 '{TOIO_NAMES_CONFIG_PATH}' 未找到！正在创建一个空文件。")
    with open(TOIO_NAMES_CONFIG_PATH, 'w') as f:
        json.dump({}, f)
    NAME_MAPPING = {}
else:
    with open(TOIO_NAMES_CONFIG_PATH) as f:
        NAME_MAPPING = json.load(f)

load_dotenv()

# --- MQTT 设置 ---
MQTT_BROKER="supos-ce-instance4.supos.app"
MQTT_PORT=1883
ROOT_TOPIC_HEAD = "toio"
COMMAND_TOPIC="toio/+/command"

STATE_TOPIC_TEMPLATE = os.getenv("STATE_TOPIC_TEMPLATE", "toio/{}/state")
EVENT_TOPIC_TEMPLATE = os.getenv("EVENT_TOPIC_TEMPLATE", "toio/{}/event")

logging.info(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
logging.info(f"Command Topic: {COMMAND_TOPIC}")
logging.info(f"Event Topic Template: {EVENT_TOPIC_TEMPLATE}")
logging.info(f"目标 Cube 名称: {list(NAME_MAPPING.keys())}")

class CubeManager:
    """
    一个 Actor，通过主动健康探测来管理单个 Toio Cube 的连接、状态和指令。
    """

    def __init__(self, address: str, gateway: 'ToioGateway'):
        self.address = address
        self.name = gateway.address_to_name_map.get(address.upper(), address)
        self.gateway = gateway
        self.queue = asyncio.Queue()
        self.cube: Optional[ToioCoreCube] = None
        self.main_task = asyncio.create_task(self._main_loop())
        logging.info(f"✅ Manager for {self.name} created and task started.")

    async def put_command(self, action: str, params: Dict):
        await self.queue.put((action, params))

    async def _is_physically_connected(self) -> bool:
        """
        通过主动探测（读取电池）来从“物理层面”检查连接。
        """
        if not self.cube or not self.cube.is_connect():
            return False
        try:
            await asyncio.wait_for(self.cube.api.battery.read(), timeout=2.0)
            return True
        except asyncio.TimeoutError:
            logging.warning(f"🩺 Health probe for {self.name} TIMED OUT. Physical link is likely down.")
            return False
        except BleakError as e:
            logging.warning(f"🩺 Health probe for {self.name} failed with BleakError: {e}. Physical link is down.")
            return False

    async def _ensure_connected(self) -> bool:
        """
        核心函数：通过主动探测来确保 Cube 处于可通信状态。如果断开则会阻塞并循环重连。
        """
        if await self._is_physically_connected():
            return True

        logging.warning(f"🔌 Manager({self.name}): Connection check failed. Attempting to reconnect...")
        await self.gateway._cleanup_cube_object(self.cube)
        self.cube = None

        while True:
            new_cube = await self.gateway._reconnect_single_cube(self.address)
            if new_cube:
                self.cube = new_cube
                logging.info(f"🔗 Manager({self.name}): Reconnection successful.")
                return True
            else:
                logging.error(f"❌ Manager({self.name}): Reconnect attempt failed. Retrying in 10 seconds...")
                await asyncio.sleep(10)

    # [修改] 重构主循环以实现更智能的错误处理和重连
    async def _main_loop(self):
        """Actor 的主工作循环。"""
        logging.info(f"Manager({self.name}): Main loop running.")
        while True:
            try:
                # 1. 首先确保连接，如果断开会在此阻塞直到重连成功
                if not await self._ensure_connected():
                    # 这个分支理论上不应该被走到，因为 _ensure_connected 会一直重试
                    continue

                # 2. 从队列中获取指令
                action, params = await self.queue.get()
                
                # 3. 执行指令
                status = await self.gateway._execute_toio_command(self.name, self.cube, action, params)

                # 4. 根据执行结果进行处理
                if status == "connection_error":
                    logging.warning(f"Manager({self.name}): Command '{action}' failed due to connection loss. Re-queueing and forcing reconnect.")
                    # 重新入队，等待重连后执行
                    await self.put_command(action, params)
                    # 主动清理 cube 对象，让下一次循环的 _ensure_connected 立即触发完整的重连流程
                    await self.gateway._cleanup_cube_object(self.cube)
                    self.cube = None
                elif status == "logic_error":
                    # 对于逻辑或参数错误，记录日志并丢弃指令，避免无限循环
                    logging.error(f"Manager({self.name}): Command '{action}' failed due to a logic/parameter error. Discarding command.")
                
                # 如果 status == "success"，则成功完成，无需额外操作
                self.queue.task_done()

            except asyncio.CancelledError:
                logging.info(f"Manager({self.name}) is shutting down.")
                break
            except Exception as e:
                logging.error(f"Manager({self.name}) main loop critical error: {e}", exc_info=True)
                if self.cube:
                    await self.gateway._cleanup_cube_object(self.cube)
                    self.cube = None
                await asyncio.sleep(5) # 避免在严重错误下快速循环

    async def shutdown(self):
        """平滑地关闭此 Manager。"""
        logging.info(f"Manager({self.name}): Shutdown initiated.")
        self.main_task.cancel()
        await asyncio.gather(self.main_task, return_exceptions=True)
        if self.cube:
            await self.gateway._cleanup_cube_object(self.cube)
        logging.info(f"Manager({self.name}): Shutdown complete.")

class ToioGateway:
    """
    总网关，现在是一个调度中心 (Dispatcher) 和服务提供者。
    """
    def __init__(self):
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.address_to_name_map = {v.upper(): k for k, v in NAME_MAPPING.items()}
        
        self.managers: Dict[str, CubeManager] = {}
        self._managers_lock = asyncio.Lock()

        self.command_handlers = {
            "motor_ctrl": self._handle_motor_ctrl,
            "stop": self._handle_stop,
            "move_to": self._handle_move_to,
            "set_led": self._handle_set_led,
            "play_sound": self._handle_play_sound,
        }

    # --- MQTT & Command Dispatch ---
    def start_mqtt(self):
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logging.info("MQTT client connecting...")

    async def _mqtt_loop(self):
        while True:
            try:
                self.mqtt_client.loop(timeout=0.1)
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"MQTT loop error: {e}", exc_info=True)
                await asyncio.sleep(5)

    def _on_mqtt_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            logging.info(f"Connected to MQTT Broker. Subscribing to: {COMMAND_TOPIC}")
            client.subscribe(COMMAND_TOPIC)
        else:
            logging.error(f"Failed to connect to MQTT, code: {rc}")

    def _on_mqtt_message(self, client, userdata, msg: mqtt.MQTTMessage):
        try:
            cube_name = msg.topic.split('/')[1]
            cube_address = next((addr for name, addr in NAME_MAPPING.items() if name == cube_name), None)
            
            if not cube_address:
                logging.warning(f"Unknown cube name in topic: {cube_name}")
                return
            
            payload = json.loads(msg.payload.decode())
            action, params = payload.get("action"), payload.get("params", {})
            if not action: return

            asyncio.create_task(self._dispatch_command(cube_address, action, params))
        except Exception as e:
            logging.error(f"Error processing MQTT message: {e}", exc_info=True)

    async def _dispatch_command(self, cube_address: str, action: str, params: Dict):
        """将指令分发给对应的 Manager，如果 Manager 不存在则创建它。"""
        async with self._managers_lock:
            if cube_address not in self.managers:
                self.managers[cube_address] = CubeManager(cube_address, self)
        
        await self.managers[cube_address].put_command(action, params)

    # --- BLE & Cube Action Execution (作为共享服务) ---

    def _publish_event(self, cube_name: str, action: str, status: str):
        """发布一个事件到 MQTT 主题。"""
        topic = EVENT_TOPIC_TEMPLATE.format(cube_name)
        payload = json.dumps({"action": action, "status": status})
        self.mqtt_client.publish(topic, payload)
        logging.info(f"Published event to '{topic}': {payload}")

    # [修改] 重构指令执行函数以返回更详细的状态，并区分连接错误和逻辑错误
    async def _execute_toio_command(self, cube_name: str, cube: ToioCoreCube, action: str, params: Dict) -> str:
        """
        执行一个具体的 toio 指令，并发布开始/结束事件，然后返回执行结果状态。
        返回 "success", "connection_error", 或 "logic_error"。
        """
        handler = self.command_handlers.get(action)
        if not handler:
            logging.warning(f"Unknown action '{action}' for cube {cube_name}")
            return "logic_error"  # 无效指令是逻辑错误，不应重试

        self._publish_event(cube_name, action, "start")
        
        status = "logic_error"  # 默认为逻辑错误
        try:
            logging.info(f"Executing '{action}' on {cube_name}...")
            await handler(cube, params)
            logging.info(f"Successfully executed '{action}' on {cube_name}.")
            status = "success"
        except BleakError as e:
            # 捕获特定的蓝牙连接错误
            logging.error(f"Execution of '{action}' on {cube_name} failed with BleakError: {e}", exc_info=False)
            status = "connection_error"
        except Exception as e:
            # 其他所有异常都视为逻辑/参数错误
            logging.error(f"Execution of '{action}' on {cube_name} failed with a logic/parameter error: {e}", exc_info=False)
            status = "logic_error"
        finally:
            # 无论成功与否，都发布 "done" 事件
            self._publish_event(cube_name, action, "done")
        
        return status

    async def _cleanup_cube_object(self, cube: Optional[ToioCoreCube]):
        """安全地断开一个 Cube 对象的连接。"""
        if not cube:
            return
        try:
            await cube.disconnect()
            logging.info(f"Disconnected from {cube.name}.")
        except Exception as e:
            logging.warning(f"Error during disconnect for {cube.name}: {e}")

    async def _scan_and_connect_initial(self) -> Dict[str, ToioCoreCube]:
        """仅在启动时扫描并连接所有目标 Cube。"""
        connected_cubes = {}
        target_addresses = set(addr.upper() for addr in NAME_MAPPING.values())
        if not target_addresses:
            return {}
        try:
            devices = await BLEScanner.scan(num=10, timeout=10) # 稍稍增加超时
            for device in devices:
                addr_upper = device.device.address.upper()
                if addr_upper in target_addresses:
                    cube = await self._connect_single_device(addr_upper, device)
                    if cube:
                        connected_cubes[addr_upper] = cube
                        await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Initial scan failed: {e}", exc_info=True)
        return connected_cubes

    async def _reconnect_single_cube(self, cube_address: str) -> Optional[ToioCoreCube]:
        """尝试扫描并连接一个指定的 Cube。这是提供给 Manager 的核心服务。"""
        try:
            devices = await BLEScanner.scan(num=10, timeout=10) # 稍稍增加超时
            for device in devices:
                if device.device.address.upper() == cube_address.upper():
                    logging.info(f"Found {self.address_to_name_map.get(cube_address.upper())} during targeted scan.")
                    return await self._connect_single_device(cube_address, device)
            logging.warning(f"Could not find {self.address_to_name_map.get(cube_address.upper(), cube_address)} in targeted scan.")
        except Exception as e:
            logging.error(f"Targeted reconnect for {cube_address} failed: {e}")
        return None

    def _create_id_handler(self, cube_name: str):
        """为状态上报创建闭包回调。"""
        def id_notification_handler(payload: bytearray):
            id_info = IdInformation.is_my_data(payload)
            if isinstance(id_info, PositionId):
                state_data = {"name": cube_name, "x": id_info.center.point.x, "y": id_info.center.point.y, "angle": id_info.center.angle}
                topic = STATE_TOPIC_TEMPLATE.format(cube_name)
                self.mqtt_client.publish(topic, json.dumps(state_data))
        return id_notification_handler

    async def _connect_single_device(self, address: str, device) -> Optional[ToioCoreCube]:
        """连接单个设备的底层实现。"""
        cube_name = self.address_to_name_map.get(address.upper(), address)
        try:
            cube = ToioCoreCube(device.interface)
            await asyncio.wait_for(cube.connect(), timeout=10) # 稍稍增加超时
            handler = self._create_id_handler(cube_name)
            await cube.api.id_information.register_notification_handler(handler)
            logging.info(f"✅ Connection to {cube_name} established.")
            return cube
        except Exception as e:
            logging.error(f"Failed to initialize connection for {cube_name}: {e}")
            return None

    # --- Main Application Lifecycle ---
    async def run(self):
        """主程序生命周期。"""
        mqtt_task = asyncio.create_task(self._mqtt_loop())
        self.start_mqtt()
        
        try:
            logging.info("Starting initial scan for cubes...")
            initial_cubes = await self._scan_and_connect_initial()
            async with self._managers_lock:
                for addr, cube in initial_cubes.items():
                    self.managers[addr] = CubeManager(addr, self)
                    self.managers[addr].cube = cube
            
            logging.info("Gateway is running. Waiting for MQTT commands or termination signal.")
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            logging.info("Main gateway task cancelled.")
        finally:
            logging.info("Gateway shutting down...")
            shutdown_tasks = [mgr.shutdown() for mgr in self.managers.values()]
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
            
            mqtt_task.cancel()
            await asyncio.gather(mqtt_task, return_exceptions=True)
            
            logging.info("Gateway has successfully shut down.")

    # --- Command Handlers (作为共享服务) ---
    async def _handle_stop(self, cube: ToioCoreCube, params: Dict):
        await cube.api.motor.motor_control(0, 0, 0)
    
    async def _handle_motor_ctrl(self, cube: ToioCoreCube, params: Dict):
        await cube.api.motor.motor_control(params.get("left", 0), params.get("right", 0), params.get("duration_ms", 0))
    
    async def _handle_move_to(self, cube: ToioCoreCube, params: Dict):
        target = TargetPosition.from_int(
                x=params.get("x", 0), 
                y=params.get("y", 0), 
                angle=params.get("angle", 0), 
                rotation_option=params.get("angle_type", int(RotationOption.WithoutRotation)))
        speed = Speed.from_int(max=params.get("speed", 100), speed_change_type=3)
        await cube.api.motor.motor_control_target(timeout=params.get("timeout", 5),
                                             movement_type=params.get("movement_type", 
                                             int(MovementType.CurveWithoutReverse)), 
                                             speed=speed,
                                             target=target)
    
    async def _handle_set_led(self, cube: ToioCoreCube, params: Dict):
        color = params.get("color", [255, 0, 0])
        await cube.api.indicator.turn_on((1, color[0], color[1], color[2]))

    async def _handle_play_sound(self, cube: ToioCoreCube, params: Dict):
        if params.get("volume", 0) == 0: await cube.api.sound.stop(); return
        sound_id, volume = params.get("sound_id", 0), params.get("volume", 50)
        if not (0 <= sound_id <= 10 and 0 <= volume <= 255):
            logging.error(f"Invalid sound params: id={sound_id}, vol={volume}"); return
        await cube.api.sound.play_sound_effect(sound_id, volume)

if __name__ == "__main__":
    gateway = ToioGateway()
    try:
        asyncio.run(gateway.run())
    except KeyboardInterrupt:
        logging.info("Shutdown requested by user (Ctrl+C).")
