"""
toio机器人避障系统 - A*算法核心模块

提供基于A*算法的路径规划，支持动态障碍物避障
"""

import math
import heapq
import threading
import time
from typing import List, Tuple, Dict, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class CellType(Enum):
    """网格单元类型"""
    FREE = "free"           # 空闲区域
    OBSTACLE = "obstacle"   # 静态障碍物
    ROBOT = "robot"         # 机器人占用
    RESERVED = "reserved"   # 路径预留


@dataclass
class GridCell:
    """网格单元"""
    x: int
    y: int
    cell_type: CellType = CellType.FREE
    cost: float = 1.0       # 通过代价
    robot_id: Optional[str] = None  # 占用的机器人ID


@dataclass
class Position:
    """位置坐标"""
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def distance_to(self, other: 'Position') -> float:
        """计算到另一个位置的距离"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def manhattan_distance_to(self, other: 'Position') -> int:
        """计算曼哈顿距离"""
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class RobotState:
    """机器人状态"""
    id: str
    position: Position
    target: Optional[Position] = None
    path: List[Position] = field(default_factory=list)
    moving: bool = False
    last_update: float = field(default_factory=time.time)
    safe_radius: int = 25  # 安全半径(毫米) - 对应50mm边长正方形


@dataclass
class PathNode:
    """A*算法路径节点"""
    position: Position
    g_cost: float = 0  # 从起点到当前节点的实际代价
    h_cost: float = 0  # 从当前节点到终点的启发式代价
    f_cost: float = 0  # 总代价 f = g + h
    parent: Optional['PathNode'] = None
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost


class CollisionAvoidanceSystem:
    """toio机器人避障系统"""
    
    def __init__(self, grid_size: int = 10):
        """
        初始化避障系统
        
        Args:
            grid_size: 网格大小(毫米)，默认10mm × 10mm
        """
        self.grid_size = grid_size
        
        # toio mat坐标范围 (45-455, 45-455)
        self.mat_min_x = 45
        self.mat_max_x = 455
        self.mat_min_y = 45
        self.mat_max_y = 455
        
        # 计算网格尺寸
        self.grid_width = (self.mat_max_x - self.mat_min_x) // grid_size
        self.grid_height = (self.mat_max_y - self.mat_min_y) // grid_size
        
        # 初始化网格地图
        self.grid: List[List[GridCell]] = []
        self._initialize_grid()
        
        # 机器人状态追踪
        self.robots: Dict[str, RobotState] = {}
        self.robot_lock = threading.RLock()
        
        # 静态障碍物定义（厨房边界等）
        self._setup_static_obstacles()
        
        print(f"🗺️ 避障系统初始化完成: {self.grid_width}×{self.grid_height} 网格 (每格{grid_size}mm)")
    
    def _initialize_grid(self):
        """初始化网格地图"""
        self.grid = []
        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                cell = GridCell(x=x, y=y)
                row.append(cell)
            self.grid.append(row)
    
    def _setup_static_obstacles(self):
        """设置静态障碍物（地图边界等）"""
        # 暂不设置静态障碍物，可以根据实际厨房布局添加
        pass
    
    def world_to_grid(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """世界坐标转换为网格坐标"""
        grid_x = (world_x - self.mat_min_x) // self.grid_size
        grid_y = (world_y - self.mat_min_y) // self.grid_size
        
        # 边界检查
        grid_x = max(0, min(grid_x, self.grid_width - 1))
        grid_y = max(0, min(grid_y, self.grid_height - 1))
        
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """网格坐标转换为世界坐标"""
        world_x = self.mat_min_x + grid_x * self.grid_size + self.grid_size // 2
        world_y = self.mat_min_y + grid_y * self.grid_size + self.grid_size // 2
        return world_x, world_y
    
    def update_robot_position(self, robot_id: str, world_x: int, world_y: int):
        """更新机器人位置"""
        with self.robot_lock:
            grid_x, grid_y = self.world_to_grid(world_x, world_y)
            new_position = Position(grid_x, grid_y)
            
            if robot_id in self.robots:
                # 清除旧位置
                old_pos = self.robots[robot_id].position
                self._clear_robot_from_grid(robot_id, old_pos)
                
                # 更新位置
                self.robots[robot_id].position = new_position
                self.robots[robot_id].last_update = time.time()
            else:
                # 新机器人
                self.robots[robot_id] = RobotState(
                    id=robot_id,
                    position=new_position
                )
            
            # 在网格中标记新位置
            self._mark_robot_on_grid(robot_id, new_position)
    
    def _clear_robot_from_grid(self, robot_id: str, position: Position):
        """从网格中清除机器人标记"""
        safe_radius_cells = self.robots[robot_id].safe_radius // self.grid_size
        
        for dy in range(-safe_radius_cells, safe_radius_cells + 1):
            for dx in range(-safe_radius_cells, safe_radius_cells + 1):
                gx, gy = position.x + dx, position.y + dy
                if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
                    cell = self.grid[gy][gx]
                    if cell.robot_id == robot_id:
                        cell.cell_type = CellType.FREE
                        cell.robot_id = None
    
    def _mark_robot_on_grid(self, robot_id: str, position: Position):
        """在网格中标记机器人位置"""
        safe_radius_cells = self.robots[robot_id].safe_radius // self.grid_size
        
        for dy in range(-safe_radius_cells, safe_radius_cells + 1):
            for dx in range(-safe_radius_cells, safe_radius_cells + 1):
                gx, gy = position.x + dx, position.y + dy
                if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
                    cell = self.grid[gy][gx]
                    if cell.cell_type == CellType.FREE:
                        cell.cell_type = CellType.ROBOT
                        cell.robot_id = robot_id
    
    def plan_path(self, robot_id: str, start_world: Tuple[int, int], 
                  goal_world: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        使用A*算法规划路径
        
        Args:
            robot_id: 机器人ID
            start_world: 起点世界坐标 (x, y)
            goal_world: 终点世界坐标 (x, y)
            
        Returns:
            路径点列表 (世界坐标)
        """
        # 转换为网格坐标
        start_grid = self.world_to_grid(start_world[0], start_world[1])
        goal_grid = self.world_to_grid(goal_world[0], goal_world[1])
        
        start_pos = Position(start_grid[0], start_grid[1])
        goal_pos = Position(goal_grid[0], goal_grid[1])
        
        # 临时清除当前机器人的占用标记（允许经过自己的位置）
        with self.robot_lock:
            if robot_id in self.robots:
                self._clear_robot_from_grid(robot_id, self.robots[robot_id].position)
        
        try:
            # 执行A*搜索
            path_nodes = self._astar_search(start_pos, goal_pos, robot_id)
            
            if not path_nodes:
                print(f"⚠️ 无法为 {robot_id} 找到从 {start_world} 到 {goal_world} 的路径")
                return []
            
            # 转换为世界坐标
            world_path = []
            for node in path_nodes:
                world_x, world_y = self.grid_to_world(node.position.x, node.position.y)
                world_path.append((world_x, world_y))
            
            # 更新机器人路径
            if robot_id in self.robots:
                self.robots[robot_id].path = [node.position for node in path_nodes]
                self.robots[robot_id].target = goal_pos
            
            print(f"🗺️ 为 {robot_id} 规划路径: {len(world_path)} 个路径点")
            return world_path
            
        finally:
            # 恢复机器人占用标记
            with self.robot_lock:
                if robot_id in self.robots:
                    self._mark_robot_on_grid(robot_id, self.robots[robot_id].position)
    
    def _astar_search(self, start: Position, goal: Position, robot_id: str) -> List[PathNode]:
        """A*搜索算法实现"""
        open_list = []
        closed_set = set()
        
        # 创建起始节点
        start_node = PathNode(position=start)
        start_node.g_cost = 0
        start_node.h_cost = start.manhattan_distance_to(goal)
        start_node.f_cost = start_node.g_cost + start_node.h_cost
        
        heapq.heappush(open_list, start_node)
        
        while open_list:
            current_node = heapq.heappop(open_list)
            
            if current_node.position in closed_set:
                continue
                
            closed_set.add(current_node.position)
            
            # 到达目标
            if current_node.position == goal:
                return self._reconstruct_path(current_node)
            
            # 检查邻居节点
            for neighbor_pos in self._get_neighbors(current_node.position):
                if neighbor_pos in closed_set:
                    continue
                
                # 检查是否可通行
                if not self._is_passable(neighbor_pos, robot_id):
                    continue
                
                # 计算代价
                move_cost = self._get_move_cost(current_node.position, neighbor_pos)
                tentative_g_cost = current_node.g_cost + move_cost
                
                # 创建邻居节点
                neighbor_node = PathNode(position=neighbor_pos)
                neighbor_node.g_cost = tentative_g_cost
                neighbor_node.h_cost = neighbor_pos.manhattan_distance_to(goal)
                neighbor_node.f_cost = neighbor_node.g_cost + neighbor_node.h_cost
                neighbor_node.parent = current_node
                
                heapq.heappush(open_list, neighbor_node)
        
        # 未找到路径
        return []
    
    def _get_neighbors(self, position: Position) -> List[Position]:
        """获取邻居位置（8方向）"""
        neighbors = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dx, dy in directions:
            new_x, new_y = position.x + dx, position.y + dy
            if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
                neighbors.append(Position(new_x, new_y))
        
        return neighbors
    
    def _is_passable(self, position: Position, robot_id: str) -> bool:
        """检查位置是否可通行"""
        if not (0 <= position.x < self.grid_width and 0 <= position.y < self.grid_height):
            return False
        
        cell = self.grid[position.y][position.x]
        
        # 障碍物不可通行
        if cell.cell_type == CellType.OBSTACLE:
            return False
        
        # 被其他机器人占用不可通行
        if cell.cell_type == CellType.ROBOT and cell.robot_id != robot_id:
            return False
        
        return True
    
    def _get_move_cost(self, from_pos: Position, to_pos: Position) -> float:
        """计算移动代价"""
        # 基础移动代价
        base_cost = from_pos.distance_to(to_pos)
        
        # 对角线移动代价更高
        if abs(from_pos.x - to_pos.x) == 1 and abs(from_pos.y - to_pos.y) == 1:
            base_cost *= 1.414  # sqrt(2)
        
        return base_cost
    
    def _reconstruct_path(self, goal_node: PathNode) -> List[PathNode]:
        """重构路径"""
        path = []
        current = goal_node
        
        while current:
            path.append(current)
            current = current.parent
        
        path.reverse()
        return path
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        with self.robot_lock:
            status = {
                "grid_size": f"{self.grid_width}×{self.grid_height}",
                "robots": {},
                "total_obstacles": 0
            }
            
            # 统计障碍物
            for row in self.grid:
                for cell in row:
                    if cell.cell_type == CellType.OBSTACLE:
                        status["total_obstacles"] += 1
            
            # 机器人状态
            for robot_id, robot in self.robots.items():
                world_pos = self.grid_to_world(robot.position.x, robot.position.y)
                status["robots"][robot_id] = {
                    "position": world_pos,
                    "moving": robot.moving,
                    "path_length": len(robot.path),
                    "last_update": time.time() - robot.last_update
                }
            
            return status
    
    def is_safe_to_move(self, robot_id: str, target_world: Tuple[int, int]) -> bool:
        """检查移动到目标位置是否安全"""
        target_grid = self.world_to_grid(target_world[0], target_world[1])
        target_pos = Position(target_grid[0], target_grid[1])
        
        with self.robot_lock:
            # 首先检查目标位置本身是否可通行
            if not self._is_passable(target_pos, robot_id):
                # 如果被其他机器人占用，检查该机器人是否很接近
                cell = self.grid[target_pos.y][target_pos.x]
                if cell.cell_type == CellType.ROBOT and cell.robot_id != robot_id:
                    # 获取占用该位置的机器人的实际坐标
                    occupying_robot = self.robots.get(cell.robot_id)
                    if occupying_robot:
                        # 计算实际世界坐标距离
                        actual_distance = ((target_world[0] - occupying_robot.position.x) ** 2 + 
                                         (target_world[1] - occupying_robot.position.y) ** 2) ** 0.5
                        
                        # 如果距离超过50mm（我们的安全区域），则认为是安全的
                        if actual_distance > 50:
                            print(f"🔍 {robot_id} 目标({target_world[0]}, {target_world[1]})与{cell.robot_id}距离{actual_distance:.1f}mm > 50mm，允许移动")
                            return True
                        else:
                            print(f"⚠️ {robot_id} 目标({target_world[0]}, {target_world[1]})与{cell.robot_id}距离{actual_distance:.1f}mm < 50mm，阻止移动")
                            return False
                return False
            
            return True
    
    def clear_robot(self, robot_id: str):
        """清除机器人（断开连接时调用）"""
        with self.robot_lock:
            if robot_id in self.robots:
                robot = self.robots[robot_id]
                self._clear_robot_from_grid(robot_id, robot.position)
                del self.robots[robot_id]
                print(f"🗑️ 清除机器人 {robot_id} 的避障数据")