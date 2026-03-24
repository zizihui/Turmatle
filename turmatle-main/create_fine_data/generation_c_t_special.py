"""生成微调数据集-特殊双图形中的圆和三角形"""
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
from geom.shapes import Circle, Triangle

WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_c_t_special/images_c_t_special')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_c_t_special/labels_c_t_special.txt')
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

def circle_desc(idx, center, radius):
    return f'circle{idx} = Circle(Point({center[0]:.1f},{center[1]:.1f}), {radius:.1f})'

def triangle_desc(idx, p1, p2, p3):
    return f'triangle{idx} = Triangle(Point({p1[0]:.1f},{p1[1]:.1f}), Point({p2[0]:.1f},{p2[1]:.1f}), Point({p3[0]:.1f},{p3[1]:.1f}))'

def get_next_img_idx(img_dir):
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('ct_special') and f.endswith('.png'):
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

def calculate_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

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
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def is_valid_triangle(p1, p2, p3, min_area=1.0, min_angle_deg=15):
    area = calculate_area(p1, p2, p3)
    if area <= min_area:
        return False
    angles = [
        angle(p1, p2, p3),
        angle(p2, p1, p3),
        angle(p3, p1, p2)
    ]
    if any(a is None or a < min_angle_deg for a in angles):
        return False
    return True

def is_point_inside_triangle(point, t1, t2, t3):
    def sub_area(x1, y1, x2, y2, x3, y3):
        return abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)) / 2.0) 
    a = sub_area(*t1, *t2, *t3) #计算三角形的面积
    a1 = sub_area(*point, *t2, *t3)
    a2 = sub_area(*t1, *point, *t3)
    a3 = sub_area(*t1, *t2, *point)
    return abs(a - (a1 + a2 + a3)) < 1e-5

# 函数生成三角形在圆内
def generate_triangle_inside_circle(num_on_circle):
    attempt = 0
    while True:
        attempt += 1
        if attempt % 100 == 0:
            print(f"Attempt {attempt} for triangle_inside_circle with {num_on_circle} on circle")
        circle_radius = round(random.uniform(2.0, 4.5), 1)
        cx = round(random.uniform(-4.9 + circle_radius, 4.9 - circle_radius), 1)
        cy = round(random.uniform(-4.9 + circle_radius, 4.9 - circle_radius), 1)
        circle_center = (cx, cy)
        
        points = []
        for _ in range(3):
            angle_rad = random.uniform(0, 2 * math.pi)
            if len(points) < num_on_circle:
                # 在圆上
                dist = circle_radius
            else:
                # 内部
                dist = round(random.uniform(0.5, circle_radius * 0.9), 1)
            px = round(cx + dist * math.cos(angle_rad), 1)
            py = round(cy + dist * math.sin(angle_rad), 1)
            points.append((px, py))
        
        random.shuffle(points)
        p1, p2, p3 = points
        
        if is_valid_triangle(p1, p2, p3):
            dists = [calculate_distance(circle_center, p) for p in [p1, p2, p3]]
            on_count = sum(1 for d in dists if abs(d - circle_radius) <= 1e-10)
            if on_count == num_on_circle:
                return circle_center, circle_radius, p1, p2, p3

# 函数生成圆在三角形内
def compute_incenter(p1, p2, p3):
    a = calculate_distance(p2, p3)
    b = calculate_distance(p1, p3)
    c = calculate_distance(p1, p2)
    x = round((a * p1[0] + b * p2[0] + c * p3[0]) / (a + b + c), 1)
    y = round((a * p1[1] + b * p2[1] + c * p3[1]) / (a + b + c), 1)
    return (x, y)

def compute_inradius(p1, p2, p3):
    a = calculate_distance(p2, p3)
    b = calculate_distance(p1, p3)
    c = calculate_distance(p1, p2)
    s = (a + b + c) / 2 #周长的一半
    area = calculate_area(p1, p2, p3)
    return round(area / s, 1)

def generate_random_triangle():
    while True:
        p1 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p2 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p3 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        if is_valid_triangle(p1, p2, p3):
            return p1, p2, p3

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

def generate_circle_inside_triangle(num_tangent):
    outer_attempt = 0
    while True:
        outer_attempt += 1
        if outer_attempt % 100 == 0:
            print(f"Outer attempt {outer_attempt} for circle_inside_triangle with {num_tangent} tangents")
        p1, p2, p3 = generate_random_triangle()
        sides = [(p1, p2), (p2, p3), (p3, p1)]
        vertices = [p1, p2, p3]
        
        if num_tangent == 3:
            center = compute_incenter(p1, p2, p3)
            radius = compute_inradius(p1, p2, p3)
            if radius >= 0.5:
                # 验证圆心到三角形三边距离与内切圆半径的差小于等于1e-10
                dists = [point_to_line_distance(center, sides[i][0], sides[i][1]) for i in range(3)]
                if all(abs(d - radius) <= 1e-10 for d in dists):
                    return p1, p2, p3, center, radius
        
        elif num_tangent == 0:
            inner_attempt = 0
            for _ in range(100):  # 有限尝试以避免无限循环
                inner_attempt += 1
                if inner_attempt % 100 == 0:
                    print(f"Inner attempt {inner_attempt} for num_tangent=0")
                center = (round(random.uniform(min(p[0] for p in vertices), max(p[0] for p in vertices)), 1),
                          round(random.uniform(min(p[1] for p in vertices), max(p[1] for p in vertices)), 1))
                if is_point_inside_triangle(center, p1, p2, p3):
                    dists = [point_to_line_distance(center, s[0], s[1]) for s in sides]
                    min_dist = min(dists)
                    if min_dist >= 1.0:
                        radius = round(random.uniform(0.5, min_dist - 0.5), 1)
                        if all(d > radius for d in dists):
                            return p1, p2, p3, center, radius
        
        elif num_tangent == 1:
            # 随机选择一边
            side_idx = random.randint(0, 2)
            s1, s2 = sides[side_idx]
            # 随机选择切点在边上
            t = random.uniform(0.1, 0.9)  # 避免端点
            tangent_point = (s1[0] + t * (s2[0] - s1[0]), s1[1] + t * (s2[1] - s1[1]))
            # 计算法线方向（向内）
            # 先计算边向量
            dx = s2[0] - s1[0]
            dy = s2[1] - s1[1]
            # 法线向量（旋转90度，向内需判断方向）                     
            nx = -dy
            ny = dx
            # 归一化
            norm = math.sqrt(nx**2 + ny**2)
            nx /= norm
            ny /= norm
            # 判断方向：向内（检查是否指向三角形内部）
            test_point = (round(tangent_point[0] + nx * 0.1, 1), round(tangent_point[1] + ny * 0.1, 1))
            if not is_point_inside_triangle(test_point, p1, p2, p3):
                nx = -nx
                ny = -ny
            # 随机radius
            radius = round(random.uniform(0.5, 2.0), 1)  
            center = (round(tangent_point[0] + nx * radius, 1), round(tangent_point[1] + ny * radius, 1))
            # 检查中心在内部且其他距离 > radius
            if is_point_inside_triangle(center, p1, p2, p3):
                dists = [point_to_line_distance(center, sides[i][0], sides[i][1]) for i in range(3)]
                if abs(dists[side_idx] - radius) <= 1e-10 and all(d > radius + 0.5 for i, d in enumerate(dists) if i != side_idx):
                    return p1, p2, p3, center, radius

def gen_one_ct_special(img_idx, case_type, sub_case):
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
    
    if case_type == 'triangle_in_circle':
        center, radius, p1, p2, p3 = generate_triangle_inside_circle(sub_case)
        circle = Circle(Point(*center), radius)
        circle.show()
        descs.append(circle_desc(1, center, radius))
        triangle = Triangle(Point(*p1), Point(*p2), Point(*p3))
        triangle.show()
        descs.append(triangle_desc(1, p1, p2, p3))
    elif case_type == 'circle_in_triangle':
        p1, p2, p3, center, radius = generate_circle_inside_triangle(sub_case)
        triangle = Triangle(Point(*p1), Point(*p2), Point(*p3))
        triangle.show()
        descs.append(triangle_desc(1, p1, p2, p3))
        circle = Circle(Point(*center), radius)
        circle.show()
        descs.append(circle_desc(1, center, radius))
    
    screen.update()
    ps_path = os.path.join(IMG_DIR, f'ct_special{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'ct_special{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())
    img = img.resize((WIDTH, HEIGHT))
    img.save(png_path)
    os.remove(ps_path)
    return png_path, descs

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    samples_per_subcase1 = 225
    samples_per_subcase2 = 300
    start_img_idx = get_next_img_idx(IMG_DIR)
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        
        # 三角形在圆内的情况
        for num_on in [0, 1, 2, 3]:
            for _ in range(samples_per_subcase1):
                img_path, descs = gen_one_ct_special(img_idx, 'triangle_in_circle', num_on)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                img_idx += 1
            print(f"Completed generating {samples_per_subcase1} samples for triangle_in_circle with {num_on} vertices on circle.")
        
        # 圆在三角形内的情况
        for num_tan in [0, 1, 3]:
            for _ in range(samples_per_subcase2):
                img_path, descs = gen_one_ct_special(img_idx, 'circle_in_triangle', num_tan)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                img_idx += 1
            print(f"Completed generating {samples_per_subcase2} samples for circle_in_triangle with {num_tan} tangents.")
    
    print('特殊圆和三角形生成完成！')

if __name__ == "__main__":
    main()
