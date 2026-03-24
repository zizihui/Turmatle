"""生成微调数据集-特殊双图形中的两个三角形"""
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
from geom.shapes import Triangle

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_two_triangles/images_two_t')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_two_triangles/labels_two_t.txt')
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

def triangle_desc(idx, p1, p2, p3):
    return f'triangle{idx} = Triangle(Point({p1[0]:.1f},{p1[1]:.1f}), Point({p2[0]:.1f},{p2[1]:.1f}), Point({p3[0]:.1f},{p3[1]:.1f}))'

def calculate_area(p1, p2, p3):
    """计算三角形面积"""
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
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def distance(p1, p2):
    """计算两点间距离"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def is_valid_triangle(p1, p2, p3, min_area=1.0, min_angle_deg=15):
    """验证是否为有效的三角形"""
    # 检查所有点是否在画布范围内
    for point in [p1, p2, p3]:
        if not (-4.9 <= point[0] <= 4.9 and -4.9 <= point[1] <= 4.9):
            return False
    
    # 检查面积
    area = calculate_area(p1, p2, p3)
    if area <= min_area:
        return False
    
    # 计算三个角
    angles = [
        angle(p1, p2, p3),
        angle(p2, p1, p3),
        angle(p3, p1, p2)
    ]
    # 检查是否有无效角度或角度过小
    if any(a is None or a < min_angle_deg for a in angles):
        return False
    return True

def is_point_inside_triangle(point, p1, p2, p3):
    """判断点是否在三角形内部"""
    x, y = point
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    
    # 使用重心坐标判断
    denominator = (y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3)
    if abs(denominator) < 1e-10:
        return False
    
    a = ((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / denominator
    b = ((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / denominator
    c = 1 - a - b
    
    return a >= 0 and b >= 0 and c >= 0

def sample_point_inside_triangle_barycentric(t1, t2, t3, margin=0.5):
    """使用重心坐标在三角形内部采样一点。
    margin ∈ [0, 1/3)。若 margin>0，保证三权重均≥margin，让点远离边界。
    """
    # 先用简单的 Dirichlet(1,1,1) 采样（等价于三独立U(0,1)再归一化）
    a = random.random()
    b = random.random()
    c = random.random()
    s = a + b + c
    a, b, c = a / s, b / s, c / s
    if margin > 0:
        scale = 1.0 - 3.0 * margin
        a = margin + scale * a
        b = margin + scale * b
        c = margin + scale * c
        # 再次归一化以消除数值误差
        s2 = a + b + c
        a, b, c = a / s2, b / s2, c / s2
    x = a * t1[0] + b * t2[0] + c * t3[0]
    y = a * t1[1] + b * t2[1] + c * t3[1]
    return (round(x, 1), round(y, 1))

def generate_random_triangle():
    """生成随机三角形"""
    while True:
        p1 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p2 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p3 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        if is_valid_triangle(p1, p2, p3):
            return p1, p2, p3

def calculate_third_point_isosceles(p1, p2, height, upward=True):
    """根据等腰三角形的性质计算第三个点"""
    x1, y1 = p1
    x2, y2 = p2
    
    # 计算底边中点
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    # 计算底边的方向向量
    base_dx = x2 - x1
    base_dy = y2 - y1
    
    # 计算垂直向量
    perp_dx = -base_dy
    perp_dy = base_dx
    
    # 单位化垂直向量
    perp_length = math.sqrt(perp_dx**2 + perp_dy**2)
    if perp_length == 0:
        return None
    
    unit_perp_dx = perp_dx / perp_length
    unit_perp_dy = perp_dy / perp_length
    
    # 计算第三个顶点
    direction = 1 if upward else -1
    p3_x = round(mid_x + direction * height * unit_perp_dx, 1)
    p3_y = round(mid_y + direction * height * unit_perp_dy, 1)
    
    return (p3_x, p3_y)

def generate_isosceles_triangle():
    """生成等腰三角形"""
    while True:
        # 随机生成两个点作为底边（1位小数）
        p1 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p2 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        
        if p1 == p2:
            continue
        
        # 计算底边长度
        base_length = distance(p1, p2)
        
        # 随机生成高度
        min_height = 2.0 / base_length + 0.1
        max_height = 8.0
        
        if min_height >= max_height:
            continue
        
        height = round(random.uniform(min_height, max_height), 1)
        upward = random.choice([True, False])
        
        p3 = calculate_third_point_isosceles(p1, p2, height, upward)
        
        if p3 is None:
            continue
        
        # 验证等腰性质
        d1 = distance(p1, p2)
        d2 = distance(p2, p3)
        d3 = distance(p3, p1)
        sides = [d1, d2, d3]
        sides.sort()
        
        is_isosceles = (abs(sides[0] - sides[1]) < 0.01 or 
                       abs(sides[1] - sides[2]) < 0.01)
        
        if is_isosceles and is_valid_triangle(p1, p2, p3):
            return p1, p2, p3

def calculate_third_point_equilateral(p1, p2, upward=True):
    """根据等边三角形的性质计算第三个点"""
    x1, y1 = p1
    x2, y2 = p2
    
    # 计算中点
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    # 计算边长
    side_length = distance(p1, p2)
    
    # 等边三角形的高
    height = side_length * math.sqrt(3) / 2
    
    # 计算底边的方向向量
    base_dx = x2 - x1
    base_dy = y2 - y1
    
    # 计算垂直向量
    perp_dx = -base_dy
    perp_dy = base_dx
    
    # 单位化垂直向量
    perp_length = math.sqrt(perp_dx**2 + perp_dy**2)
    if perp_length == 0:
        return None
    
    unit_perp_dx = perp_dx / perp_length
    unit_perp_dy = perp_dy / perp_length
    
    # 计算第三个顶点
    direction = 1 if upward else -1
    p3_x = round(mid_x + direction * height * unit_perp_dx, 1)
    p3_y = round(mid_y + direction * height * unit_perp_dy, 1)
    
    return (p3_x, p3_y)

def generate_equilateral_triangle():
    """生成等边三角形"""
    while True:
        # 随机生成两个点（1位小数）
        p1 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p2 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        
        if p1 == p2:
            continue
        
        upward = random.choice([True, False])
        p3 = calculate_third_point_equilateral(p1, p2, upward)
        
        if p3 is None:
            continue
        
        # 验证等边性质
        d1 = distance(p1, p2)
        d2 = distance(p2, p3)
        d3 = distance(p3, p1)
        
        max_diff = max(abs(d1-d2), abs(d2-d3), abs(d3-d1))
        if max_diff <= 0.01 and is_valid_triangle(p1, p2, p3):
            return p1, p2, p3

def calculate_third_point_right_angle(p1, p2, height, from_p1=True, upward=True):
    """根据直角三角形的性质计算第三个点"""
    x1, y1 = p1
    x2, y2 = p2
    
    # 选择直角顶点
    right_vertex = p1 if from_p1 else p2
    
    # 计算底边的方向向量
    base_dx = x2 - x1
    base_dy = y2 - y1
    
    # 计算垂直向量
    perp_dx = -base_dy
    perp_dy = base_dx
    
    # 单位化垂直向量
    perp_length = math.sqrt(perp_dx**2 + perp_dy**2)
    if perp_length == 0:
        return None
    
    unit_perp_dx = perp_dx / perp_length
    unit_perp_dy = perp_dy / perp_length
    
    # 根据upward参数确定方向
    direction = 1 if upward else -1
    
    # 计算第三个顶点
    p3_x = round(right_vertex[0] + direction * height * unit_perp_dx, 1)
    p3_y = round(right_vertex[1] + direction * height * unit_perp_dy, 1)
    
    return (p3_x, p3_y)

def generate_right_triangle():
    """生成直角三角形"""
    while True:
        # 随机生成两个点作为底边（1位小数）
        p1 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p2 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        
        if p1 == p2:
            continue
        
        # 计算底边长度
        base_length = distance(p1, p2)
        
        # 随机生成高度
        min_height = 2.0 / base_length + 0.1
        max_height = 8.0
        
        if min_height >= max_height:
            continue
        
        height = round(random.uniform(min_height, max_height), 1)
        from_p1 = random.choice([True, False])
        upward = random.choice([True, False])
        
        p3 = calculate_third_point_right_angle(p1, p2, height, from_p1, upward)
        
        if p3 is None:
            continue
        
        # 验证直角性质
        angles = [
            angle(p1, p2, p3),
            angle(p2, p1, p3),
            angle(p3, p1, p2)
        ]
        
        if any(a is None for a in angles):
            continue
        
        has_right_angle = any(abs(a - 90) < 0.01 for a in angles)
        if has_right_angle and is_valid_triangle(p1, p2, p3):
            return p1, p2, p3

def generate_triangle_by_type(triangle_type):
    """根据类型生成三角形"""
    if triangle_type == 'random':
        return generate_random_triangle()
    elif triangle_type == 'isosceles':
        return generate_isosceles_triangle()
    elif triangle_type == 'equilateral':
        return generate_equilateral_triangle()
    elif triangle_type == 'right':
        return generate_right_triangle()
    else:
        return generate_random_triangle()

def generate_triangles_with_common_vertex():
    """生成有一个公共顶点的两个三角形"""
    while True:
        # 生成第一个三角形
        triangle_type1 = random.choice(['random', 'isosceles', 'equilateral', 'right'])
        t1_p1, t1_p2, t1_p3 = generate_triangle_by_type(triangle_type1)
        
        # 选择一个公共顶点
        common_vertex = random.choice([t1_p1, t1_p2, t1_p3])
        
        # 生成第二个三角形，确保有一个顶点是公共顶点
        # 先生成两个不同于公共顶点的新点（1位小数）
        while True:
            p1 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
            p2 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
            
            # 确保新点不与公共顶点重合，且能构成有效三角形
            if (p1 != common_vertex and p2 != common_vertex and p1 != p2 and
                is_valid_triangle(common_vertex, p1, p2)):
                t2_p1, t2_p2, t2_p3 = common_vertex, p1, p2
                
                # 验证两个三角形不重合
                triangle1_points = {t1_p1, t1_p2, t1_p3}
                triangle2_points = {t2_p1, t2_p2, t2_p3}
                if len(triangle1_points.intersection(triangle2_points)) == 1:  # 只有一个公共点
                    return (t1_p1, t1_p2, t1_p3), (t2_p1, t2_p2, t2_p3)

def generate_triangles_with_common_edge():
    """生成有一条公共边的两个三角形"""
    while True:
        # 生成第一个三角形
        triangle_type1 = random.choice(['random', 'isosceles', 'equilateral', 'right'])
        t1_p1, t1_p2, t1_p3 = generate_triangle_by_type(triangle_type1)
        
        # 选择一条边作为公共边
        edges = [(t1_p1, t1_p2), (t1_p2, t1_p3), (t1_p3, t1_p1)]
        common_edge = random.choice(edges)
        
        # 生成第二个三角形，共享这条边
        while True:
            p3 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
            
            # 确保第三个点不在已选边上，且能构成有效三角形
            if (p3 != common_edge[0] and p3 != common_edge[1] and
                is_valid_triangle(common_edge[0], common_edge[1], p3)):
                t2_p1, t2_p2, t2_p3 = common_edge[0], common_edge[1], p3
                
                # 验证两个三角形不重合
                triangle1_points = {t1_p1, t1_p2, t1_p3}
                triangle2_points = {t2_p1, t2_p2, t2_p3}
                if len(triangle1_points.intersection(triangle2_points)) == 2:  # 有两个公共点（一条公共边）
                    return (t1_p1, t1_p2, t1_p3), (t2_p1, t2_p2, t2_p3)

def generate_containing_triangles():
    """生成包含关系的两个三角形（大三角形包含小三角形）——使用重心坐标快速采样。"""
    while True:
        # 生成一个较大的三角形
        triangle_type1 = random.choice(['random', 'isosceles', 'equilateral', 'right'])
        large_t = generate_triangle_by_type(triangle_type1)
        A, B, C = large_t
        # 在内部采样小三角形三个点；加入边距避免贴边导致退化
        for _ in range(100):
            p1 = sample_point_inside_triangle_barycentric(A, B, C, margin=0.5)
            p2 = sample_point_inside_triangle_barycentric(A, B, C, margin=0.5)
            p3 = sample_point_inside_triangle_barycentric(A, B, C, margin=0.5)
            if is_valid_triangle(p1, p2, p3, min_area=1.0, min_angle_deg=15):
                return large_t, (p1, p2, p3)
        # 若连续多次失败，则重新采一个大三角形

def generate_random_triangles():
    """生成两个随机的三角形"""
    triangle_type1 = random.choice(['random', 'isosceles', 'equilateral', 'right'])
    triangle_type2 = random.choice(['random', 'isosceles', 'equilateral', 'right'])
    
    t1 = generate_triangle_by_type(triangle_type1)
    t2 = generate_triangle_by_type(triangle_type2)
    
    return t1, t2

def gen_two_triangles(img_idx, generation_type):
    """生成两个三角形的图像"""
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
    
    # 根据类型生成两个三角形
    if generation_type == "common_vertex":
        result = generate_triangles_with_common_vertex()
    elif generation_type == "common_edge":
        result = generate_triangles_with_common_edge()
    elif generation_type == "containing":
        result = generate_containing_triangles()
    else:  # random
        result = generate_random_triangles()
    
    if result is None:
        return None, None  # 生成失败
    
    (t1_p1, t1_p2, t1_p3), (t2_p1, t2_p2, t2_p3) = result
    
    # 创建并显示两个三角形
    triangle1 = Triangle(Point(*t1_p1), Point(*t1_p2), Point(*t1_p3))
    triangle2 = Triangle(Point(*t2_p1), Point(*t2_p2), Point(*t2_p3))
    
    triangle1.show()
    triangle2.show()
    
    screen.update()
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, f'two_t{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'two_t{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    
    # 生成描述
    descs = [
        triangle_desc(1, t1_p1, t1_p2, t1_p3),
        triangle_desc(2, t2_p1, t2_p2, t2_p3)
    ]
    
    return png_path, descs

def get_next_img_idx(img_dir):
    """获取下一个图像索引"""
    if not os.path.exists(img_dir):
        return 1
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('two_t') and f.endswith('.png'):
            try:
                num = int(f[5:-4])  # 去掉'tt'前缀和'.png'后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    """主函数"""
    # 每种类型生成5000个样本
    samples_per_type = 5000
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    generation_types = [
        ("common_vertex", "有一个公共顶点的两个三角形"),
        ("common_edge", "有一条公共边的两个三角形"),
        ("containing", "包含关系的两个三角形"),
        ("random", "随机的两个三角形")
    ]
    
    print(f"开始生成两三角形组合，总共{len(generation_types) * samples_per_type}张图像...")
    print(f"输出目录: {IMG_DIR}")
    print(f"标签文件: {LABEL_FILE}")
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        
        for gen_type, description in generation_types:
            print(f"正在生成: {description} ({samples_per_type}个样本)")
            
            generated = 0
            while generated < samples_per_type:
                result = gen_two_triangles(img_idx, gen_type)
                if result[0] is not None:  # 生成成功
                    img_path, descs = result
                    rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                    f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                    generated += 1
                    img_idx += 1
                    
                    if generated % 100 == 0:
                        print(f"  已完成 {generated}/{samples_per_type}")
                else:
                    # 生成失败，重试但不增加img_idx
                    continue
    
    print(f'两三角形生成完成！总共生成了 {len(generation_types) * samples_per_type} 个样本')
    print(f'图像保存在: {IMG_DIR}')
    print(f'标签保存在: {LABEL_FILE}')

if __name__ == "__main__":
    main()