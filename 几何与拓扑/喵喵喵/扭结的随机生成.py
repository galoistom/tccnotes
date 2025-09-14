import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
import matplotlib.patches as patches
import networkx as nx
from scipy.spatial import Delaunay

class Knot:
    def __init__(self, name, pd_code):
        self.name = name
        self.pd_code = pd_code
        self.crossings = len(pd_code)
        self.graph = self.build_graph()
        self.positions = self.calculate_positions()
        self.path = self.trace_path()
    
    def build_graph(self):
        """构建扭结的图表示"""
        G = nx.Graph()
        
        # 添加所有弧段作为节点
        all_arcs = set()
        for cross in self.pd_code:
            for arc in cross:
                all_arcs.add(arc)
        
        # 添加节点
        G.add_nodes_from(all_arcs)
        
        # 添加边（连接关系）
        for cross in self.pd_code:
            # 在同一个交叉点内连接弧段
            G.add_edge(cross[0], cross[1])
            G.add_edge(cross[1], cross[2])
            G.add_edge(cross[2], cross[3])
            G.add_edge(cross[3], cross[0])
            
            # 添加交叉点之间的连接
            G.add_edge(cross[0], cross[2])  # 对角连接
            G.add_edge(cross[1], cross[3])  # 对角连接
        
        return G
    
    def calculate_positions(self):
        """计算交叉点的位置（圆形布局）"""
        angles = np.linspace(0, 2 * np.pi, self.crossings, endpoint=False)
        positions = []
        for i, angle in enumerate(angles):
            positions.append((np.cos(angle) * 1.5, np.sin(angle) * 1.5))
        return positions
    
    def trace_path(self):
        """追踪扭结的完整路径"""
        # 获取所有弧段
        all_arcs = list(self.graph.nodes())
        start_arc = all_arcs[0]
        
        # 深度优先搜索追踪路径
        path = [start_arc]
        visited = set([start_arc])
        current = start_arc
        
        while True:
            neighbors = list(self.graph.neighbors(current))
            unvisited = [n for n in neighbors if n not in visited]
            
            if not unvisited:
                break
                
            next_arc = unvisited[0]
            path.append(next_arc)
            visited.add(next_arc)
            current = next_arc
        
        # 使路径闭合
        if path[0] in self.graph.neighbors(path[-1]):
            path.append(path[0])
        
        return path
    
    def get_arc_position(self, arc):
        """获取弧段对应的交叉点位置"""
        for i, cross in enumerate(self.pd_code):
            if arc in cross:
                return self.positions[i]
        return None
    
    def draw(self, ax, title):
        """绘制完整的扭结曲线"""
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"{title}: {self.name}", fontsize=12)
        
        # 绘制完整的扭结路径
        points = []
        for arc in self.path:
            pos = self.get_arc_position(arc)
            if pos:
                points.append(pos)
        
        if not points:
            return
        
        # 转换为numpy数组
        points = np.array(points)
        
        # 使用Delaunay三角剖分创建平滑路径
        if len(points) > 3:
            tri = Delaunay(points[:, :2])
            edges = set()
            for simplex in tri.simplices:
                for i in range(3):
                    edge = tuple(sorted([simplex[i], simplex[(i+1)%3]]))
                    edges.add(edge)
            
            # 绘制所有边
            for edge in edges:
                p1 = points[edge[0]]
                p2 = points[edge[1]]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-', lw=2, alpha=0.6)
        
        # 绘制主要路径
        x = points[:, 0]
        y = points[:, 1]
        ax.plot(x, y, 'r-', lw=3, alpha=0.9)
        
        # 绘制交叉点并显示上下关系
        for i, pos in enumerate(self.positions):
            # 绘制交叉点
            ax.plot(pos[0], pos[1], 'o', markersize=12, 
                   markerfacecolor='white', markeredgecolor='black', zorder=10)
            
            # 绘制交叉关系：上方的线段（实线）
            ax.plot([pos[0] - 0.1, pos[0] + 0.1], 
                    [pos[1] - 0.1, pos[1] + 0.1], 
                    'k-', lw=2, zorder=5)
            
            # 绘制下方的线段（断开）
            ax.plot([pos[0] - 0.1, pos[0] - 0.03], 
                    [pos[1] + 0.1, pos[1] + 0.03], 
                    'k-', lw=2, zorder=5)
            ax.plot([pos[0] + 0.03, pos[0] + 0.1], 
                    [pos[1] - 0.03, pos[1] - 0.1], 
                    'k-', lw=2, zorder=5)
        
        # 设置图形范围
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)

# 修正后的预定义扭结PD码
KNOT_DEFINITIONS = {
    "Unknot": [(1, 2, 3, 4)],
    "Trefoil": [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12)],
    "FigureEight": [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 16)],
    "Cinquefoil": [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), 
                   (13, 14, 15, 16), (17, 18, 19, 20)],
    "6₁": [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), 
           (13, 14, 15, 16), (17, 18, 19, 20), (21, 22, 23, 24)],
    "7₄": [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), 
           (13, 14, 15, 16), (17, 18, 19, 20), (21, 22, 23, 24),
           (25, 26, 27, 28)],
    "8₁₉": [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), 
            (13, 14, 15, 16), (17, 18, 19, 20), (21, 22, 23, 24), 
            (25, 26, 27, 28), (29, 30, 31, 32)],
    "9₄₂": [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), 
            (13, 14, 15, 16), (17, 18, 19, 20), (21, 22, 23, 24), 
            (25, 26, 27, 28), (29, 30, 31, 32), (33, 34, 35, 36)],
    "10₁₆₁": [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), 
              (13, 14, 15, 16), (17, 18, 19, 20), (21, 22, 23, 24), 
              (25, 26, 27, 28), (29, 30, 31, 32), (33, 34, 35, 36),
              (37, 38, 39, 40)]
}

def generate_knot_pair():
    """生成一对扭结（可能等价或不等价）"""
    # 排除平凡结
    knot_types = list(KNOT_DEFINITIONS.keys())
    knot_types.remove("Unknot")
    
    # 决定是否生成等价对
    equivalent = random.choice([True, False])
    
    if equivalent:
        # 选择一种扭结类型
        knot_type = random.choice(knot_types)
        knot1 = Knot(knot_type, KNOT_DEFINITIONS[knot_type])
        
        # 创建等价的扭结（相同类型）
        knot2 = Knot(knot_type, KNOT_DEFINITIONS[knot_type])
    else:
        # 生成两个不同的扭结
        knot_type1, knot_type2 = random.sample(knot_types, 2)
        knot1 = Knot(knot_type1, KNOT_DEFINITIONS[knot_type1])
        knot2 = Knot(knot_type2, KNOT_DEFINITIONS[knot_type2])
    
    return knot1, knot2, equivalent

def main():
    print("扭结等价性判断练习")
    print("==================")
    print("规则：")
    print("1. 程序会显示两个扭结的二维投影图")
    print("2. 判断这两个扭结是否等价（是否可以通过连续变形互相转换）")
    print("3. 输入 'y' 表示等价，'n' 表示不等价")
    print("4. 所有扭结都是非平凡的，交叉点数3-10")
    print("5. 交叉点处的上下关系：实线表示在上方，断开表示在下方")
    print("6. 按'q'退出程序\n")
    
    score = 0
    total = 0
    
    while True:
        try:
            knot1, knot2, equivalent = generate_knot_pair()
            
            # 创建图形
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
            
            # 绘制两个扭结
            knot1.draw(ax1, "扭结 A")
            knot2.draw(ax2, "扭结 B")
            
            plt.tight_layout()
            plt.show()
            
            # 获取用户输入
            user_input = input("这两个扭结是否等价？ (y/n/q): ").strip().lower()
            
            if user_input == 'q':
                break
                
            if user_input not in ['y', 'n']:
                print("无效输入，请输入 'y', 'n' 或 'q'")
                continue
            
            # 检查答案
            user_equivalent = (user_input == 'y')
            correct = (user_equivalent == equivalent)
            
            if correct:
                print("正确！")
                score += 1
            else:
                if equivalent:
                    print(f"错误！这两个扭结是等价的，都是 {knot1.name} 扭结")
                else:
                    print(f"错误！这两个扭结不等价：扭结A是 {knot1.name}，扭结B是 {knot2.name}")
            
            total += 1
            print(f"当前得分: {score}/{total} ({score/total*100:.1f}%)\n")
        except Exception as e:
            print(f"发生错误: {e}")
            print("重新生成扭结对...\n")
            continue
    
    print("\n练习结束！")
    if total > 0:
        print(f"最终得分: {score}/{total} ({score/total*100:.1f}%)")

if __name__ == "__main__":
    main()