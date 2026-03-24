from inspect import BlockFinder
import sys
import os

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 现在导入应该可以工作了
from geom import Geom, Point, Line, Function, Rect, Angle, Text
from geom.effects import Flash, Outline, Scale, Indicate
import math
import turtle
from PIL import Image

def main():
    Geom.setup_canvas(1000, 1000)   # DPI 感知 + 1000×1000 画布
    Geom.set_defaults(origin_x=0, origin_y=0, scale=120, fontsize=25)

    WIDTH, HEIGHT = 1000, 1000
    IMG_DIR = os.path.join(project_root, 'examples/images')
    os.makedirs(IMG_DIR, exist_ok=True) # 创建images目录

    angle1 = Angle(
        vertex=Point(-2, -1),       # 顶点坐标
        start_point=Point(2, -1),   # 起始点坐标，控制角边长
        angle_deg=60,              # 旋转角度
        direction=1,               # 旋转方向，逆时针1，顺时针-1
        color="blue",             # 线颜色
        pensize=5,                 # 线粗细,None默认1
        animate=True,              # 是否动画
        show_degree=True,           # 是否表示度数
        fontsize=30                # 字体大小
    )

    # # 顶点标注
    # o_label = Text(
    #     position=angle1.vertex,     # 文本位置
    #     text="O",                   # 文本内容
    #     color="red",              # 文本颜色
    #     fontsize=None,              # 字体大小，不指定即为Geom默认
    #     align="center",             # 对齐方式'left', 'center', 'right'
    #     bold=False,                 # 是否加粗
    #     italic=False,               # 是否斜体
    # )

    # angle2 = Angle(
    #     vertex=Point(-1, 0),       
    #     start_point=Point(2, 0),   
    #     angle_deg=30,              
    #     direction=-1,              
    #     color="blue",             
    #     pensize=2,                 
    #     animate=True,              
    #     show_degree=True,
    #     fontsize=30          
    # )

    # a_label = Text(
    #     position=angle2.vertex,     # 文本位置
    #     text="A",                   # 文本内容
    #     color="red",              # 文本颜色
    #     fontsize=None,              # 字体大小，不指定即为Geom默认
    #     align="center",             # 对齐方式'left', 'center', 'right'
    #     bold=False,                 # 是否加粗
    #     italic=False,               # 是否斜体
    # )

    
    angle1.show()
    # o_label.show()
    # angle2.show()
    # a_label.show()
    
    screen = turtle.Screen()
    screen.update()  # 更新画面

    # 保存图像
    ps_path = os.path.join(IMG_DIR, 'demo_angle.ps')
    png_path = os.path.join(IMG_DIR, 'demo_angle.png')
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