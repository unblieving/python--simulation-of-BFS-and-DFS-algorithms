import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("迷宫寻路系统 - BFS vs DFS")
print("=" * 50)

try:
    # 导入模块
    from maze.maze import Maze
    from visualizer import MazeVisualizer

    print("✓ 模块导入成功")

    # 创建迷宫
    print("生成迷宫中...")
    maze = Maze(15, 15).generate()

    print(f"迷宫大小: {maze.width} × {maze.height}")
    print(f"起点: {maze.start}")
    print(f"终点: {maze.end}")

    # 显示迷宫（简化版）
    print("\n迷宫预览:")
    for y in range(min(10, maze.height)):
        row = []
        for x in range(min(10, maze.width)):
            if (x, y) == maze.start:
                row.append('S')
            elif (x, y) == maze.end:
                row.append('E')
            elif maze.grid[y][x] == 1:
                row.append('#')
            else:
                row.append('.')
        print(' '.join(row))
    if maze.width > 10 or maze.height > 10:
        print("... (完整迷宫将在界面中显示)")

    print("\n" + "-" * 40)
    print("程序功能:")
    print("  1. 演示模式 - BFS和DFS算法对比")
    print("  2. 比赛模式 - 玩家与算法对战")
    print("  3. 按ESC键返回菜单或退出")
    print("-" * 40)

    # 创建可视化器
    cell_size = 40
    visualizer = MazeVisualizer(maze, cell_size=cell_size)

    print(f"\n启动界面 ({maze.width * cell_size + 250} × {maze.height * cell_size})")
    print("正在启动...")

    # 运行主循环
    visualizer.run()

except ImportError as e:
    print(f"✗ 导入错误: {e}")
    print("\n请确保文件结构如下:")
    print("项目目录/")
    print("  ├── maze/")
    print("  │   └── maze.py    # 迷宫和算法类")
    print("  ├── visualizer.py  # 可视化界面")
    print("  └── main.py        # 这个文件")
    print("\n按Enter键退出...")
    input()
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback

    traceback.print_exc()
    print("\n按Enter键退出...")
    input()