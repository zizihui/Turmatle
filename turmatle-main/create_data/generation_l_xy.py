"""生成预训练数据集-特殊单图形中的水平/垂直线段"""
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
from geom.shapes import Line

# 画布参数
WIDTH, HEIGHT = 1000, 1000
IMG_DIR = os.path.join(project_root, 'datas/datas_l_xy/images_l_xy')
LABEL_FILE = os.path.join(project_root, 'datas/datas_l_xy/labels_l_xy.txt')
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

def gen_one_line_xy(img_idx, n_lines, line_start_idx=1):
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
    
    for i in range(n_lines):
        # 随机选择生成水平线还是垂直线
        line_type = random.choice(['horizontal', 'vertical'])
        
        if line_type == 'horizontal':
            # 水平线：y坐标相同
            y = round(random.uniform(-4.9, 4.9), 1)
            x1 = round(random.uniform(-4.9, 4.9), 1)
            x2 = round(random.uniform(-4.9, 4.9), 1)
            # 确保x1 != x2，避免生成点
            while x1 == x2:
                x2 = round(random.uniform(-4.9, 4.9), 1)
            line = Line(Point(x1, y), Point(x2, y))
            descs.append(line_desc(line_start_idx + i, (x1, y), (x2, y)))
        else:
            # 垂直线：x坐标相同
            x = round(random.uniform(-4.9, 4.9), 1)
            y1 = round(random.uniform(-4.9, 4.9), 1)
            y2 = round(random.uniform(-4.9, 4.9), 1)
            # 确保y1 != y2，避免生成点
            while y1 == y2:
                y2 = round(random.uniform(-4.9, 4.9), 1)
            line = Line(Point(x, y1), Point(x, y2))
            descs.append(line_desc(line_start_idx + i, (x, y1), (x, y2)))
        
        line.show()
    screen.update()
    ps_path = os.path.join(IMG_DIR, f'l_xy{img_idx}.ps')
    png_path = os.path.join(IMG_DIR, f'l_xy{img_idx}.png')
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
        if f.startswith('l_xy') and f.endswith('.png'):
            try:
                num = int(f[4:-4])  # 去掉'l_xy'前缀和'.png'后缀
                nums.append(num)
            except:
                pass
    return max(nums) + 1 if nums else 1

def main():
    # 设置DPI感知
    set_dpi_awareness()
    
    samples_per_group = 50000
    start_img_idx = get_next_img_idx(IMG_DIR)
    
    print(f"开始生成水平和垂直直线，总共{samples_per_group}张图像...")
    print(f"输出目录: {IMG_DIR}")
    print(f"标签文件: {LABEL_FILE}")
    
    with open(LABEL_FILE, 'a', encoding='utf-8') as f:  # 用追加模式
        line_xy_idx = start_img_idx
        for n_lines in range(1, 2):  # 每张图像生成1条直线
            for j in range(samples_per_group):
                img_path, descs = gen_one_line_xy(line_xy_idx, n_lines, line_start_idx=1)
                rel_path = os.path.relpath(img_path, start=os.path.dirname(LABEL_FILE))
                f.write(rel_path + '\t' + '<br>'.join(descs) + '\n')
                line_xy_idx += 1
                
                # 显示进度
                if j % 500 == 0:
                    print(f"已生成 {j} 张图像...")
    
    print(f'水平和垂直直线生成完成！共生成 {samples_per_group} 张图像')

if __name__ == "__main__":
    main() 