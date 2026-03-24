"""生成微调数据集-特殊双图形中的两条线段"""
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
from geom.shapes import Line

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas_finetuning/datas_two_lines/images_two_l')
LABEL_FILE = os.path.join(project_root, 'datas_finetuning/datas_two_lines/labels_two_l.txt')
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
    """生成线条描述"""
    return f'line{idx} = Line(Point({start[0]:.1f},{start[1]:.1f}), Point({end[0]:.1f},{end[1]:.1f}))'

def are_collinear(p1, p2, p3):
    """检查三个点是否共线"""
    # 使用叉积判断，如果叉积为0则共线
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    x3, y3 = p3[0], p3[1]
    
    # 计算向量(p1->p2)和(p1->p3)的叉积
    cross_product = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
    return abs(cross_product) < 0.01

def angle_between_vectors_deg(v1, v2):
    """计算两向量的夹角(度)。v=(dx,dy)。返回[0,180]范围。
    若有零向量则返回 None。"""
    dx1, dy1 = v1
    dx2, dy2 = v2
    norm1 = math.hypot(dx1, dy1)
    norm2 = math.hypot(dx2, dy2)
    if norm1 == 0 or norm2 == 0:
        return None
    cos_theta = (dx1*dx2 + dy1*dy2) / (norm1 * norm2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    return math.degrees(math.acos(cos_theta))

def point_on_line_segment(line_start, line_end, t):
    """在线段上按比例t（0到1）生成一个点"""
    x = round(line_start[0] + t * (line_end[0] - line_start[0]), 1)
    y = round(line_start[1] + t * (line_end[1] - line_start[1]), 1)
    return (x, y)

def point_to_line_distance(point, line_start, line_end):
    """计算点到直线的距离"""
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # 使用点到直线距离公式：|ax + by + c| / sqrt(a² + b²)
    # 其中直线方程为：(y2-y1)x - (x2-x1)y + (x2-x1)y1 - (y2-y1)x1 = 0
    a = y2 - y1
    b = -(x2 - x1)
    c = (x2 - x1) * y1 - (y2 - y1) * x1
    
    distance = abs(a * x0 + b * y0 + c) / math.sqrt(a**2 + b**2)
    return distance

def calculate_distance(p1, p2):
    """计算两点之间的距离"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def generate_valid_line_points(min_length=1.0, max_length=8.0):
    """生成满足长度要求的线段端点"""
    while True:
        x1 = round(random.uniform(-4.9, 4.9), 1)
        y1 = round(random.uniform(-4.9, 4.9), 1)
        x2 = round(random.uniform(-4.9, 4.9), 1)
        y2 = round(random.uniform(-4.9, 4.9), 1)
        
        distance = calculate_distance((x1, y1), (x2, y2))
        if min_length <= distance <= max_length:
            return (x1, y1), (x2, y2)

def generate_shared_endpoint_lines():
    """生成有公共端点且不共线的两条线"""
    # 公共端点（1位小数）
    shared_x = round(random.uniform(-4.9, 4.9), 1)
    shared_y = round(random.uniform(-4.9, 4.9), 1)
    shared_point = (shared_x, shared_y)
    
    # 第一条线的另一个端点
    while True:
        x1, y1 = round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1)
        distance = calculate_distance(shared_point, (x1, y1))
        if 1.0 <= distance <= 8.0:  # 控制线段长度
            break
    
    # 第二条线的另一个端点，确保不共线、夹角>=10°且长度合适
    while True:
        x2, y2 = round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1)
        distance = calculate_distance(shared_point, (x2, y2))
        v1 = (x1 - shared_x, y1 - shared_y)
        v2 = (x2 - shared_x, y2 - shared_y)
        ang = angle_between_vectors_deg(v1, v2)
        if (1.0 <= distance <= 8.0 and 
            not are_collinear(shared_point, (x1, y1), (x2, y2)) and
            ang is not None and ang >= 10.0):
            break
    
    line1_start, line1_end = shared_point, (x1, y1)
    line2_start, line2_end = shared_point, (x2, y2)
    
    return line1_start, line1_end, line2_start, line2_end

def generate_point_on_line():
    """生成一条线的端点在另一条线上的两条线"""
    while True:
        # 先生成第一条线
        line1_start, line1_end = generate_valid_line_points()
        
        # 在第一条线上随机选择一个点（不是端点）
        t = random.uniform(0.1, 0.9)  # 避免选择端点
        point_on_line1 = point_on_line_segment(line1_start, line1_end, t)
        
        # 验证生成的点到第一条线的距离小于1e-10
        dist_to_line = point_to_line_distance(point_on_line1, line1_start, line1_end)
        if dist_to_line > 1e-10:
            continue  # 重新生成
        
        # 生成第二条线，其中一个端点在第一条线上；要求与第一条线夹角>=10°
        while True:
            x3, y3 = round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1)
            distance = calculate_distance(point_on_line1, (x3, y3))
            # 与第一条线的方向夹角
            dir1 = (line1_end[0] - line1_start[0], line1_end[1] - line1_start[1])
            dir2 = (x3 - point_on_line1[0], y3 - point_on_line1[1])
            ang = angle_between_vectors_deg(dir1, dir2)
            # 确保不共线、长度合适、夹角在[10°,170°]内（互补角也>=10°）
            if (1.0 <= distance <= 8.0 and 
                not are_collinear(line1_start, line1_end, (x3, y3)) and
                ang is not None and 10.0 <= ang <= 170.0):
                break
        
        # 随机决定第二条线的哪个端点在第一条线上
        if random.choice([True, False]):
            line2_start, line2_end = point_on_line1, (x3, y3)
        else:
            line2_start, line2_end = (x3, y3), point_on_line1
        
        return line1_start, line1_end, line2_start, line2_end

def generate_random_lines():
    """生成两条随机线"""
    # 第一条线
    line1_start, line1_end = generate_valid_line_points()
    
    # 第二条线
    line2_start, line2_end = generate_valid_line_points()
    
    return line1_start, line1_end, line2_start, line2_end

def gen_two_lines(img_idx, generation_type):
    """生成两条线的图像"""
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
    
    # 根据类型生成两条线
    if generation_type == "shared_endpoint":
        line1_start, line1_end, line2_start, line2_end = generate_shared_endpoint_lines()
    elif generation_type == "point_on_line":
        line1_start, line1_end, line2_start, line2_end = generate_point_on_line()
    else:  # random
        line1_start, line1_end, line2_start, line2_end = generate_random_lines()
    
    # 创建并显示两条线
    line1 = Line(Point(line1_start[0], line1_start[1]), Point(line1_end[0], line1_end[1]))
    line2 = Line(Point(line2_start[0], line2_start[1]), Point(line2_end[0], line2_end[1]))
    
    line1.show()
    line2.show()
    
    screen.update()
    
    # 保存图像
    ps_path = os.path.join(IMG_DIR, f'two_l{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'two_l{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    
    # 生成描述
    descs = [
        line_desc(1, line1_start, line1_end),
        line_desc(2, line2_start, line2_end)
    ]
    
    return png_path, descs

def get_next_img_idx(img_dir):
    """获取下一个图像索引"""
    if not os.path.exists(img_dir):
        return 1
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('two_l') and f.endswith('.png'):
            try:
                num = int(f[5:-4])  # 去掉'two_l'前缀和'.png'后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    """主函数"""
    # 每种类型生成1500个样本
    samples_per_type = 1500
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    generation_types = [
        ("shared_endpoint", "两条线有公共端点且不共线"),
        ("point_on_line", "一条线的端点在另一条线上且不共线"),
        ("random", "随机生成两条线")
    ]
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        img_idx = start_img_idx
        
        for gen_type, description in generation_types:
            print(f"正在生成: {description} ({samples_per_type}个样本)")
            
            for j in range(samples_per_type):
                img_path, descs = gen_two_lines(img_idx, gen_type)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                img_idx += 1
                
                if (j + 1) % 100 == 0:
                    print(f"  已完成 {j + 1}/{samples_per_type}")
    
    print(f'两条线生成完成！总共生成了 {len(generation_types) * samples_per_type} 个样本')
    print(f'图像保存在: {IMG_DIR}')
    print(f'标签保存在: {LABEL_FILE}')

if __name__ == "__main__":
    main() 