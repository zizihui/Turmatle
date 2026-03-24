import sys
import os

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from geom import Geom, Point, Line, Text
from geom.effects import Flash, Outline, Scale, Indicate
import turtle
from PIL import Image

def main():
    Geom.setup_canvas(1000, 1000)   # DPI 感知 + 1000×1000 画布
    # 设置全局默认值
    Geom.set_defaults(origin_x=0, origin_y=0, scale=150, fontsize=25)

    WIDTH, HEIGHT = 1000, 1000
    IMG_DIR = os.path.join(project_root, 'examples/images')
    os.makedirs(IMG_DIR, exist_ok=True) # 创建images目录
    
    # 创建坐标轴
    x_axis = Line(Point(-2, 0), Point(3, 0), 
                  speed=0, pensize=3, 
                  arrow=True,
                  color="gray", text="x")
    y_axis = Line(Point(0, -2), Point(0, 3), 
                  speed=0, pensize=3,
                  arrow=True,
                  color="gray", text="y")

    # 创建不同样式的文本
    text1 = Text(
        position=Point(1, 2),
        text="Hello, World!",
        color="blue",
        fontsize=30,
        bold=True
    )

    text2 = Text(
        position=Point(0, 1),
        text="Centered Text",
        color="red",
        fontsize=30,
        align="center",
        italic=True
    )

    text3 = Text(
        position=Point(-1,-1),
        text="Right Aligned",
        color="green",
        fontsize=30,
        align="right",
        bold=True,
        italic=True
    )

    # 显示所有元素
    x_axis.show()
    y_axis.show()
    text1.show()
    text1.play(Outline())
    text2.show()
    text3.show()

    screen = turtle.Screen()
    screen.update()  # 更新画面

    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'demo_texts.ps')
    png_path = os.path.join(IMG_DIR, 'demo_texts.png')
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