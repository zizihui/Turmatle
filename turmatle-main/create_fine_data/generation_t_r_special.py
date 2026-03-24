"""生成微调数据集-特殊双图形中的三角形和矩形"""
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
from geom.shapes import Rect, Triangle

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_t_r_special/images_t_r_special')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_t_r_special/labels_t_r_special.txt')
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
# ----------------------------------------
# 描述与工具函数
# ----------------------------------------

def rect_desc(idx, bottom_left, top_right):
    return f'rect{idx} = Rect(Point({bottom_left[0]:.1f},{bottom_left[1]:.1f}), Point({top_right[0]:.1f},{top_right[1]:.1f}))'

def triangle_desc(idx, p1, p2, p3):
    return f'triangle{idx} = Triangle(Point({p1[0]:.1f},{p1[1]:.1f}), Point({p2[0]:.1f},{p2[1]:.1f}), Point({p3[0]:.1f},{p3[1]:.1f}))'

def get_next_img_idx(img_dir):
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('tr_special') and f.endswith('.png'):
            try:
                num = int(f[10:-4])
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

# 与 generation_triangle.py 保持一致的三角形有效性校验

def calculate_area(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    area = 0.5 * abs((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1))
    return area

def angle(P1, P2, P3):
    p1p2 = (P2[0]-P1[0], P2[1]-P1[1])
    p1p3 = (P3[0]-P1[0], P3[1]-P1[1])
    dot_product = p1p2[0]*p1p3[0] + p1p2[1]*p1p3[1]
    norm_p1p2 = math.sqrt(p1p2[0]**2 + p1p2[1]**2)
    norm_p1p3 = math.sqrt(p1p3[0]**2 + p1p3[1]**2)
    if norm_p1p2 == 0 or norm_p1p3 == 0:
        return None
    cos_theta = dot_product / (norm_p1p2 * norm_p1p3)
    cos_theta = max(-1, min(1, cos_theta))
    angle_rad = math.acos(cos_theta)
    return math.degrees(angle_rad)

def is_valid_triangle(p1, p2, p3, min_area=1.0, min_angle_deg=15):
    area = calculate_area(p1, p2, p3)
    if area <= min_area:
        return False
    angles = [angle(p1, p2, p3), angle(p2, p1, p3), angle(p3, p1, p2)]
    if any(a is None or a < min_angle_deg for a in angles):
        return False
    return True

# ----------------------------------------
# 几何构造辅助
# ----------------------------------------

def make_rect_inside_canvas():
    """生成画布内的矩形，宽高足够满足边缘留白和边点0.5约束"""
    while True:
        rect_left = round(random.uniform(-4.5, 1.5), 1)
        rect_bottom = round(random.uniform(-4.5, 1.5), 1)
        
        # 计算最大可用宽度和高度
        max_width = 4.5 - rect_left   # 右边界限制
        max_height = 4.5 - rect_bottom # 上边界限制
        
        # 确保最小尺寸要求
        if max_width < 2.0 or max_height < 2.0:
            continue
            
        rect_width = round(random.uniform(2.0, max_width), 1)
        rect_height = round(random.uniform(2.0, max_height), 1)
        
        rect_right = round(rect_left + rect_width, 1)
        rect_top = round(rect_bottom + rect_height, 1)
        
        # 最终边界检查
        if rect_right <= 4.5 and rect_top <= 4.5:
            return rect_left, rect_bottom, rect_right, rect_top


def rect_vertices(rect_left, rect_bottom, rect_right, rect_top):
    return [
        (rect_left, rect_bottom),  # 0 左下
        (rect_right, rect_bottom), # 1 右下
        (rect_right, rect_top),    # 2 右上
        (rect_left, rect_top)      # 3 左上
    ]


def point_on_edge(rect_left, rect_bottom, rect_right, rect_top, edge: str, min_margin: float = 0.5):
    """在指定边上取点，距离相邻顶点至少 min_margin（几何坐标单位）"""
    if edge in ('left', 'right'):
        y_min = rect_bottom + min_margin
        y_max = rect_top - min_margin
        if y_min >= y_max:
            return None
        y = round(random.uniform(y_min, y_max), 1)
        x = rect_left if edge == 'left' else rect_right
        return (x, y)
    else:  # 'bottom' or 'top'
        x_min = rect_left + min_margin
        x_max = rect_right - min_margin
        if x_min >= x_max:
            return None
        x = round(random.uniform(x_min, x_max), 1)
        y = rect_bottom if edge == 'bottom' else rect_top
        return (x, y)


def random_edge():
    return random.choice(['left', 'right', 'bottom', 'top'])

# ----------------------------------------
# 三种类别的构造
# ----------------------------------------

def gen_triangle_type1(rect_bounds):
    """类型1：p1为矩形顶点；p2在任一边(非顶点，距顶点>=0.5)；p3在除p2所在边的其他三边之一(非顶点，距顶点>=0.5)。"""
    rect_left, rect_bottom, rect_right, rect_top = rect_bounds
    verts = rect_vertices(*rect_bounds)
    p1 = random.choice(verts)
    while True:
        e2 = random_edge()
        p2 = point_on_edge(rect_left, rect_bottom, rect_right, rect_top, e2, 0.5)
        if p2 is None:
            continue
        e3_choices = [e for e in ['left', 'right', 'bottom', 'top'] if e != e2]
        e3 = random.choice(e3_choices)
        p3 = point_on_edge(rect_left, rect_bottom, rect_right, rect_top, e3, 0.5)
        if p3 is None:
            continue
        if is_valid_triangle(p1, p2, p3):
            return p1, p2, p3


def gen_triangle_type2(rect_bounds):
    """类型2：p1、p2为不同的矩形顶点；p3在任一边(非顶点)，且距任意顶点>=0.5；若p1,p2在同一条边上，则p3不能在该边上。"""
    rect_left, rect_bottom, rect_right, rect_top = rect_bounds
    verts = rect_vertices(*rect_bounds)
    while True:
        p1_idx, p2_idx = random.sample(range(4), 2)
        p1 = verts[p1_idx]
        p2 = verts[p2_idx]
        # 判断p1,p2是否同边
        same_edge = False
        if {p1_idx, p2_idx} in [{0,1}, {1,2}, {2,3}, {0,3}]:
            same_edge = True
        # 选择p3所在边
        e3_candidates = ['left', 'right', 'bottom', 'top']
        if same_edge:
            # 去除该条边
            if {p1_idx, p2_idx} == {0,1}:
                e3_candidates.remove('bottom')
            elif {p1_idx, p2_idx} == {1,2}:
                e3_candidates.remove('right')
            elif {p1_idx, p2_idx} == {2,3}:
                e3_candidates.remove('top')
            else:  # {0,3}
                e3_candidates.remove('left')
        e3 = random.choice(e3_candidates)
        p3 = point_on_edge(rect_left, rect_bottom, rect_right, rect_top, e3, 0.5)
        if p3 is None:
            continue
        if is_valid_triangle(p1, p2, p3):
            return p1, p2, p3


def gen_triangle_type3(rect_bounds):
    """类型3：三个点均在矩形边上（不含顶点、距顶点>=0.5），且分布在两条边或三条边上（禁止三点在同一条边）。"""
    rect_left, rect_bottom, rect_right, rect_top = rect_bounds
    edges = ['left', 'right', 'bottom', 'top']
    while True:
        # 随机决定使用两条边还是三条边
        if random.random() < 0.5:
            # 两条边：一条取两个点，另一条取一个点
            e_pair = random.sample(edges, 2)
            counts = [2, 1]
            chosen_edges = [e_pair[0]] * counts[0] + [e_pair[1]] * counts[1]
            random.shuffle(chosen_edges)
        else:
            # 三条边：各取一个点
            chosen_edges = random.sample(edges, 3)
        # 采样点
        pts = []
        valid = True
        for e in chosen_edges:
            p = point_on_edge(rect_left, rect_bottom, rect_right, rect_top, e, 0.5)
            if p is None:
                valid = False
                break
            pts.append(p)
        if not valid:
            continue
        p1, p2, p3 = pts[0], pts[1], pts[2]
        if is_valid_triangle(p1, p2, p3):
            return p1, p2, p3

# ----------------------------------------
# 绘制与保存
# ----------------------------------------

def draw_and_save(img_idx, rect_bounds, p1, p2, p3):
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

    rect_left, rect_bottom, rect_right, rect_top = rect_bounds
    rect = Rect(Point(rect_left, rect_bottom), Point(rect_right, rect_top))
    rect.show()

    tri = Triangle(Point(*p1), Point(*p2), Point(*p3))
    tri.show()

    descs = [
        rect_desc(1, (rect_left, rect_bottom), (rect_right, rect_top)),
        triangle_desc(1, p1, p2, p3)
    ]

    screen.update()

    ps_path = os.path.join(IMG_DIR, f'tr_special{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'tr_special{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())
    img = img.resize((WIDTH, HEIGHT))
    img.save(png_path)
    os.remove(ps_path)
    return png_path, descs

# ----------------------------------------
# 主入口
# ----------------------------------------

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    samples_per_category = 900
    start_img_idx = get_next_img_idx(IMG_DIR)

    categories = [
        'type1_vertex_edge_other_edges',
        'type2_two_vertices_one_edge',
        'type3_on_two_or_three_edges'
    ]

    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        for cat in categories:
            print(f'生成类别: {cat}')
            for _ in range(samples_per_category):
                rect_bounds = make_rect_inside_canvas()
                if cat == 'type1_vertex_edge_other_edges':
                    p1, p2, p3 = gen_triangle_type1(rect_bounds)
                elif cat == 'type2_two_vertices_one_edge':
                    p1, p2, p3 = gen_triangle_type2(rect_bounds)
                else:
                    p1, p2, p3 = gen_triangle_type3(rect_bounds)
                img_path, descs = draw_and_save(img_idx, rect_bounds, p1, p2, p3)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                img_idx += 1
                
    print('Triangle+Rect 特殊数据生成完成！')

if __name__ == '__main__':
    main()
