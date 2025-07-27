"""
多机器人路径规划器

协调多个toio机器人的路径规划，避免路径冲突和碰撞
"""

import threading
import time
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from .collision_avoidance import CollisionAvoidanceSystem, Position
from .position_tracker import PositionTracker


class PlanningPriority(Enum):
    """路径规划优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    EMERGENCY = 4


@dataclass
class PathRequest:
    """路径规划请求"""
    robot_id: str
    start: Tuple[int, int]  # 世界坐标
    goal: Tuple[int, int]   # 世界坐标
    priority: PlanningPriority = PlanningPriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    timeout: float = 5.0    # 请求超时时间（秒）
    
    def is_expired(self) -> bool:
        """检查请求是否过期"""
        return time.time() - self.timestamp > self.timeout


@dataclass
class PathPlan:
    """路径规划结果"""
    robot_id: str
    path: List[Tuple[int, int]]  # 世界坐标路径
    estimated_time: float       # 估计执行时间（秒）
    created_time: float = field(default_factory=time.time)
    conflicts: List[str] = field(default_factory=list)  # 冲突的机器人ID列表


class PathPlanner:
    """多机器人路径规划器"""
    
    def __init__(self, collision_system: CollisionAvoidanceSystem, 
                 position_tracker: PositionTracker):
        """
        初始化路径规划器
        
        Args:
            collision_system: 避障系统
            position_tracker: 位置追踪器
        """
        self.collision_system = collision_system
        self.position_tracker = position_tracker
        
        # 规划请求队列
        self.planning_queue: List[PathRequest] = []
        self.queue_lock = threading.RLock()
        
        # 当前活跃路径
        self.active_paths: Dict[str, PathPlan] = {}
        self.paths_lock = threading.RLock()
        
        # 规划线程
        self.planning_thread = None
        self.running = False
        
        # 路径冲突解决
        self.conflict_resolution_enabled = True
        self.max_replanning_attempts = 3
        
        # 路径执行监控
        self.execution_monitor_enabled = True
        self.path_deviation_threshold = 20  # 毫米
        
        print("🗺️ 多机器人路径规划器初始化完成")
    
    def start_planner(self):
        """启动路径规划器"""
        if self.running:
            print("⚠️ 路径规划器已在运行中")
            return
        
        self.running = True
        self.planning_thread = threading.Thread(target=self._planning_loop, daemon=True)
        self.planning_thread.start()
        print("🚀 路径规划器已启动")
    
    def stop_planner(self):
        """停止路径规划器"""
        if not self.running:
            return
        
        self.running = False
        if self.planning_thread:
            self.planning_thread.join(timeout=2.0)
        print("⏹️ 路径规划器已停止")
    
    def request_path(self, robot_id: str, start: Tuple[int, int], goal: Tuple[int, int],
                    priority: PlanningPriority = PlanningPriority.NORMAL) -> bool:
        """
        请求路径规划
        
        Args:
            robot_id: 机器人ID
            start: 起点坐标
            goal: 终点坐标
            priority: 规划优先级
            
        Returns:
            是否成功添加到规划队列
        """
        request = PathRequest(
            robot_id=robot_id,
            start=start,
            goal=goal,
            priority=priority
        )
        
        with self.queue_lock:
            # 移除同一机器人的旧请求
            self.planning_queue = [req for req in self.planning_queue if req.robot_id != robot_id]
            
            # 添加新请求，按优先级排序
            self.planning_queue.append(request)
            self.planning_queue.sort(key=lambda r: r.priority.value, reverse=True)
        
        print(f"📋 添加路径规划请求: {robot_id} {start} -> {goal} (优先级: {priority.name})")
        return True
    
    def get_path(self, robot_id: str) -> Optional[List[Tuple[int, int]]]:
        """获取机器人的当前路径"""
        with self.paths_lock:
            plan = self.active_paths.get(robot_id)
            return plan.path.copy() if plan else None
    
    def cancel_path(self, robot_id: str):
        """取消机器人的路径规划"""
        with self.queue_lock:
            self.planning_queue = [req for req in self.planning_queue if req.robot_id != robot_id]
        
        with self.paths_lock:
            if robot_id in self.active_paths:
                del self.active_paths[robot_id]
                print(f"❌ 取消 {robot_id} 的路径规划")
    
    def _planning_loop(self):
        """路径规划主循环"""
        print("🗺️ 路径规划循环开始...")
        
        while self.running:
            try:
                # 处理规划请求
                self._process_planning_requests()
                
                # 监控路径执行
                if self.execution_monitor_enabled:
                    self._monitor_path_execution()
                
                # 清理过期数据
                self._cleanup_expired_data()
                
                time.sleep(0.1)  # 100ms循环间隔
                
            except Exception as e:
                print(f"❌ 路径规划异常: {e}")
                time.sleep(0.1)
        
        print("🗺️ 路径规划循环结束")
    
    def _process_planning_requests(self):
        """处理路径规划请求"""
        with self.queue_lock:
            if not self.planning_queue:
                return
            
            # 取出最高优先级请求
            request = self.planning_queue.pop(0)
        
        # 检查请求是否过期
        if request.is_expired():
            print(f"⏰ 路径规划请求过期: {request.robot_id}")
            return
        
        # 执行路径规划
        success = self._plan_path(request)
        
        if not success:
            print(f"❌ 路径规划失败: {request.robot_id}")
            
            # 如果是高优先级请求，尝试重新规划
            if request.priority in [PlanningPriority.HIGH, PlanningPriority.EMERGENCY]:
                request.timestamp = time.time()  # 更新时间戳
                with self.queue_lock:
                    self.planning_queue.insert(0, request)  # 重新加入队列头部
    
    def _plan_path(self, request: PathRequest) -> bool:
        """执行单个路径规划"""
        robot_id = request.robot_id
        
        # 获取当前位置（如果start不是当前位置，使用tracker的数据）
        current_pos = self.position_tracker.get_current_position(robot_id)
        if current_pos:
            start = current_pos
        else:
            start = request.start
        
        # 规划路径
        path = self.collision_system.plan_path(robot_id, start, request.goal)
        
        if not path:
            return False
        
        # 检查路径冲突
        conflicts = []
        if self.conflict_resolution_enabled:
            conflicts = self._detect_path_conflicts(robot_id, path)
        
        # 创建路径规划结果
        plan = PathPlan(
            robot_id=robot_id,
            path=path,
            estimated_time=self._estimate_execution_time(path),
            conflicts=conflicts
        )
        
        # 如果有冲突，尝试解决
        if conflicts and request.priority != PlanningPriority.EMERGENCY:
            resolved = self._resolve_path_conflicts(plan, request)
            if not resolved:
                print(f"⚠️ 无法解决路径冲突: {robot_id}, 冲突对象: {conflicts}")
                # 对于冲突无法解决的情况，仍然保存路径但标记冲突
        
        # 保存路径规划结果
        with self.paths_lock:
            self.active_paths[robot_id] = plan
        
        print(f"✅ 路径规划完成: {robot_id}, 路径点数: {len(path)}, 预计时间: {plan.estimated_time:.1f}s")
        return True
    
    def _detect_path_conflicts(self, robot_id: str, path: List[Tuple[int, int]]) -> List[str]:
        """检测路径冲突"""
        conflicts = []
        
        with self.paths_lock:
            for other_id, other_plan in self.active_paths.items():
                if other_id == robot_id:
                    continue
                
                # 检查路径是否有时空重叠
                if self._paths_intersect(path, other_plan.path):
                    conflicts.append(other_id)
        
        return conflicts
    
    def _paths_intersect(self, path1: List[Tuple[int, int]], path2: List[Tuple[int, int]]) -> bool:
        """检查两条路径是否相交"""
        # 简化的相交检测：检查是否有相同或相近的路径点
        for i, point1 in enumerate(path1):
            for j, point2 in enumerate(path2):
                # 计算距离
                distance = ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5
                
                if distance < 50:  # 50mm安全距离
                    # 检查时间重叠（假设匀速运动）
                    time_diff = abs(i - j) * 0.5  # 假设每个路径点间隔0.5秒
                    if time_diff < 2.0:  # 2秒安全时间间隔
                        return True
        
        return False
    
    def _resolve_path_conflicts(self, plan: PathPlan, request: PathRequest) -> bool:
        """解决路径冲突"""
        if not plan.conflicts:
            return True
        
        attempts = 0
        while attempts < self.max_replanning_attempts:
            attempts += 1
            
            # 为冲突机器人重新规划路径（延迟或绕行）
            for conflict_robot in plan.conflicts:
                with self.paths_lock:
                    if conflict_robot in self.active_paths:
                        # 简单策略：为冲突机器人添加延迟
                        self._add_path_delay(conflict_robot, 1.0)  # 1秒延迟
            
            # 重新检查冲突
            new_conflicts = self._detect_path_conflicts(plan.robot_id, plan.path)
            plan.conflicts = new_conflicts
            
            if not new_conflicts:
                print(f"✅ 路径冲突已解决: {plan.robot_id}")
                return True
        
        print(f"❌ 无法解决路径冲突: {plan.robot_id}")
        return False
    
    def _add_path_delay(self, robot_id: str, delay_seconds: float):
        """为路径添加延迟"""
        with self.paths_lock:
            if robot_id in self.active_paths:
                plan = self.active_paths[robot_id]
                
                # 在路径开始处添加等待点
                if plan.path:
                    wait_point = plan.path[0]
                    delay_steps = int(delay_seconds / 0.5)  # 假设每步0.5秒
                    
                    # 在路径前添加重复的起始点作为等待
                    delayed_path = [wait_point] * delay_steps + plan.path
                    plan.path = delayed_path
                    plan.estimated_time += delay_seconds
                    
                    print(f"⏰ 为 {robot_id} 添加 {delay_seconds}s 延迟")
    
    def _monitor_path_execution(self):
        """监控路径执行情况"""
        with self.paths_lock:
            for robot_id, plan in list(self.active_paths.items()):
                current_pos = self.position_tracker.get_current_position(robot_id)
                
                if not current_pos or not plan.path:
                    continue
                
                # 检查是否偏离路径
                deviation = self._calculate_path_deviation(current_pos, plan.path)
                
                if deviation > self.path_deviation_threshold:
                    print(f"⚠️ {robot_id} 偏离路径 {deviation:.1f}mm，触发重新规划")
                    
                    # 触发重新规划
                    if plan.path:
                        goal = plan.path[-1]  # 使用原目标点
                        self.request_path(robot_id, current_pos, goal, PlanningPriority.HIGH)
                
                # 检查是否到达目标
                if plan.path and self._is_near_goal(current_pos, plan.path[-1]):
                    print(f"🎯 {robot_id} 已到达目标")
                    del self.active_paths[robot_id]
    
    def _calculate_path_deviation(self, current_pos: Tuple[int, int], 
                                 path: List[Tuple[int, int]]) -> float:
        """计算当前位置与路径的偏差"""
        if not path:
            return float('inf')
        
        # 找到路径上最近的点
        min_distance = float('inf')
        for point in path:
            distance = ((current_pos[0] - point[0])**2 + (current_pos[1] - point[1])**2)**0.5
            min_distance = min(min_distance, distance)
        
        return min_distance
    
    def _is_near_goal(self, current_pos: Tuple[int, int], goal: Tuple[int, int], 
                     threshold: float = 15.0) -> bool:
        """检查是否接近目标"""
        distance = ((current_pos[0] - goal[0])**2 + (current_pos[1] - goal[1])**2)**0.5
        return distance <= threshold
    
    def _estimate_execution_time(self, path: List[Tuple[int, int]]) -> float:
        """估计路径执行时间"""
        if len(path) < 2:
            return 0.0
        
        total_distance = 0
        for i in range(1, len(path)):
            prev_point = path[i-1]
            curr_point = path[i]
            distance = ((curr_point[0] - prev_point[0])**2 + (curr_point[1] - prev_point[1])**2)**0.5
            total_distance += distance
        
        # 假设平均速度为50mm/s
        average_speed = 50.0  # mm/s
        return total_distance / average_speed
    
    def _cleanup_expired_data(self):
        """清理过期数据"""
        current_time = time.time()
        
        # 清理过期的活跃路径（超过预计时间很久的）
        with self.paths_lock:
            expired_robots = []
            for robot_id, plan in self.active_paths.items():
                age = current_time - plan.created_time
                if age > plan.estimated_time + 30.0:  # 超过预计时间30秒
                    expired_robots.append(robot_id)
            
            for robot_id in expired_robots:
                del self.active_paths[robot_id]
                print(f"🗑️ 清理过期路径: {robot_id}")
        
        # 清理过期的规划请求
        with self.queue_lock:
            self.planning_queue = [req for req in self.planning_queue if not req.is_expired()]
    
    def get_planner_status(self) -> Dict[str, Any]:
        """获取规划器状态"""
        with self.queue_lock:
            queue_count = len(self.planning_queue)
        
        with self.paths_lock:
            active_count = len(self.active_paths)
            active_robots = list(self.active_paths.keys())
        
        return {
            "running": self.running,
            "queue_size": queue_count,
            "active_paths": active_count,
            "active_robots": active_robots,
            "conflict_resolution": self.conflict_resolution_enabled,
            "execution_monitoring": self.execution_monitor_enabled
        }
    
    def emergency_stop_all(self):
        """紧急停止所有路径规划"""
        with self.queue_lock:
            self.planning_queue.clear()
        
        with self.paths_lock:
            self.active_paths.clear()
        
        print("🚨 紧急停止所有路径规划")
    
    def set_conflict_resolution(self, enabled: bool):
        """设置冲突解决功能"""
        self.conflict_resolution_enabled = enabled
        print(f"🔧 路径冲突解决: {'启用' if enabled else '禁用'}")
    
    def set_execution_monitoring(self, enabled: bool):
        """设置路径执行监控"""
        self.execution_monitor_enabled = enabled
        print(f"🔧 路径执行监控: {'启用' if enabled else '禁用'}")
    
    def __del__(self):
        """析构函数"""
        if self.running:
            self.stop_planner()