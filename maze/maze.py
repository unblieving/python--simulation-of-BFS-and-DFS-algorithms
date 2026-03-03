#迷宫生成算法
import random
from collections import deque


class Maze:
    def __init__(self, width=21, height=21):  # 增加默认大小
        self.width = width if width % 2 == 1 else width + 1  # 确保是奇数
        self.height = height if height % 2 == 1 else height + 1
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.start = (1, 1)
        self.end = (self.width - 2, self.height - 2)

    def generate(self):
        """使用递归回溯算法生成复杂迷宫"""
        # 初始化网格
        for y in range(self.height):
            for x in range(self.width):
                if x % 2 == 0 or y % 2 == 0:
                    self.grid[y][x] = 1  # 墙
                else:
                    self.grid[y][x] = 0  # 潜在的通路

        # 递归回溯算法
        stack = []
        visited = set()

        # 随机起始点（奇数坐标）
        start_x = 1
        start_y = 1
        current = (start_x, start_y)
        visited.add(current)
        stack.append(current)

        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

        while stack:
            x, y = current

            # 获取未访问的邻居
            unvisited_neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (1 <= nx < self.width - 1 and 1 <= ny < self.height - 1 and
                        (nx, ny) not in visited):
                    unvisited_neighbors.append((dx, dy, nx, ny))

            if unvisited_neighbors:
                # 随机选择一个方向
                dx, dy, nx, ny = random.choice(unvisited_neighbors)

                # 打通墙壁
                wall_x, wall_y = x + dx // 2, y + dy // 2
                self.grid[wall_y][wall_x] = 0

                # 移动到新位置
                current = (nx, ny)
                visited.add(current)
                stack.append(current)
            else:
                # 回溯
                if stack:
                    current = stack.pop()

        # 设置起点和终点
        self.start = (1, 1)
        self.end = (self.width - 2, self.height - 2)
        self.grid[1][1] = 0
        self.grid[self.height - 2][self.width - 2] = 0

        # 添加额外的死胡同和环路增加复杂度
        self._add_complexity()

        # 确保有路径
        if not self._has_path(self.start, self.end):
            self._connect_areas()

        return self

    def _add_complexity(self):
        """添加额外的复杂度：随机打通一些墙壁创建环路"""
        # 随机打通一些墙壁（除了最外层）
        for _ in range(max(self.width, self.height) * 2):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)

            # 只打通墙壁，不通路
            if self.grid[y][x] == 1:
                # 检查是否连接两个不同的区域
                neighbors = []
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        neighbors.append(self.grid[ny][nx])

                # 如果连接两个通路，就打通
                if neighbors.count(0) >= 2:
                    self.grid[y][x] = 0

    def _connect_areas(self):
        """连接孤立的区域"""
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        regions = []

        # 找到所有区域
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 0 and not visited[y][x]:
                    region = self._flood_fill(x, y, visited)
                    if region:
                        regions.append(region)

        # 如果有多于一个区域，连接它们
        if len(regions) > 1:
            for i in range(len(regions) - 1):
                # 连接两个最近的区域
                region1 = regions[i]
                region2 = regions[i + 1]

                # 找到两个区域中最近的点
                min_dist = float('inf')
                best_wall = None

                for x1, y1 in region1:
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        x2, y2 = x1 + dx, y1 + dy
                        if 0 <= x2 < self.width and 0 <= y2 < self.height:
                            if self.grid[y2][x2] == 1:  # 如果是墙
                                # 检查墙的另一边
                                x3, y3 = x2 + dx, y2 + dy
                                if 0 <= x3 < self.width and 0 <= y3 < self.height:
                                    if (x3, y3) in region2:
                                        dist = abs(x1 - x3) + abs(y1 - y3)
                                        if dist < min_dist:
                                            min_dist = dist
                                            best_wall = (x2, y2)

                if best_wall:
                    wx, wy = best_wall
                    self.grid[wy][wx] = 0  # 打通墙壁

    def _flood_fill(self, x, y, visited):
        """洪水填充找到连通区域"""
        if visited[y][x] or self.grid[y][x] == 1:
            return []

        region = []
        stack = [(x, y)]

        while stack:
            cx, cy = stack.pop()
            if not visited[cy][cx] and self.grid[cy][cx] == 0:
                visited[cy][cx] = True
                region.append((cx, cy))

                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        stack.append((nx, ny))

        return region

    def _has_path(self, start, end):
        """检查是否有路径"""
        return self._bfs(start, end) is not None

    def _bfs(self, start, end):
        """BFS检查路径"""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        queue = deque([(start, [start])])
        visited = set([start])

        while queue:
            current, path = queue.popleft()
            if current == end:
                return path

            x, y = current
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                        self.grid[ny][nx] == 0 and (nx, ny) not in visited):
                    queue.append(((nx, ny), path + [(nx, ny)]))
                    visited.add((nx, ny))
        return None

    def __str__(self):
        """字符串表示"""
        result = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x, y) == self.start:
                    row.append('S')
                elif (x, y) == self.end:
                    row.append('E')
                elif self.grid[y][x] == 1:
                    row.append('#')
                else:
                    row.append('.')
            result.append(' '.join(row))
        return '\n'.join(result)



class BFSFinder:
    def __init__(self, maze):
        self.maze = maze
        self.visited = []
        self.path = []

    def find_path(self):
        """BFS寻路算法"""
        self.visited = []
        self.path = []

        start = self.maze.start
        end = self.maze.end
        grid = self.maze.grid

        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        queue = deque([(start, [start])])
        visited_set = set([start])

        while queue:
            current, path = queue.popleft()
            self.visited.append(current)

            if current == end:
                self.path = path
                return path

            x, y = current
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.maze.width and 0 <= ny < self.maze.height and
                        grid[ny][nx] == 0 and (nx, ny) not in visited_set):
                    queue.append(((nx, ny), path + [(nx, ny)]))
                    visited_set.add((nx, ny))

        return None


class DFSFinder:
    def __init__(self, maze):
        self.maze = maze
        self.visited = []
        self.path = []

    def find_path(self):
        """DFS寻路算法"""
        self.visited = []
        self.path = []

        start = self.maze.start
        end = self.maze.end
        grid = self.maze.grid

        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        stack = [(start, [start])]
        visited_set = set([start])

        while stack:
            current, path = stack.pop()
            self.visited.append(current)

            if current == end:
                self.path = path
                return path

            x, y = current
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.maze.width and 0 <= ny < self.maze.height and
                        grid[ny][nx] == 0 and (nx, ny) not in visited_set):
                    stack.append(((nx, ny), path + [(nx, ny)]))
                    visited_set.add((nx, ny))

        return None