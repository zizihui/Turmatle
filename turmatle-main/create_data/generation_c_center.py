"""生成预训练数据集-特殊单图形中的居中圆"""
import os
import sys
import random
import turtle
import ctypes
from PIL import Image

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from geom.base import Geom, Point
from geom.shapes import Circle

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas/datas_c_center/images_c_center')
LABEL_FILE = os.path.join(project_root, 'datas/datas_c_center/labels_c_center.txt')
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

def gen_one_circle_center(img_idx, n_circles, circle_start_idx=1):
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
    for i in range(n_circles):
        # 随机选择生成模式：50%概率生成随机圆心圆，50%概率生成中心圆
        if random.choice([True, False]):
            # 模式1: 随机圆心圆（圆心在-3到3范围内）
            x0 = round(random.uniform(-3, 3), 1)
            y0 = round(random.uniform(-3, 3), 1)
            
            # 根据圆心位置计算最大半径，确保圆不超出画布边界
            # 画布逻辑坐标范围大约是-5到5
            max_r_x = min(4.9 - x0, x0 + 4.9)  # x方向的最大半径
            max_r_y = min(4.9 - y0, y0 + 4.9)  # y方向的最大半径
            max_r = min(max_r_x, max_r_y)  # 取较小值确保不超界
            
            # 确保最大半径至少为0.1，避免生成过小的圆
            max_r = max(max_r, 0.1)
    
            # 生成半径，范围从0.1到计算出的最大半径
            r = round(random.uniform(0.1, max_r), 1)
        else:
            # 模式2: 中心圆（圆心固定在原点，半径0.1～4.9）
            x0 = 0.0  # 保持1位小数的一致性
            y0 = 0.0  # 保持1位小数的一致性
            r = round(random.uniform(0.1, 4.9), 1)
        
        circle = Circle(Point(x0, y0), r)
        circle.show()
        descs.append(circle_desc(circle_start_idx + i, (x0, y0), r))
    screen.update()
    ps_path = os.path.join(IMG_DIR, f'c_center{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'c_center{img_idx}.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)
    return png_path, descs

def get_next_img_idx(img_dir):
    files = os.listdir(img_dir)
    nums = []
    for f in files:
        if f.startswith('c_center') and f.endswith('.png'):
            try:
                num = int(f[8:-4])  # 跳过'c_center'前缀，去掉'.png'后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    samples_per_group = 50000
    start_img_idx = get_next_img_idx(IMG_DIR)
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        circle_center_idx = start_img_idx
        for n_circles in range(1, 2):
            for j in range(samples_per_group):
                img_path, descs = gen_one_circle_center(circle_center_idx, n_circles, circle_start_idx=1)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                circle_center_idx += 1
    print('Circle_center生成完成！')

if __name__ == "__main__":
    main() 