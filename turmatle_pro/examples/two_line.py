import sys
import os

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from geom import Geom, Point, Line, Rect, Text
from geom.effects import Outline, Scale
import turtle   
from PIL import Image


def main():
    # 画布初始化（Enhanced 体系）
    Geom.setup_canvas(1000, 1000)

    # 设置全局默认值
    Geom.set_defaults(origin_x=0, origin_y=0, scale=100, fontsize=25)

    WIDTH, HEIGHT = 1000, 1000
    IMG_DIR = os.path.join(project_root, 'examples/images')
    os.makedirs(IMG_DIR, exist_ok=True) # 创建images目录

    # =========================
    # 线段 a1（数学语义表达）
    # =========================
    line1 = Line(
        start=Point(-2.8, -1.7),
        end=Point(2.2,-1.7),
        pensize=5,
        arrow=False,          # 融合箭头（方向属性）
        color="black",
        text=None           # 数学标注
    )
    #跟 line1垂直的线段b
    line2 = Line(
        start=Point(0,-2.8),
        end=Point(0,2.4),
        pensize=5,
        arrow=False,          # 融合箭头（方向属性）
        color="black",
        text=None           # 数学标注
    )
    # =====================
    line1.show()
    line2.show()
    screen = turtle.Screen()
    screen.update()  # 更新画面

    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'two_line.ps')
    png_path = os.path.join(IMG_DIR, 'two_line.png')
    canvas = screen.getcanvas()
    canvas.postscript(file=ps_path, colormode='color', width=WIDTH, height=HEIGHT)
    
    # 使用PIL处理图像
    img = Image.open(ps_path)
    img = img.crop(img.getbbox())  # 自动去除白边
    img = img.resize((WIDTH, HEIGHT))  # 强制拉伸到目标尺寸
    img.save(png_path)
    os.remove(ps_path)  # 删除中间的ps文件
    
    print(f"图像已保存到: {png_path}")  
    turtle.done()


if __name__ == "__main__":
    main()