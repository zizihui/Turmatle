"""生成预训练数据集-基础单图形中的矩形"""
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
from geom.shapes import Rect

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas/datas_r/images_r')
LABEL_FILE = os.path.join(project_root, 'datas/datas_r/labels_r.txt')
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

def rect_desc(idx, bottom_left, top_right):
    return f'rect{idx} = Rect(Point({bottom_left[0]:.1f},{bottom_left[1]:.1f}), Point({top_right[0]:.1f},{top_right[1]:.1f}))'

def gen_one_rect(img_idx, n_rects, rect_start_idx=1):
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
    for i in range(n_rects):
        # 直接生成1位小数的坐标
        x1 = round(random.uniform(-4.9, 4.8), 1)
        y1 = round(random.uniform(-4.9, 4.8), 1)
        x2 = round(random.uniform(x1+0.1, 4.9), 1)
        y2 = round(random.uniform(y1+0.1, 4.9), 1)
        rect = Rect(Point(x1, y1), Point(x2, y2))
        rect.show()
        descs.append(rect_desc(rect_start_idx + i, (x1, y1), (x2, y2)))
    screen.update()
    ps_path = os.path.join(IMG_DIR, f'r{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'r{img_idx}.png')
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
        if f.startswith('r') and f.endswith('.png'):
            try:
                num = int(f[1:-4])
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    samples_per_group = 80000
    start_img_idx = get_next_img_idx(IMG_DIR)
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:
        rect_idx = start_img_idx
        for n_rects in range(1, 2):
            for j in range(samples_per_group):
                img_path, descs = gen_one_rect(rect_idx, n_rects, rect_start_idx=1)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                rect_idx += 1
    print('Rect生成完成！')

if __name__ == "__main__":
    main() 