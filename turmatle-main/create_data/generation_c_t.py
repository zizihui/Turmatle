"""生成预训练数据集-混合双图形中的圆和三角形"""
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
IMG_DIR = os.path.join(project_root, 'datas/datas_c_t/images_c_t')
LABEL_FILE = os.path.join(project_root, 'datas/datas_c_t/labels_c_t.txt')
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
        if f.startswith('ct') and f.endswith('.png'):
            try:
                num = int(f[2:-4])
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

def is_valid_triangle(p1, p2, p3, min_area=1.0, min_angle_deg=15):
    """验证是否为有效的三角形"""
    # 检查面积
    area = calculate_area(p1, p2, p3)
    if area <= min_area:
        return False
    
    # 计算三个角（现在直接得到度数）
    angles = [
        angle(p1, p2, p3),  # p1处的角
        angle(p2, p1, p3),  # p2处的角  
        angle(p3, p1, p2)   # p3处的角
    ]
    # 检查是否有无效角度（None）或角度过小
    if any(a is None or a < min_angle_deg for a in angles):
        return False
    return True

def gen_one_ct(img_idx, n_circles, n_triangles, circle_start_idx=1, triangle_start_idx=1):
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
    # 生成圆
    for i in range(n_circles):
        max_r = 5 - 0.1
        r = round(random.uniform(0.1, max_r), 1)
        x0 = round(random.uniform(-4.9 + r, 4.9 - r), 1)
        y0 = round(random.uniform(-4.9 + r, 4.9 - r), 1)
        circle = Circle(Point(x0, y0), r)
        circle.show()
        descs.append(circle_desc(circle_start_idx + i, (x0, y0), r))
    # 生成三角形
    for i in range(n_triangles):
        while True:
            p1 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
            p2 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
            p3 = (round(random.uniform(-4.9, 4.9), 1), round(random.uniform(-4.9, 4.9), 1))
            if is_valid_triangle(p1, p2, p3):
                break
        triangle = Triangle(Point(*p1), Point(*p2), Point(*p3))
        triangle.show()
        descs.append(triangle_desc(triangle_start_idx + i, p1, p2, p3))
    screen.update()
    ps_path = os.path.join(IMG_DIR, f'ct{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'ct{img_idx}.png')
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
    
    samples_per_group = 80000
    start_img_idx = get_next_img_idx(IMG_DIR)
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        ct_idx = start_img_idx
        for n_circles in range(1, 2):
            for n_triangles in range(1, 2):
                for j in range(samples_per_group):
                    img_path, descs = gen_one_ct(ct_idx, n_circles, n_triangles, circle_start_idx=1, triangle_start_idx=1)
                    rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                    f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                    ct_idx += 1
    print('Circle+Triangle混合生成完成！')

if __name__ == "__main__":
    main() 