import pygame
import sys
import os
import random
import time

# 初始化pygame
pygame.init()


class MazeVisualizer:
    def __init__(self, maze, cell_size=40):
        self.maze = maze
        self.cell_size = cell_size

        # 窗口大小
        self.panel_width = 280
        self.window_width = maze.width * cell_size + self.panel_width
        self.window_height = maze.height * cell_size

        # 创建窗口
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Maze Path Finding - BFS vs DFS")

        print("初始化字体...")

        # 简单可靠的字体初始化
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 28)
            self.font_tiny = pygame.font.Font(None, 22)
            self.font_micro = pygame.font.Font(None, 18)
            print("✓ 使用pygame默认字体")
        except Exception as e:
            print(f"字体初始化失败: {e}")
            self.font_large = None
            self.font_medium = None
            self.font_small = None
            self.font_tiny = None
            self.font_micro = None

        # 颜色定义
        self.colors = {
            'background': (240, 240, 245),
            'wall': (40, 40, 60),
            'path': (255, 255, 255),
            'start': (50, 200, 50),
            'end': (220, 50, 50),
            'visited_bfs': (100, 150, 255),
            'visited_dfs': (180, 100, 255),
            'path_bfs': (255, 200, 50),
            'path_dfs': (200, 100, 255),
            'player': (255, 80, 80),
            'algorithm': (50, 150, 255),
            'text': (30, 30, 30),
            'panel_bg': (230, 235, 245),
            'button': (80, 140, 220),
            'button_hover': (100, 160, 240),
            'button2': (70, 180, 70),
            'button2_hover': (90, 200, 90),
            'button3': (220, 80, 80),
            'button3_hover': (240, 100, 100),
            'border': (200, 205, 220),
            'result_win': (50, 200, 50),
            'result_lose': (220, 50, 50)
        }

        # 游戏状态
        self.running = True
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.mode = 'menu'
        self.menu_buttons = []

        # 算法数据
        self.bfs_path = []
        self.dfs_path = []
        self.bfs_visited = []
        self.dfs_visited = []
        self.bfs_step = 0
        self.dfs_step = 0
        self.demo_speed = 0.1
        self.demo_playing = True
        self.demo_paused = False
        self.demo_finished = False
        self.demo_end_time = 0

        # 比赛模式数据
        self.player_pos = maze.start
        self.algorithm_pos = maze.start
        self.player_steps = 0
        self.algorithm_steps = 0
        self.race_started = False
        self.race_finished = False
        self.winner = None
        self.algorithm_path = []
        self.algorithm_index = 0
        self.last_algorithm_move = 0

        # 菜单状态
        self.demo_menu_buttons = []
        self.game_over_buttons = []
        self.show_demo_end_menu = False
        self.show_game_over_menu = False
        self.game_over_time = 0
        self.race_start_time = 0

        print("✓ 可视化器初始化完成")

    def draw_text(self, text, font, color, position, centered=False, max_width=None):
        """安全的文字绘制函数，支持自动换行"""
        if font is None or text == "":
            return

        try:
            # 如果指定了最大宽度，处理换行
            if max_width:
                words = text.split(' ')
                lines = []
                current_line = []

                for word in words:
                    test_line = ' '.join(current_line + [word])
                    test_width = font.size(test_line)[0]

                    if test_width <= max_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]

                if current_line:
                    lines.append(' '.join(current_line))

                # 绘制多行文本
                total_height = len(lines) * (font.get_height() + 2)
                start_y = position[1] - total_height // 2 if centered else position[1]

                for i, line in enumerate(lines):
                    line_surface = font.render(line, True, color)
                    if centered:
                        line_rect = line_surface.get_rect(center=(position[0], start_y + i * (font.get_height() + 2)))
                        self.screen.blit(line_surface, line_rect)
                    else:
                        self.screen.blit(line_surface, (position[0], start_y + i * (font.get_height() + 2)))
                return

            # 单行文本
            text_surface = font.render(text, True, color)
            if centered:
                text_rect = text_surface.get_rect(center=position)
                self.screen.blit(text_surface, text_rect)
            else:
                self.screen.blit(text_surface, position)

        except Exception as e:
            print(f"文字渲染失败: {e}")

    def draw_maze(self):
        """绘制迷宫基础"""
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

                # 确定颜色
                if (x, y) == self.maze.start:
                    color = self.colors['start']
                elif (x, y) == self.maze.end:
                    color = self.colors['end']
                elif self.maze.grid[y][x] == 1:
                    color = self.colors['wall']
                else:
                    color = self.colors['path']

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.colors['border'], rect, 1)

                # 标记起点和终点
                if (x, y) == self.maze.start:
                    self.draw_text("S", self.font_small, (255, 255, 255),
                                   rect.center, centered=True)
                elif (x, y) == self.maze.end:
                    self.draw_text("E", self.font_small, (255, 255, 255),
                                   rect.center, centered=True)

    def draw_panel(self):
        """绘制右侧面板"""
        maze_width = self.maze.width * self.cell_size
        panel_rect = pygame.Rect(maze_width, 0, self.panel_width, self.window_height)

        pygame.draw.rect(self.screen, self.colors['panel_bg'], panel_rect)
        pygame.draw.line(self.screen, self.colors['border'],
                         (maze_width, 0), (maze_width, self.window_height), 2)

        return panel_rect

    def draw_menu(self):
        """绘制主菜单"""
        self.screen.fill(self.colors['background'])

        # 标题
        center_x = self.window_width // 2

        # 绘制标题区域
        title_bg = pygame.Rect(center_x - 220, 50, 440, 120)
        pygame.draw.rect(self.screen, self.colors['button'], title_bg, border_radius=12)
        pygame.draw.rect(self.screen, (60, 100, 180), title_bg, 4, border_radius=12)

        # 标题文字
        self.draw_text("MAZE PATH FINDING", self.font_large, (255, 255, 255),
                       (center_x, 80), centered=True)
        self.draw_text("BFS vs DFS Visualization", self.font_medium, (200, 220, 255),
                       (center_x, 130), centered=True)

        # 按钮
        button_width, button_height = 240, 55
        button_y = 200

        modes = ["DEMO MODE", "RACE MODE", "EXIT"]
        descriptions = ["Compare BFS and DFS algorithms", "Player vs Algorithm race", "Press ESC to exit"]

        self.menu_buttons = []

        for i, (title, desc) in enumerate(zip(modes, descriptions)):
            rect = pygame.Rect(
                center_x - button_width // 2,
                button_y + i * 85,
                button_width,
                button_height
            )

            # 悬停效果
            mouse_pos = pygame.mouse.get_pos()
            hover = rect.collidepoint(mouse_pos)

            if title == "EXIT":
                color = self.colors['button3_hover'] if hover else self.colors['button3']
            else:
                color = self.colors['button_hover'] if hover else self.colors['button']

            # 绘制按钮
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (60, 100, 180), rect, 3, border_radius=10)

            # 按钮文字
            self.draw_text(title, self.font_small, (255, 255, 255),
                           (rect.centerx, rect.centery - 5), centered=True)
            self.draw_text(desc, self.font_tiny, (180, 180, 220),
                           (center_x, rect.bottom + 12), centered=True)

            self.menu_buttons.append((title, rect))

        # 控制说明
        controls = [
            "CONTROLS:",
            "• Click buttons to select mode",
            "• ESC: Back to menu or exit",
            "• Demo: Auto-play algorithms",
            "• Race: Arrow keys to move player"
        ]

        controls_y = button_y + len(modes) * 85 + 50

        for i, text in enumerate(controls):
            color = (100, 100, 140) if i == 0 else (80, 80, 120)
            self.draw_text(text, self.font_tiny, color,
                           (center_x, controls_y + i * 24), centered=True)

    def draw_demo_mode(self):
        """绘制演示模式"""
        # 绘制迷宫
        self.draw_maze()

        # 检查demo是否结束
        if not self.demo_finished:
            # 更新动画 - 非常慢的速度
            if self.demo_playing and not self.demo_paused:
                if self.bfs_step < len(self.bfs_visited):
                    self.bfs_step = min(self.bfs_step + 0.05, len(self.bfs_visited))
                if self.dfs_step < len(self.dfs_visited):
                    self.dfs_step = min(self.dfs_step + 0.05, len(self.dfs_visited))

                # 检查是否动画结束
                if (self.bfs_step >= len(self.bfs_visited) and
                        self.dfs_step >= len(self.dfs_visited) and
                        not self.demo_finished):
                    self.demo_finished = True
                    self.demo_end_time = pygame.time.get_ticks()

        # 绘制BFS探索过程
        for i in range(int(self.bfs_step)):
            if i < len(self.bfs_visited):
                x, y = self.bfs_visited[i]
                if (x, y) not in [self.maze.start, self.maze.end]:
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    s.fill((100, 150, 255, 120))
                    self.screen.blit(s, rect)

        # 绘制DFS探索过程
        for i in range(int(self.dfs_step)):
            if i < len(self.dfs_visited):
                x, y = self.dfs_visited[i]
                if (x, y) not in [self.maze.start, self.maze.end]:
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    s.fill((180, 100, 255, 120))
                    self.screen.blit(s, rect)

        # 绘制BFS路径
        for (x, y) in self.bfs_path:
            if (x, y) not in [self.maze.start, self.maze.end]:
                center_x = x * self.cell_size + self.cell_size // 2
                center_y = y * self.cell_size + self.cell_size // 2
                pygame.draw.circle(self.screen, self.colors['path_bfs'],
                                   (center_x, center_y), self.cell_size // 3)

        # 绘制DFS路径
        for (x, y) in self.dfs_path:
            if (x, y) not in [self.maze.start, self.maze.end]:
                center_x = x * self.cell_size + self.cell_size // 2
                center_y = y * self.cell_size + self.cell_size // 2
                pygame.draw.circle(self.screen, self.colors['path_dfs'],
                                   (center_x, center_y), self.cell_size // 3)

        # 绘制面板
        panel = self.draw_panel()
        panel_x = panel.x + 20
        y = 25

        # 标题
        self.draw_text("DEMO MODE", self.font_medium, self.colors['text'], (panel_x, y))
        y += 45

        # 控制说明
        controls = [
            "ESC: Back to menu",
            "SPACE: Pause/Resume",
            "+ / -: Speed control",
            "R: Restart demo"
        ]

        for text in controls:
            self.draw_text(text, self.font_tiny, (80, 80, 100), (panel_x, y))
            y += 28

        y += 15

        # 算法信息
        bfs_progress = f"{int(self.bfs_step)}/{len(self.bfs_visited)}" if self.bfs_visited else "0/0"
        dfs_progress = f"{int(self.dfs_step)}/{len(self.dfs_visited)}" if self.dfs_visited else "0/0"

        info = [
            f"Maze: {self.maze.width} x {self.maze.height}",
            f"Start: {self.maze.start}",
            f"End: {self.maze.end}",
            f"BFS progress: {bfs_progress}",
            f"DFS progress: {dfs_progress}",
            f"BFS path: {len(self.bfs_path)} steps",
            f"DFS path: {len(self.dfs_path)} steps"
        ]

        for text in info:
            self.draw_text(text, self.font_tiny, (60, 60, 80), (panel_x, y))
            y += 22

        # 图例
        y += 10
        self.draw_text("LEGEND:", self.font_tiny, (80, 80, 100), (panel_x, y))
        y += 25

        legends = [
            ("BFS visited", self.colors['visited_bfs']),
            ("DFS visited", self.colors['visited_dfs']),
            ("BFS path", self.colors['path_bfs']),
            ("DFS path", self.colors['path_dfs'])
        ]

        for name, color in legends:
            pygame.draw.rect(self.screen, color, (panel_x, y, 14, 14), border_radius=3)
            self.draw_text(name, self.font_tiny, (60, 60, 80), (panel_x + 22, y - 2))
            y += 22

        # 状态和速度
        if self.demo_finished:
            status = "FINISHED"
            status_color = (50, 200, 50)
        else:
            status = "PLAYING" if not self.demo_paused else "PAUSED"
            status_color = (50, 200, 50) if not self.demo_paused else (220, 50, 50)

        self.draw_text(f"Status: {status}", self.font_tiny, status_color,
                       (panel_x, panel.height - 80))
        self.draw_text(f"Speed: {self.demo_speed:.1f}x", self.font_tiny,
                       (80, 80, 100), (panel_x, panel.height - 50))

        # 如果demo结束，显示提示
        if self.demo_finished:
            if not self.show_demo_end_menu:
                hint_text = "Demo finished! Press any key to continue..."
                self.draw_text(hint_text, self.font_tiny, (50, 200, 50),
                               (panel.x + panel.width // 2, panel.height - 25), centered=True)

        # 如果显示demo结束菜单
        if self.show_demo_end_menu:
            self.draw_demo_end_menu()

    def draw_demo_end_menu(self):
        """绘制demo结束菜单"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # demo结束菜单框
        menu_width = min(550, self.window_width - 80)
        menu_height = 400
        menu_x = (self.window_width - menu_width) // 2
        menu_y = (self.window_height - menu_height) // 2

        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, (40, 45, 60), menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 150, 255), menu_rect, 4, border_radius=15)

        # 标题
        title_y = menu_y + 30
        self.draw_text("DEMO FINISHED", self.font_large, (255, 255, 255),
                       (self.window_width // 2, title_y), centered=True)

        # 算法对比结果
        stats_y = title_y + 60

        bfs_path_len = len(self.bfs_path) if self.bfs_path else 0
        dfs_path_len = len(self.dfs_path) if self.dfs_path else 0
        bfs_cells = len(self.bfs_visited)
        dfs_cells = len(self.dfs_visited)

        if bfs_path_len > 0 and dfs_path_len > 0:
            if bfs_path_len < dfs_path_len:
                better_algo = "✓ BFS found shorter path"
                better_color = (100, 150, 255)
            elif dfs_path_len < bfs_path_len:
                better_algo = "✓ DFS found shorter path"
                better_color = (180, 100, 255)
            else:
                better_algo = "Both algorithms found same length path"
                better_color = (200, 200, 100)
        elif bfs_path_len > 0:
            better_algo = "✓ Only BFS found a path"
            better_color = (100, 150, 255)
        elif dfs_path_len > 0:
            better_algo = "✓ Only DFS found a path"
            better_color = (180, 100, 255)
        else:
            better_algo = "✗ No path found by either algorithm"
            better_color = (220, 100, 100)

        stats = [
            f"BFS: {bfs_path_len} steps, visited {bfs_cells} cells",
            f"DFS: {dfs_path_len} steps, visited {dfs_cells} cells",
            better_algo
        ]

        for i, stat in enumerate(stats):
            color = better_color if i == 2 else (180, 200, 240)
            font_size = self.font_tiny if i == 2 else self.font_micro
            self.draw_text(stat, font_size, color,
                           (self.window_width // 2, stats_y + i * 28), centered=True)

        # 按钮
        button_width = min(400, menu_width - 60)
        button_height = 45
        button_y_start = menu_y + 170

        options = [
            ("RESTART DEMO", "Run demo again with same maze"),
            ("NEW MAZE DEMO", "Generate new maze and run demo"),
            ("BACK TO MENU", "Return to main menu")
        ]

        self.demo_menu_buttons = []

        for i, (title, desc) in enumerate(options):
            button_rect = pygame.Rect(
                self.window_width // 2 - button_width // 2,
                button_y_start + i * 85,
                button_width,
                button_height
            )

            mouse_pos = pygame.mouse.get_pos()
            hover = button_rect.collidepoint(mouse_pos)

            if i == 0:
                color = self.colors['button2_hover'] if hover else self.colors['button2']
            elif i == 1:
                color = self.colors['button_hover'] if hover else self.colors['button']
            else:
                color = self.colors['button3_hover'] if hover else self.colors['button3']

            pygame.draw.rect(self.screen, color, button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2, border_radius=8)

            title_font = self.font_tiny if len(title) > 12 else self.font_small
            self.draw_text(title, title_font, (255, 255, 255),
                           (button_rect.centerx, button_rect.centery - 6), centered=True)

            self.draw_text(desc, self.font_micro, (180, 180, 220),
                           (button_rect.centerx, button_rect.bottom + 6),
                           centered=True, max_width=button_width - 40)

            self.demo_menu_buttons.append((title, button_rect))

    def draw_race_mode(self):
        """绘制比赛模式"""
        self.draw_maze()

        # 绘制玩家和算法
        player_center = (
            self.player_pos[0] * self.cell_size + self.cell_size // 2,
            self.player_pos[1] * self.cell_size + self.cell_size // 2
        )
        pygame.draw.circle(self.screen, self.colors['player'], player_center, self.cell_size // 3)
        pygame.draw.circle(self.screen, (255, 255, 255), player_center, self.cell_size // 3 + 2, 2)

        algo_center = (
            self.algorithm_pos[0] * self.cell_size + self.cell_size // 2,
            self.algorithm_pos[1] * self.cell_size + self.cell_size // 2
        )
        pygame.draw.circle(self.screen, self.colors['algorithm'], algo_center, self.cell_size // 3)
        pygame.draw.circle(self.screen, (255, 255, 255), algo_center, self.cell_size // 3 + 2, 2)

        # 绘制面板
        panel = self.draw_panel()
        panel_x = panel.x + 20
        y = 25

        # 标题
        self.draw_text("RACE MODE", self.font_medium, self.colors['text'], (panel_x, y))
        y += 45

        # 控制说明
        controls = [
            "ESC: Back to menu",
            "ARROWS: Move player",
            "SPACE: Start/Pause",
            "R: Restart race"
        ]

        for text in controls:
            self.draw_text(text, self.font_tiny, (80, 80, 100), (panel_x, y))
            y += 28

        y += 15

        # 比赛信息
        status_color = (50, 200, 50) if self.race_started else (220, 150, 50)
        status_text = "RACING" if self.race_started else "READY"

        info = [
            f"Player: {self.player_pos}",
            f"Steps: {self.player_steps}",
            f"Algorithm: {self.algorithm_pos}",
            f"Steps: {self.algorithm_steps}",
            f"Status: {status_text}",
            f"Distance: {self._manhattan_distance(self.player_pos, self.maze.end)}"
        ]

        for i, text in enumerate(info):
            color = status_color if i == 4 else (60, 60, 80)
            self.draw_text(text, self.font_tiny, color, (panel_x, y))
            y += 24

        # 图例
        y += 15
        self.draw_text("LEGEND:", self.font_tiny, (80, 80, 100), (panel_x, y))
        y += 25

        legends = [
            ("Player", self.colors['player']),
            ("Algorithm", self.colors['algorithm'])
        ]

        for name, color in legends:
            pygame.draw.rect(self.screen, color, (panel_x, y, 16, 16), border_radius=8)
            self.draw_text(name, self.font_tiny, (60, 60, 80), (panel_x + 25, y - 2))
            y += 25

        # 如果比赛结束，显示游戏结束菜单
        if self.race_finished:
            result_y = panel.height - 180
            result_color = self.colors['result_win'] if self.winner == "Player" else self.colors['result_lose']

            self.draw_text("RACE FINISHED!", self.font_small, result_color,
                           (panel.x + panel.width // 2, result_y), centered=True)

            winner_text = f"WINNER: {self.winner}"
            self.draw_text(winner_text, self.font_medium, result_color,
                           (panel.x + panel.width // 2, result_y + 40), centered=True)

            race_time = self._format_time(pygame.time.get_ticks() - self.race_start_time)
            stats = [
                f"Player steps: {self.player_steps}",
                f"Algorithm steps: {self.algorithm_steps}",
                f"Time: {race_time}"
            ]

            for i, stat in enumerate(stats):
                self.draw_text(stat, self.font_tiny, (80, 80, 100),
                               (panel.x + panel.width // 2, result_y + 80 + i * 25), centered=True)

            if self.show_game_over_menu:
                self.draw_game_over_menu()
            else:
                hint_text = "Press any key to continue..."
                self.draw_text(hint_text, self.font_tiny, (150, 150, 180),
                               (panel.x + panel.width // 2, panel.height - 40), centered=True)
        else:
            if not self.race_started:
                hint_text = "Press SPACE to start the race!"
                hint_color = (220, 50, 50)
            else:
                hint_text = "Race in progress..."
                hint_color = (50, 200, 50)

            self.draw_text(hint_text, self.font_tiny, hint_color,
                           (panel.x + panel.width // 2, panel.height - 40), centered=True)

    def draw_game_over_menu(self):
        """绘制游戏结束菜单"""
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        menu_width = min(500, self.window_width - 100)
        menu_height = 400
        menu_x = (self.window_width - menu_width) // 2
        menu_y = (self.window_height - menu_height) // 2

        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, (30, 35, 50), menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, (80, 120, 200), menu_rect, 4, border_radius=15)

        title_y = menu_y + 40
        self.draw_text("GAME OVER", self.font_large, (255, 255, 255),
                       (self.window_width // 2, title_y), centered=True)

        result_color = self.colors['result_win'] if self.winner == "Player" else self.colors['result_lose']
        result_text = f"Winner: {self.winner}"
        self.draw_text(result_text, self.font_medium, result_color,
                       (self.window_width // 2, title_y + 60), centered=True)

        race_time = self._format_time(pygame.time.get_ticks() - self.race_start_time)
        stats = [
            f"Player steps: {self.player_steps}",
            f"Algorithm steps: {self.algorithm_steps}",
            f"Race time: {race_time}"
        ]

        stats_y = title_y + 100
        for i, stat in enumerate(stats):
            self.draw_text(stat, self.font_tiny, (180, 200, 220),
                           (self.window_width // 2, stats_y + i * 25), centered=True)

        button_width = min(350, menu_width - 40)
        button_height = 50
        button_y_start = menu_y + 200

        options = [
            ("PLAY AGAIN", "Start a new race with same maze"),
            ("NEW MAZE", "Generate a new maze and race"),
            ("BACK TO MENU", "Return to main menu")
        ]

        self.game_over_buttons = []

        for i, (title, desc) in enumerate(options):
            button_rect = pygame.Rect(
                self.window_width // 2 - button_width // 2,
                button_y_start + i * 85,
                button_width,
                button_height
            )

            mouse_pos = pygame.mouse.get_pos()
            hover = button_rect.collidepoint(mouse_pos)

            if i == 0:
                color = self.colors['button2_hover'] if hover else self.colors['button2']
            elif i == 1:
                color = self.colors['button_hover'] if hover else self.colors['button']
            else:
                color = self.colors['button3_hover'] if hover else self.colors['button3']

            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2, border_radius=10)

            self.draw_text(title, self.font_tiny if len(title) > 10 else self.font_small,
                           (255, 255, 255), (button_rect.centerx, button_rect.centery - 8), centered=True)

            self.draw_text(desc, self.font_micro, (180, 180, 220),
                           (button_rect.centerx, button_rect.bottom + 8), centered=True, max_width=button_width - 20)

            self.game_over_buttons.append((title, button_rect))

    def _manhattan_distance(self, pos1, pos2):
        """计算曼哈顿距离"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _format_time(self, milliseconds):
        """格式化时间"""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def handle_menu_click(self, title):
        """处理菜单点击"""
        if title == "DEMO MODE":
            self.mode = 'demo'
            self.init_demo_mode()
        elif title == "RACE MODE":
            self.mode = 'race'
            self.init_race_mode()
        elif title == "EXIT":
            self.running = False

    def handle_demo_menu_click(self, title):
        """处理demo结束菜单点击"""
        if title == "RESTART DEMO":
            self.init_demo_mode()
            self.show_demo_end_menu = False
        elif title == "NEW MAZE DEMO":
            from maze.maze import Maze
            new_maze = Maze(self.maze.width, self.maze.height).generate()
            self.maze = new_maze
            self.init_demo_mode()
            self.show_demo_end_menu = False
        elif title == "BACK TO MENU":
            self.mode = 'menu'
            self.show_demo_end_menu = False

    def handle_game_over_click(self, title):
        """处理游戏结束菜单点击"""
        if title == "PLAY AGAIN":
            self.init_race_mode()
            self.show_game_over_menu = False
        elif title == "NEW MAZE":
            from maze.maze import Maze
            new_maze = Maze(self.maze.width, self.maze.height).generate()
            self.maze = new_maze
            self.init_race_mode()
            self.show_game_over_menu = False
        elif title == "BACK TO MENU":
            self.mode = 'menu'
            self.show_game_over_menu = False

    def init_demo_mode(self):
        """初始化演示模式"""
        print("Starting Demo Mode...")

        self.demo_finished = False
        self.show_demo_end_menu = False
        self.demo_playing = True
        self.demo_paused = False
        self.demo_speed = 0.1

        try:
            from maze.maze import BFSFinder, DFSFinder

            bfs = BFSFinder(self.maze)
            self.bfs_path = bfs.find_path() or []
            self.bfs_visited = bfs.visited

            dfs = DFSFinder(self.maze)
            self.dfs_path = dfs.find_path() or []
            self.dfs_visited = dfs.visited

            self.bfs_step = 0
            self.dfs_step = 0

            print(f"BFS path: {len(self.bfs_path)} steps")
            print(f"DFS path: {len(self.dfs_path)} steps")

        except Exception as e:
            print(f"Error initializing demo: {e}")
            self.bfs_path = [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
            self.dfs_path = [(1, 1), (1, 2), (2, 2), (3, 2), (3, 3), (4, 3), (5, 3)]
            self.bfs_visited = [(1, 1), (2, 1), (1, 2), (3, 1), (2, 2), (4, 1), (3, 2)]
            self.dfs_visited = [(1, 1), (1, 2), (2, 2), (1, 3), (3, 2), (2, 3), (4, 2)]

    def init_race_mode(self):
        """初始化比赛模式"""
        print("Initializing Race Mode...")

        self.player_pos = self.maze.start
        self.algorithm_pos = self.maze.start
        self.player_steps = 0
        self.algorithm_steps = 0
        self.race_started = False
        self.race_finished = False
        self.winner = None
        self.show_game_over_menu = False
        self.game_over_time = 0
        self.race_start_time = pygame.time.get_ticks()
        self.last_algorithm_move = 0
        self.algorithm_speed = 0.8

        try:
            from maze.maze import BFSFinder
            bfs = BFSFinder(self.maze)
            self.algorithm_path = bfs.find_path() or []
            self.algorithm_index = 0
            print(f"Algorithm path calculated: {len(self.algorithm_path)} steps")
        except:
            self.algorithm_path = []
            print("Using simple algorithm")

    def update_race(self):
        """更新比赛状态"""
        if not self.race_started or self.race_finished:
            return

        current_time = pygame.time.get_ticks()

        # 算法移动 - 限制速度
        if current_time - self.last_algorithm_move > self.algorithm_speed * 1000:
            self.last_algorithm_move = current_time

            if self.algorithm_pos != self.maze.end:
                if self.algorithm_path and self.algorithm_index < len(self.algorithm_path) - 1:
                    self.algorithm_index += 1
                    self.algorithm_pos = self.algorithm_path[self.algorithm_index]
                    self.algorithm_steps += 1
                else:
                    x, y = self.algorithm_pos
                    possible_moves = []

                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < self.maze.width and 0 <= ny < self.maze.height and
                                self.maze.grid[ny][nx] == 0):
                            possible_moves.append((nx, ny))

                    if possible_moves:
                        if random.random() < 0.8:
                            best_move = None
                            best_distance = float('inf')

                            for move in possible_moves:
                                distance = self._manhattan_distance(move, self.maze.end)
                                if distance < best_distance:
                                    best_distance = distance
                                    best_move = move

                            if best_move:
                                self.algorithm_pos = best_move
                        else:
                            self.algorithm_pos = random.choice(possible_moves)

                        self.algorithm_steps += 1

        # 检查比赛是否结束
        if self.player_pos == self.maze.end:
            self.race_finished = True
            self.winner = "Player"
            self.game_over_time = pygame.time.get_ticks()
            print(f"Player wins! Steps: {self.player_steps}")

        elif self.algorithm_pos == self.maze.end:
            self.race_finished = True
            self.winner = "Algorithm"
            self.game_over_time = pygame.time.get_ticks()
            print(f"Algorithm wins! Steps: {self.algorithm_steps}")

    def move_player(self, direction):
        """移动玩家"""
        if not self.race_started or self.race_finished:
            return

        dx, dy = direction
        x, y = self.player_pos
        new_x, new_y = x + dx, y + dy

        if (0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height and
                self.maze.grid[new_y][new_x] == 0):
            self.player_pos = (new_x, new_y)
            self.player_steps += 1

            if self.player_pos == self.maze.end:
                self.race_finished = True
                self.winner = "Player"
                self.game_over_time = pygame.time.get_ticks()
                print(f"Player reaches end! Steps: {self.player_steps}")

    def run(self):
        """主游戏循环"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.mode == 'menu':
                            self.running = False
                        else:
                            self.mode = 'menu'
                            self.show_demo_end_menu = False
                            self.show_game_over_menu = False

                    elif self.mode == 'demo':
                        if self.demo_finished:
                            if not self.show_demo_end_menu:
                                self.show_demo_end_menu = True
                        else:
                            if event.key == pygame.K_SPACE:
                                self.demo_paused = not self.demo_paused
                            elif event.key in [pygame.K_PLUS, pygame.K_EQUALS]:
                                self.demo_speed = min(1.0, self.demo_speed + 0.05)
                            elif event.key == pygame.K_MINUS:
                                self.demo_speed = max(0.05, self.demo_speed - 0.05)
                            elif event.key == pygame.K_r:
                                self.init_demo_mode()

                    elif self.mode == 'race':
                        if self.race_finished:
                            if not self.show_game_over_menu:
                                self.show_game_over_menu = True
                        else:
                            if event.key == pygame.K_SPACE:
                                self.race_started = not self.race_started
                                if self.race_started:
                                    self.race_start_time = pygame.time.get_ticks()
                            elif event.key == pygame.K_r:
                                self.init_race_mode()
                            elif event.key in [pygame.K_UP, pygame.K_w]:
                                self.move_player((0, -1))
                            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                                self.move_player((1, 0))
                            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                                self.move_player((0, 1))
                            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                                self.move_player((-1, 0))

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.mode == 'menu':
                        for title, rect in self.menu_buttons:
                            if rect.collidepoint(mouse_pos):
                                self.handle_menu_click(title)
                                break

                    elif self.mode == 'demo' and self.show_demo_end_menu:
                        for title, rect in self.demo_menu_buttons:
                            if rect.collidepoint(mouse_pos):
                                self.handle_demo_menu_click(title)
                                break

                    elif self.mode == 'race' and self.show_game_over_menu:
                        for title, rect in self.game_over_buttons:
                            if rect.collidepoint(mouse_pos):
                                self.handle_game_over_click(title)
                                break

            # 更新游戏状态
            if self.mode == 'race' and self.race_started and not self.race_finished:
                self.update_race()

            # 绘制
            self.screen.fill(self.colors['background'])

            if self.mode == 'menu':
                self.draw_menu()
            elif self.mode == 'demo':
                self.draw_demo_mode()
            elif self.mode == 'race':
                self.draw_race_mode()

            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()
        sys.exit()