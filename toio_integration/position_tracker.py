"""
toio机器人位置追踪系统

实时监控所有toio机器人的位置，为避障系统提供数据支持
"""

import threading
import time
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass
from .controller import ToioController


@dataclass
class PositionHistory:
    """位置历史记录"""
    timestamp: float
    x: int
    y: int
    
    def age(self) -> float:
        """获取记录年龄（秒）"""
        return time.time() - self.timestamp


class PositionTracker:
    """位置追踪器"""
    
    def __init__(self, toio_controller: ToioController, update_interval: float = 0.1):
        """
        初始化位置追踪器
        
        Args:
            toio_controller: toio控制器实例
            update_interval: 位置更新间隔（秒）
        """
        self.toio_controller = toio_controller
        self.update_interval = update_interval
        
        # 位置数据
        self.current_positions: Dict[str, Tuple[int, int]] = {}
        self.position_history: Dict[str, List[PositionHistory]] = {}
        self.position_lock = threading.RLock()
        
        # 回调函数
        self.position_callbacks: List[Callable[[str, int, int], None]] = []
        
        # 追踪线程
        self.tracking_thread = None
        self.running = False
        
        # 历史记录设置
        self.max_history_size = 50  # 最多保存50个历史位置
        self.max_history_age = 10.0  # 历史记录最大年龄（秒）
        
        print(f"📍 位置追踪器初始化完成，更新间隔: {update_interval}秒")
    
    def start_tracking(self):
        """开始位置追踪"""
        if self.running:
            print("⚠️ 位置追踪已在运行中")
            return
        
        self.running = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        print("🚀 位置追踪已启动")
    
    def stop_tracking(self):
        """停止位置追踪"""
        if not self.running:
            return
        
        self.running = False
        if self.tracking_thread:
            self.tracking_thread.join(timeout=2.0)
        print("⏹️ 位置追踪已停止")
    
    def _tracking_loop(self):
        """位置追踪主循环"""
        print("📍 位置追踪循环开始...")
        
        while self.running:
            try:
                # 获取所有cube的当前位置
                cubes = self.toio_controller.get_cubes()
                
                for cube_id, cube in cubes.items():
                    position = self.toio_controller.get_position(cube_id)
                    
                    if position and hasattr(position, 'point'):
                        x, y = position.point.x, position.point.y
                        self._update_position(cube_id, x, y)
                
                # 清理过期的历史记录
                self._cleanup_history()
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"❌ 位置追踪异常: {e}")
                time.sleep(self.update_interval)
        
        print("📍 位置追踪循环结束")
    
    def _update_position(self, cube_id: str, x: int, y: int):
        """更新机器人位置"""
        with self.position_lock:
            # 检查位置是否发生变化
            current_pos = self.current_positions.get(cube_id)
            if current_pos == (x, y):
                return  # 位置未变化，跳过更新
            
            # 更新当前位置
            self.current_positions[cube_id] = (x, y)
            
            # 添加到历史记录
            if cube_id not in self.position_history:
                self.position_history[cube_id] = []
            
            self.position_history[cube_id].append(
                PositionHistory(timestamp=time.time(), x=x, y=y)
            )
            
            # 限制历史记录数量
            if len(self.position_history[cube_id]) > self.max_history_size:
                self.position_history[cube_id] = self.position_history[cube_id][-self.max_history_size:]
        
        # 触发回调
        self._trigger_position_callbacks(cube_id, x, y)
    
    def _cleanup_history(self):
        """清理过期的历史记录"""
        current_time = time.time()
        
        with self.position_lock:
            for cube_id in list(self.position_history.keys()):
                history = self.position_history[cube_id]
                
                # 过滤掉过期的记录
                self.position_history[cube_id] = [
                    record for record in history
                    if current_time - record.timestamp <= self.max_history_age
                ]
                
                # 如果历史记录为空且cube不在当前位置中，删除该cube的记录
                if not self.position_history[cube_id] and cube_id not in self.current_positions:
                    del self.position_history[cube_id]
    
    def _trigger_position_callbacks(self, cube_id: str, x: int, y: int):
        """触发位置更新回调"""
        for callback in self.position_callbacks:
            try:
                callback(cube_id, x, y)
            except Exception as e:
                print(f"❌ 位置回调异常: {e}")
    
    def add_position_callback(self, callback: Callable[[str, int, int], None]):
        """添加位置更新回调函数"""
        self.position_callbacks.append(callback)
        print(f"📍 添加位置回调，总数: {len(self.position_callbacks)}")
    
    def remove_position_callback(self, callback: Callable[[str, int, int], None]):
        """移除位置更新回调函数"""
        if callback in self.position_callbacks:
            self.position_callbacks.remove(callback)
            print(f"📍 移除位置回调，总数: {len(self.position_callbacks)}")
    
    def get_current_position(self, cube_id: str) -> Optional[Tuple[int, int]]:
        """获取机器人当前位置"""
        with self.position_lock:
            return self.current_positions.get(cube_id)
    
    def get_all_positions(self) -> Dict[str, Tuple[int, int]]:
        """获取所有机器人的当前位置"""
        with self.position_lock:
            return self.current_positions.copy()
    
    def get_position_history(self, cube_id: str, max_age: float = None) -> List[PositionHistory]:
        """
        获取机器人位置历史
        
        Args:
            cube_id: 机器人ID
            max_age: 最大年龄（秒），None表示获取所有历史
            
        Returns:
            位置历史列表（按时间顺序）
        """
        with self.position_lock:
            if cube_id not in self.position_history:
                return []
            
            history = self.position_history[cube_id]
            
            if max_age is None:
                return history.copy()
            
            current_time = time.time()
            return [
                record for record in history
                if current_time - record.timestamp <= max_age
            ]
    
    def get_movement_vector(self, cube_id: str, time_window: float = 1.0) -> Optional[Tuple[float, float]]:
        """
        计算机器人在指定时间窗口内的移动向量
        
        Args:
            cube_id: 机器人ID
            time_window: 时间窗口（秒）
            
        Returns:
            移动向量 (dx, dy)，如果无法计算则返回None
        """
        history = self.get_position_history(cube_id, time_window)
        
        if len(history) < 2:
            return None
        
        # 使用最新和最旧的位置计算向量
        oldest = history[0]
        newest = history[-1]
        
        time_delta = newest.timestamp - oldest.timestamp
        if time_delta <= 0:
            return None
        
        dx = (newest.x - oldest.x) / time_delta
        dy = (newest.y - oldest.y) / time_delta
        
        return (dx, dy)
    
    def predict_position(self, cube_id: str, future_time: float = 0.5) -> Optional[Tuple[int, int]]:
        """
        预测机器人在未来时间的位置
        
        Args:
            cube_id: 机器人ID
            future_time: 未来时间（秒）
            
        Returns:
            预测位置 (x, y)
        """
        current_pos = self.get_current_position(cube_id)
        if not current_pos:
            return None
        
        movement_vector = self.get_movement_vector(cube_id)
        if not movement_vector:
            return current_pos  # 无移动趋势，返回当前位置
        
        # 基于当前位置和移动向量预测未来位置
        dx, dy = movement_vector
        predicted_x = int(current_pos[0] + dx * future_time)
        predicted_y = int(current_pos[1] + dy * future_time)
        
        return (predicted_x, predicted_y)
    
    def is_moving(self, cube_id: str, min_distance: float = 5.0, time_window: float = 1.0) -> bool:
        """
        判断机器人是否在移动
        
        Args:
            cube_id: 机器人ID
            min_distance: 最小移动距离（毫米）
            time_window: 检查时间窗口（秒）
            
        Returns:
            是否在移动
        """
        history = self.get_position_history(cube_id, time_window)
        
        if len(history) < 2:
            return False
        
        # 计算总移动距离
        total_distance = 0
        for i in range(1, len(history)):
            prev = history[i-1]
            curr = history[i]
            distance = ((curr.x - prev.x)**2 + (curr.y - prev.y)**2)**0.5
            total_distance += distance
        
        return total_distance >= min_distance
    
    def get_tracking_status(self) -> Dict[str, Any]:
        """获取追踪状态"""
        with self.position_lock:
            status = {
                "running": self.running,
                "update_interval": self.update_interval,
                "tracked_cubes": len(self.current_positions),
                "cubes": {}
            }
            
            for cube_id in self.current_positions:
                history_count = len(self.position_history.get(cube_id, []))
                moving = self.is_moving(cube_id)
                
                status["cubes"][cube_id] = {
                    "position": self.current_positions[cube_id],
                    "history_count": history_count,
                    "moving": moving
                }
            
            return status
    
    def force_position_update(self, cube_id: str, x: int, y: int):
        """强制更新位置（用于测试或手动校正）"""
        self._update_position(cube_id, x, y)
        print(f"🔧 强制更新 {cube_id} 位置: ({x}, {y})")
    
    def __del__(self):
        """析构函数，确保线程正确停止"""
        if self.running:
            self.stop_tracking()