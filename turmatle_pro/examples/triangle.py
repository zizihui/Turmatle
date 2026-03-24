import sys
import os

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 现在导入应该可以工作了
from geom import Geom, Point, Line, Function, Rect,Triangle,Text
from geom.effects import Flash, Outline, Scale, Indicate
import math
import turtle
from PIL import Image

def main():
    Geom.setup_canvas(1000, 1000)   # DPI 感知 + 1000×1000 画布
    # 设置全局默认值
    Geom.set_defaults(origin_x=0, origin_y=0, scale=100, fontsize=25)

    WIDTH, HEIGHT = 1000, 1000
    IMG_DIR = os.path.join(project_root, 'examples/images')
    os.makedirs(IMG_DIR, exist_ok=True) # 创建images目录

    # 创建坐标轴
    # x_axis = Line(Point(-1, 0), Point(5, 0), 
    #               speed=0, pensize=3, arrow=True,
    #               color="gray", text="x")
    # y_axis = Line(Point(0, -1), Point(0, 3), 
    #               speed=0, pensize=3,arrow=True,
    #               color="gray", text="y")
    triangle1 = Triangle(Point(-5.0,1.6), Point(-5.0,-3.2), Point(3.6,1.6))
    # 创建三角形
    # triangle1 = Triangle(
    #     p1=Point(-3.8,-3.4),
    #     p2=Point(-3.8,3.4),
    #     p3=Point(2,-3.4),
    #     # sides=(2,4),            # 或者p1,p2,p3;或着sides=(3,4),angle=90
    #     # angle=60,                    # 两边夹角
    #     pivot="p1",               # 旋转中心："center" / "p1" / "p2" / "p3" / Point
    #     rotation_deg=0,               # 旋转角度，不旋转0
    #     direction=-1,                  # 旋转方向：逆时针1，顺时针-1
    #     color="black",                  # 线条颜色
    #     pensize=3,                    # 线条粗细，None默认1
    #     fill=False,                    # 是否填充
    #     fill_color="YELLOW",           # 填充颜色
    #     text=None,                    # 文本内容
    #     text_pos=None                 # 文本位置，默认最右边线外侧
    # )
    # # 顶点标注
    # A_label = Text(
    #     position=Point(2,-3.4),     # 文本位置
    #     text="A",                   # 文本内容
    #     color="black",              # 文本颜色
    #     fontsize=None,              # 字体大小，不指定即为Geom默认
    #     align="center",             # 对齐方式'left', 'center', 'right'
    #     bold=False,                 # 是否加粗
    #     italic=False,               # 是否斜体
    # )
    # B_label = Text(
    #     position=Point(-3.8,3.4),     # 文本位置
    #     text="B",                   # 文本内容
    #     color="black",              # 文本颜色
    #     fontsize=None,              # 字体大小，不指定即为Geom默认
    #     align="center",             # 对齐方式'left', 'center', 'right'
    #     bold=False,                 # 是否加粗
    #     italic=False,               # 是否斜体
    # )
    # C_label = Text(
    #     position=Point(-3.9,-3.5),     # 文本位置
    #     text="C",                   # 文本内容
    #     color="black",              # 文本颜色
    #     fontsize=None,              # 字体大小，不指定即为Geom默认
    #     align="center",             # 对齐方式'left', 'center', 'right'
    #     bold=False,                 # 是否加粗
    #     italic=False,               # 是否斜体
    # )

#     line1=Line(
#         start=Point(-2,0),
#         end=Point(2.5,1.5),
#         color="red",
#         pensize=3,
#         arrow=False,
#         text="D",
#         # text_pos=Point(3.0,1.6)
# )

    # 显示所有元素
    triangle1.show()
    # triangle1.play(Outline())
    # line1.show()
    # A_label.show()
    # B_label.show()
    # C_label.show()
    # triangle1.play(Indicate())

    screen = turtle.Screen()
    screen.update()  # 更新画面

    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'draw_triangle.ps')
    png_path = os.path.join(IMG_DIR, 'draw_triangle.png')
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