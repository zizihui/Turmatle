import sys
import os

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 现在导入应该可以工作了
from geom import Geom, Point, Line, Function, Rect,Triangle,Text,Circle
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

        # 创建矩形
    rect1 = Rect(
        bottom_left=Point(-1.2, -1.2),  # 左下点坐标
        top_right=Point(2.2, 2.2),    # 右上点坐标
        pivot="center",            # 旋转中心：'center', 'bottom_left', 'bottom_right', 'top_left', 'top_right'
        rotation_deg=0,               # 旋转角度，不旋转0
        direction=-1,                 # 旋转方向：1 逆时针，-1 顺时针
        color="blue",                # 线条颜色
        pensize=5,                    # 线条粗细，None默认1
        fill_color="green",           # 填充颜色
        fill=False,                    # 是否填充
        text=None,                    # 文本内容
        text_pos=None                 # 文本位置，默认矩形右上角点，或（x，y）
    )
    
    circle1=Circle(
        center=Point(0.5,0.5),
        radius=1.7,
        color="black",
        pensize=4,                  # 线条粗细
        fill_color="lightblue",     # 填充颜色
        fill=False,                 # 是否填充
        text=None,                  # 文本内容
        text_pos=None,              # 文本位置，默认半径右侧
        show_center=True,           # 是否画圆心点
        center_label="O",           # 圆心标 O
        show_radius=False,           # 是否画半径
        radius_endpoint_label=None,  # 圆周上端点标 A（半径 OA），不标注即None
        radius_angle=None,            # 半径方向，度数
        show_tangent=False,          # 是否画切线
        tangent_angle=None,           # 切点所在角度
        tangent_length=None,        # 切线半长（数学坐标），None 表示自动
        tangent_label=None,          # 切线标注
        tangent_point_label=None     # 切点标注，如 "P"
    )

    # 显示所有元素
    rect1.show()

    circle1.show()

    # triangle1.play(Indicate())

    screen = turtle.Screen()
    screen.update()  # 更新画面

    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'rect_circle.ps')
    png_path = os.path.join(IMG_DIR, 'rect_circle.png')
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