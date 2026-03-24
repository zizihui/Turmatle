"""生成微调数据集-特殊双图形中的线段和矩形"""
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
from geom.shapes import Line, Rect

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_l_r_special/images_l_r_special')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_l_r_special/labels_l_r_special.txt')
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
    return f'line{idx} = Line(Point({start[0]:.1f},{start[1]:.1f}), Point({end[0]:.1f},{end[1]:.1f}))'

def rect_desc(idx, bottom_left, top_right):
    return f'rect{idx} = Rect(Point({bottom_left[0]:.1f},{bottom_left[1]:.1f}), Point({top_right[0]:.1f},{top_right[1]:.1f}))'

def is_point_in_bounds(point):
    """检查点是否在画布范围内"""
    return -4.9 <= point[0] <= 4.9 and -4.9 <= point[1] <= 4.9

def get_point_on_edge(x1, y1, x2, y2, edge, exclude_endpoints=False):
    """在矩形的指定边上获取随机点，可选排除端点"""
    if exclude_endpoints:
        min_t, max_t = 0.1, 0.9
    else:
        min_t, max_t = 0, 1
    
    if edge == 'bottom':  # 底边
        x = round(random.uniform(x1 + min_t * (x2 - x1), x1 + max_t * (x2 - x1)), 1)
        return (x, y1)
    elif edge == 'top':  # 顶边
        x = round(random.uniform(x1 + min_t * (x2 - x1), x1 + max_t * (x2 - x1)), 1)
        return (x, y2)
    elif edge == 'left':  # 左边
        y = round(random.uniform(y1 + min_t * (y2 - y1), y1 + max_t * (y2 - y1)), 1)
        return (x1, y)
    elif edge == 'right':  # 右边
        y = round(random.uniform(y1 + min_t * (y2 - y1), y1 + max_t * (y2 - y1)), 1)
        return (x2, y)

def get_rect_vertices(x1, y1, x2, y2):
    """获取矩形的四个顶点"""
    return [
        (x1, y1),  # 左下
        (x2, y1),  # 右下
        (x2, y2),  # 右上
        (x1, y2)   # 左上
    ]

def get_other_edges(current_edge):
    """获取除当前边之外的其他边"""
    all_edges = ['bottom', 'top', 'left', 'right']
    return [edge for edge in all_edges if edge != current_edge]

def generate_line_endpoints_on_edges():
    """生成直线两端点都在矩形边上，不含端点"""
    while True:
        # 生成矩形（1位小数）
        x1 = round(random.uniform(-4.9, 4.0), 1)
        y1 = round(random.uniform(-4.9, 4.0), 1)
        x2 = round(random.uniform(x1 + 0.5, 4.9), 1)
        y2 = round(random.uniform(y1 + 0.5, 4.9), 1)
        
        # 矩形的四条边
        edges = ['bottom', 'top', 'left', 'right']
        
        # 随机选择两个不同的边
        edge1, edge2 = random.sample(edges, 2)
        
        # 在选定的边上生成点，排除端点
        point1 = get_point_on_edge(x1, y1, x2, y2, edge1, exclude_endpoints=True)
        point2 = get_point_on_edge(x1, y1, x2, y2, edge2, exclude_endpoints=True)
        
        # 确保两点不重合且都在画布内
        if (point1 != point2 and 
            is_point_in_bounds(point1) and 
            is_point_in_bounds(point2)):
            return (x1, y1), (x2, y2), point1, point2

def generate_line_one_vertex_one_opposite():
    """生成直线一端在顶点，另一端在对面两条边上或对角顶点"""
    while True:
        # 生成矩形（1位小数）
        x1 = round(random.uniform(-4.9, 4.0), 1)
        y1 = round(random.uniform(-4.9, 4.0), 1)
        x2 = round(random.uniform(x1 + 0.5, 4.9), 1)
        y2 = round(random.uniform(y1 + 0.5, 4.9), 1)
        
        # 矩形的四个顶点
        vertices = get_rect_vertices(x1, y1, x2, y2)
        
        # 随机选择一个顶点作为起点
        vertex_idx = random.randint(0, 3)
        point1 = vertices[vertex_idx]
        
        # 定义对面两条边和对角顶点
        opposite_edges_map = {
            0: (['top', 'right'], 2),  # 左下 -> top, right, 对角: 右上 (index 2)
            1: (['top', 'left'], 3),   # 右下 -> top, left, 对角: 左上 (3)
            2: (['bottom', 'left'], 0),# 右上 -> bottom, left, 对角: 左下 (0)
            3: (['bottom', 'right'], 1)# 左上 -> bottom, right, 对角: 右下 (1)
        }
        opposite_edges, opposite_vertex_idx = opposite_edges_map[vertex_idx]
        opposite_vertex = vertices[opposite_vertex_idx]
        
        # 随机决定另一端的位置：对面边上或对角顶点
        if random.choice([True, False]):  # 选择对角顶点
            point2 = opposite_vertex
        else:  # 选择对面边上的一点（排除端点，避免与矩形边重合）
            edge2 = random.choice(opposite_edges)
            point2 = get_point_on_edge(x1, y1, x2, y2, edge2, exclude_endpoints=True)
        
        # 确保两点不重合且都在画布内
        if (point1 != point2 and 
            is_point_in_bounds(point1) and 
            is_point_in_bounds(point2)):
            return (x1, y1), (x2, y2), point1, point2

def gen_line_rect_relation(img_idx, relation_type):
    """生成直线与矩形的特定关系图像"""
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
    
    if relation_type == "endpoints_on_edges":
        # 生成直线端点都在边上的情况，不含端点
        rect_bl, rect_tr, line_start, line_end = generate_line_endpoints_on_edges()
        
        # 先画矩形
        rect = Rect(Point(rect_bl[0], rect_bl[1]), Point(rect_tr[0], rect_tr[1]))
        rect.show()
        descs.append(rect_desc(1, rect_bl, rect_tr))
        
        # 再画直线
        line = Line(Point(line_start[0], line_start[1]), Point(line_end[0], line_end[1]))
        line.show()
        descs.append(line_desc(1, line_start, line_end))
        
    elif relation_type == "one_vertex_one_opposite":
        # 生成一端在顶点另一端在对面边或对角的情况
        rect_bl, rect_tr, line_start, line_end = generate_line_one_vertex_one_opposite()
        
        # 先画矩形
        rect = Rect(Point(rect_bl[0], rect_bl[1]), Point(rect_tr[0], rect_tr[1]))
        rect.show()
        descs.append(rect_desc(1, rect_bl, rect_tr))
        
        # 再画直线
        line = Line(Point(line_start[0], line_start[1]), Point(line_end[0], line_end[1]))
        line.show()
        descs.append(line_desc(1, line_start, line_end))
    
    screen.update()
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, f'lr_special{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'lr_special{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    
    return png_path, descs

def get_next_img_idx(img_dir):
    """获取下一个图像索引"""
    if not os.path.exists(img_dir):
        return 1
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('lr_special') and f.endswith('.png'):
            try:
                num = int(f[10:-4])  # 去掉'lr_special'前缀和'.png'后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    """主函数"""
    # 每种关系生成900个样本
    samples_per_type = 900
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    relation_types = [
        ("endpoints_on_edges", "直线两端在任意两条边上，不含端点"),
        ("one_vertex_one_opposite", "一端在顶点，另一端在对面两条边上或对角顶点")
    ]
    
    print(f"开始生成直线与矩形的关系数据，总共{len(relation_types) * samples_per_type}张图像...")
    print(f"输出目录: {IMG_DIR}")
    print(f"标签文件: {LABEL_FILE}")
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        
        for relation_type, description in relation_types:
            print(f"正在生成: {description} ({samples_per_type}个样本)")
            
            for j in range(samples_per_type):
                img_path, descs = gen_line_rect_relation(img_idx, relation_type)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                img_idx += 1
                
                if (j + 1) % 100 == 0:
                    print(f"  已完成 {j + 1}/{samples_per_type}")
    
    print(f'直线与矩形关系生成完成！总共生成了 {len(relation_types) * samples_per_type} 个样本')
    print(f'图像保存在: {IMG_DIR}')
    print(f'标签保存在: {LABEL_FILE}')

if __name__ == "__main__":
    main()