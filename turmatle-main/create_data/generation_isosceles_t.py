"""生成预训练数据集-特殊单图形中的等腰三角形"""
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
IMG_DIR = os.path.join(project_root, 'datas/datas_isosceles_t/images_iso_t')
LABEL_FILE = os.path.join(project_root, 'datas/datas_isosceles_t/labels_iso_t.txt')
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

def angle(P1,P2,P3):
    p1p2 = (P2[0]-P1[0],P2[1]-P1[1])
    p1p3 = (P3[0]-P1[0],P3[1]-P1[1])
    dot_product = p1p2[0]*p1p3[0] + p1p2[1]*p1p3[1]
    norm_p1p2 = math.sqrt(p1p2[0]**2 + p1p2[1]**2)
    norm_p1p3 = math.sqrt(p1p3[0]**2 + p1p3[1]**2)
    if norm_p1p2 == 0 or norm_p1p3 == 0:
        return None  # 返回None表示无效角度，需要重新生成
    cos_theta = dot_product / (norm_p1p2 * norm_p1p3)
    # 防止数值误差导致超出[-1,1]
    cos_theta = max(-1, min(1, cos_theta))
    angle_rad = math.acos(cos_theta)
    angle_deg = math.degrees(angle_rad)
    return angle_deg  # 转换为度数返回

def distance(p1, p2):
    """计算两点间距离"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def calculate_third_point_isosceles(p1, p2, height, upward=True):
    """
    根据等腰三角形的性质，由两个底边点和高度计算第三个点
    
    Args:
        p1, p2: 底边的两个点 (x, y)
        height: 三角形的高度
        upward: True表示第三个点在p1p2连线的上方，False表示下方
    
    Returns:
        tuple: 第三个点的坐标 (x, y)
    """
    x1, y1 = p1
    x2, y2 = p2
    
    # 计算底边中点
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    # 计算底边的方向向量
    base_dx = x2 - x1
    base_dy = y2 - y1
    
    # 计算垂直向量（逆时针旋转90度）
    perp_dx = -base_dy
    perp_dy = base_dx
    
    # 单位化垂直向量
    perp_length = math.sqrt(perp_dx**2 + perp_dy**2)
    if perp_length == 0:
        return None  # 两点重合，无法构成三角形
    
    unit_perp_dx = perp_dx / perp_length
    unit_perp_dy = perp_dy / perp_length
    
    # 计算第三个顶点
    direction = 1 if upward else -1
    p3_x = round(mid_x + direction * height * unit_perp_dx, 1)  # 保留一位小数
    p3_y = round(mid_y + direction * height * unit_perp_dy, 1)  # 保留一位小数
    
    return (p3_x, p3_y)


def is_valid_isosceles_triangle(p1, p2, p3, min_area=1.0, min_angle_deg=15, tolerance=0.01):
    """验证是否为有效的等腰三角形"""
    # 检查所有点是否在画布范围内
    for point in [p1, p2, p3]:
        if not (-4.9 <= point[0] <= 4.9 and -4.9 <= point[1] <= 4.9):
            return False
    
    # 检查面积
    area = calculate_area(p1, p2, p3)
    if area <= min_area:
        return False
    
    # 计算三边长度
    d1 = distance(p1, p2)
    d2 = distance(p2, p3)
    d3 = distance(p3, p1)
    
    # 检查是否等腰（至少有两边相等）
    sides = [d1, d2, d3]
    sides.sort()
    
    # 检查是否有两边相等（允许0.01的小误差）
    is_isosceles = (abs(sides[0] - sides[1]) < tolerance or 
                   abs(sides[1] - sides[2]) < tolerance)
    
    if not is_isosceles:
        return False
        
    # 检查角度
    angles = [
        angle(p1, p2, p3),  # p1处的角
        angle(p2, p1, p3),  # p2处的角  
        angle(p3, p1, p2)   # p3处的角
    ]
    # 检查是否有无效角度（None）或角度过小
    if any(a is None or a < min_angle_deg for a in angles):
        return False
    
    return True

def generate_isosceles_triangle(min_area=1.0, min_angle_deg=15): 
    """
    通过随机生成两个点作为底边，随机生成高度来生成等腰三角形
    
    Args:
        min_area: 最小面积要求
        min_angle_deg: 最小角度要求（度数）
    
    Returns:
        tuple: 三个顶点坐标 (p1, p2, p3)
    """
    while True:  # 无限循环直到生成成功
        # 随机生成两个点作为底边（1位小数）
        p1 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        p2 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
        
        # 判断两点是否重合
        if p1 == p2:  # 直接判断是否相等
            continue  # 重合则重新开始
        
        # 计算底边长度
        base_length = distance(p1, p2)
        
        # 随机生成高度（考虑面积要求，area = 0.5 * base * height > min_area）
        # 所以 height > 2 * min_area / base_length
        min_height = 2.0 * min_area / base_length + 0.1  # 加上一点余量
        max_height = 8.0  # 设定一个合理的最大高度，避免超出画布
        
        if min_height >= max_height:
            continue  # 底边太长，无法满足面积要求
        
        height = round(random.uniform(min_height, max_height), 1)
        
        # 随机选择第三个点在上方还是下方
        upward = random.choice([True, False])
        
        # 计算第三个点
        p3 = calculate_third_point_isosceles(p1, p2, height, upward)
        
        if p3 is None:
            continue  # 计算失败，重新生成
        
        # 验证生成的三角形是否有效
        if is_valid_isosceles_triangle(p1, p2, p3, min_area, min_angle_deg):
            return p1, p2, p3
        
        # 如果不满足条件，继续下一次循环


def gen_one_isosceles_triangle(img_idx, n_triangles, triangle_start_idx=1):
    """生成一张包含指定数量等腰三角形的图片"""
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
    print("逻辑画布大小（单位：turtle坐标）:", screen.screensize())
    print("窗口像素宽度:", screen.window_width())
    print("窗口像素高度:", screen.window_height())
    screen.tracer(0)
    
    descs = []
    for i in range(n_triangles):
        p1, p2, p3 = generate_isosceles_triangle()
        triangle = Triangle(Point(*p1), Point(*p2), Point(*p3))
        triangle.show()
        descs.append(triangle_desc(triangle_start_idx + i, p1, p2, p3))
    screen.update()
    
    # 保存图片
    ps_path = os.path.join(IMG_DIR, f'iso_t{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'iso_t{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    
    return png_path, descs

def get_next_img_idx(img_dir):
    """获取下一个三角形索引"""
    if not os.path.exists(img_dir):
        return 1
        
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('iso_t') and f.endswith('.png'):
            try:
                num = int(f[5:-4])  # 去掉 'iso_t' 前缀和 '.png' 后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    samples_per_group = 60000  # 每组生成的图片数量
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        iso_triangle_idx = start_img_idx
        
        # 生成包含1个等腰三角形的图片
        for n_triangles in range(1, 2):
            print(f"正在生成包含 {n_triangles} 个等腰三角形的图片...")
            
            for j in range(samples_per_group):
                img_path, descs = gen_one_isosceles_triangle(iso_triangle_idx, n_triangles, triangle_start_idx=1)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                iso_triangle_idx += 1
                
                if (j + 1) % 100 == 0:
                    print(f"已生成 {j + 1}/{samples_per_group} 张图片")
    
    print('等腰三角形生成完成！')

if __name__ == "__main__":
    main()