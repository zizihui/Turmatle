"""生成微调数据集-特殊双图形中的线段和三角形"""
import os
import sys
import random
import turtle
import math
import ctypes
from PIL import Image

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from geom.base import Geom, Point
from geom.shapes import Line, Triangle

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_l_t_special/images_l_t_special')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_l_t_special/labels_l_t_special.txt')
os.makedirs(IMG_DIR, exist_ok=True)

def set_dpi_awareness():
    """确保Windows下的窗口大小一致性"""
    if sys.platform != 'win32':
        return
    try:
        # Windows 8.1+ (每显示器DPI感知)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # Windows Vista/7
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def line_desc(idx, start, end):
    """生成直线标签描述字符串"""
    return f'line{idx} = Line(Point({start[0]:.1f},{start[1]:.1f}), Point({end[0]:.1f},{end[1]:.1f}))'

def triangle_desc(idx, p1, p2, p3):
    """生成三角形标签描述字符串"""
    return f'triangle{idx} = Triangle(Point({p1[0]:.1f},{p1[1]:.1f}), Point({p2[0]:.1f},{p2[1]:.1f}), Point({p3[0]:.1f},{p3[1]:.1f}))'

def get_next_img_idx(img_dir):
    """获取下一个图片编号"""
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('lt_special') and f.endswith('.png'):
            try:
                num = int(f[10:-4])
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def calculate_area(p1, p2, p3):
    """计算三角形面积"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    area = 0.5 * abs((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1))
    return area
    
def angle(P1, P2, P3):
    """计算P1处的角度（度数）"""
    p1p2 = (P2[0]-P1[0], P2[1]-P1[1])
    p1p3 = (P3[0]-P1[0], P3[1]-P1[1])
    dot_product = p1p2[0]*p1p3[0] + p1p2[1]*p1p3[1]
    norm_p1p2 = math.sqrt(p1p2[0]**2 + p1p2[1]**2)
    norm_p1p3 = math.sqrt(p1p3[0]**2 + p1p3[1]**2)
    if norm_p1p2 == 0 or norm_p1p3 == 0:
        return None  # 返回None表示无效角度
    cos_theta = dot_product / (norm_p1p2 * norm_p1p3)
    # 防止数值误差导致超出[-1,1]
    cos_theta = max(-1, min(1, cos_theta))
    angle_rad = math.acos(cos_theta)
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def is_valid_triangle(p1, p2, p3, min_area=1.0, min_angle_deg=15):
    """验证是否为有效的三角形"""
    # 检查面积
    area = calculate_area(p1, p2, p3)
    if area <= min_area:
        return False
    
    # 计算三个角
    angles = [
        angle(p1, p2, p3),  # p1处的角
        angle(p2, p1, p3),  # p2处的角  
        angle(p3, p1, p2)   # p3处的角
    ]
    # 检查是否有无效角度或角度过小
    if any(a is None or a < min_angle_deg for a in angles):
        return False
    return True

def point_on_segment(p1, p2, t):
    """在线段p1-p2上根据参数t（0到1）生成点（1位小数）"""
    return (round(p1[0] + t * (p2[0] - p1[0]), 1), round(p1[1] + t * (p2[1] - p1[1]), 1))

def point_to_line_distance(point, line_p1, line_p2):
    """计算点到直线的距离"""
    x0, y0 = point
    x1, y1 = line_p1
    x2, y2 = line_p2
    
    # 使用点到直线距离公式：|ax + by + c| / sqrt(a² + b²)
    # 其中直线方程为：(y2-y1)x - (x2-x1)y + (x2-x1)y1 - (y2-y1)x1 = 0
    a = y2 - y1
    b = -(x2 - x1)
    c = (x2 - x1) * y1 - (y2 - y1) * x1
    
    distance = abs(a * x0 + b * y0 + c) / math.sqrt(a**2 + b**2)
    return distance

def get_opposite_edge(vertex_idx):
    """获取指定顶点对面的边"""
    # 对于p1 (index 0), 对面边是p2-p3 (edges[1])
    # 对于p2 (1), 对面边是p3-p1 (edges[2])  
    # 对于p3 (2), 对面边是p1-p2 (edges[0])
    opposite_edges = [(1, 2), (2, 0), (0, 1)]  # 对面边的顶点索引
    return opposite_edges[vertex_idx]

def gen_one_lt(img_idx, category):
    """生成一张直线+三角形的图片"""
    Geom.set_defaults(origin_x=0, origin_y=0, scale=100, speed=0, pensize=5)
    turtle.clearscreen()
    screen = turtle.Screen()
    # 强制Tk缩放为1.0（禁用额外的DPI缩放）
    try:
        tk_obj = getattr(screen, '_root', None)
        if tk_obj is not None:
            tk_obj.tk.call('tk', 'scaling', 1.0)
        else:
            tk_fallback = screen.cv._rootwindow
            tk_fallback.tk.call('tk', 'scaling', 1.0)
    except Exception:
        pass
    screen.setup(WIDTH, HEIGHT)
    screen.tracer(0)
    descs = []
    
    # 生成有效三角形和线段端点
    while True:
        p1 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p2 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p3 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        if not is_valid_triangle(p1, p2, p3):
            continue
        
        # 三角形的顶点和边
        vertices = [p1, p2, p3]
        edges = [(p1, p2), (p2, p3), (p3, p1)]
        
        if category == 'two_points_on_different_sides_no_endpoints':
            # 类1: 直线两端在任意两条边上（不在端点）
            edge_idx1, edge_idx2 = random.sample(range(3), 2)
            edge1 = edges[edge_idx1]
            edge2 = edges[edge_idx2]
            t1 = random.uniform(0.1, 0.9)
            t2 = random.uniform(0.1, 0.9)
            start = point_on_segment(edge1[0], edge1[1], t1)
            end = point_on_segment(edge2[0], edge2[1], t2)
            
            # 验证线段端点到对应边的距离小于等于1e-10
            dist_start_to_edge1 = point_to_line_distance(start, edge1[0], edge1[1])
            dist_end_to_edge2 = point_to_line_distance(end, edge2[0], edge2[1])
            
            if dist_start_to_edge1 > 1e-10 or dist_end_to_edge2 > 1e-10:
                continue  # 重新生成
            
        elif category == 'one_vertex_opposite_side':
            # 类2: 一端在顶点，另一端在对面边上
            vertex_idx = random.randint(0, 2)
            vertex = vertices[vertex_idx]
            opposite_edge_indices = get_opposite_edge(vertex_idx)  # 返回的是元组 (idx1, idx2)
            opposite_edge = (vertices[opposite_edge_indices[0]], vertices[opposite_edge_indices[1]])  # 构造边
            t = random.uniform(0.1, 0.9)  # 避免在端点
            end = point_on_segment(opposite_edge[0], opposite_edge[1], t)
            start = vertex
            
            # 验证线段端点到对应边的距离小于等于1e-10
            dist_end_to_opposite_edge = point_to_line_distance(end, opposite_edge[0], opposite_edge[1])
            
            if dist_end_to_opposite_edge > 1e-10:
                continue  # 重新生成
        
        # 确保start和end不同
        if start != end:
            break  # 找到有效的配置，跳出循环
    
    triangle = Triangle(Point(*p1), Point(*p2), Point(*p3))
    triangle.show()
    descs.append(triangle_desc(1, p1, p2, p3))
    
    line = Line(Point(*start), Point(*end))
    line.show()
    descs.append(line_desc(1, start, end))
    
    screen.update()
    
    # 保存图片
    ps_path = os.path.join(IMG_DIR, f'lt_special{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'lt_special{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    return png_path, descs

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    """主函数"""
    samples_per_category = 900
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    # 定义关系类型
    relation_types = [
        'two_points_on_different_sides_no_endpoints',  # 直线两端在不同边上
        'one_vertex_opposite_side'                     # 一端在顶点，另一端在对面边
    ]
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        lts_idx = start_img_idx
        for category in relation_types:
            print(f"生成类别: {category}")
            for j in range(samples_per_category):
                img_path, descs = gen_one_lt(lts_idx, category)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                lts_idx += 1
                if j % 100 == 0:
                    print(f"  已生成 {j} 张图片...")
    
    print('特殊Line+Triangle混合数据生成完成！')

if __name__ == "__main__":
    main() 