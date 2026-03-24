from geom.base import Geom, Point
import turtle
import math

class Line(Geom):
    def __init__(
        self,
        start: Point,
        end: Point,
        color: str = "black",
    ) -> None:
        super().__init__()
        self.start = start
        self.end = end
        self.color = color
        #创建turtle用于画线
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.speed(self.speed)
        self.turtle.pensize(self.pensize)
        self.turtle.color(self.color)

    def show(self):
        # 获取屏幕对象
        screen = self.turtle.getscreen()
        # 关闭动画，立即显示
        screen.tracer(0)

        # 获取屏幕坐标
        x1, y1 = self.start.get_screen_coords()
        x2, y2 = self.end.get_screen_coords()

        # 画
        self.turtle.penup()
        self.turtle.goto(x1, y1)
        self.turtle.pendown()
        self.turtle.goto(x2, y2)
        self.turtle.penup()

        # 更新
        screen.update()


class Rect(Geom):
    def __init__(
        self,
        bottom_left: Point,  # 左下顶点
        top_right: Point,    # 右上顶点
        color = "black",
    ):
        super().__init__()
        self.bottom_left = bottom_left
        self.top_right = top_right
        self.color = color
        # 创建turtle用于画线
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.pensize(self.pensize)
        self.turtle.speed(self.speed)
        self.turtle.color(self.color)

    def show(self):
        # 获取屏幕对象
        screen = self.turtle.getscreen()
        # 关闭动画，立即显示
        screen.tracer(0)

        # 获取四个顶点的屏幕坐标
        bl_x, bl_y = self.bottom_left.get_screen_coords()
        tr_x, tr_y = self.top_right.get_screen_coords()
        br_x, br_y = Point(self.top_right.x, self.bottom_left.y).get_screen_coords()
        tl_x, tl_y = Point(self.bottom_left.x, self.top_right.y).get_screen_coords()
        
        # 画矩形边框
        self.turtle.penup()
        self.turtle.goto(bl_x, bl_y)
        self.turtle.pendown()
        self.turtle.goto(tl_x, tl_y)
        self.turtle.goto(tr_x, tr_y)
        self.turtle.goto(br_x, br_y)
        self.turtle.goto(bl_x, bl_y)
        self.turtle.penup()
        
        # 更新
        screen.update()

class Circle(Geom):
    def __init__(
        self, 
        center: Point, 
        radius: float, 
        color = "black", 
 ):
        super().__init__()
        self.center = center
        self.radius = radius
        self.color = color
        # 创建turtle用于画线
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.pensize(self.pensize)
        self.turtle.speed(self.speed)
        self.turtle.color(self.color)

    def show(self):
        # 获取屏幕对象
        screen = self.turtle.getscreen()
        # 关闭动画，立即显示
        screen.tracer(0)

        # 获取圆心屏幕坐标
        center_x, center_y = self.center.get_screen_coords()
        # 计算屏幕坐标系统中的半径
        screen_radius = self.radius * self.scale
        # 移动到圆的起始位置（圆心正下方）
        start_x, start_y = center_x, center_y - screen_radius

        # 画圆
        self.turtle.penup()
        self.turtle.goto(start_x, start_y)
        self.turtle.pendown()
        self.turtle.circle(screen_radius)
        self.turtle.penup()

        # 更新
        screen.update()

class Triangle(Geom):
    def __init__(
        self,
        p1 : Point,
        p2 : Point,
        p3 : Point,
        color = "black", 
):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.color = color
        # 创建turtle用于画线
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.pensize(self.pensize)
        self.turtle.speed(self.speed)
        self.turtle.color(self.color)


    def show(self):
        # 获取屏幕对象
        screen = self.turtle.getscreen()
        # 关闭动画，立即显示
        screen.tracer(0)

        # 获取三个顶点的屏幕坐标
        p1_x, p1_y = self.p1.get_screen_coords()
        p2_x, p2_y = self.p2.get_screen_coords()
        p3_x, p3_y = self.p3.get_screen_coords()

        # 画三角形边框
        self.turtle.penup()
        self.turtle.goto(p1_x, p1_y)
        self.turtle.pendown()
        self.turtle.goto(p2_x, p2_y)
        self.turtle.goto(p3_x, p3_y)
        self.turtle.goto(p1_x, p1_y)
        self.turtle.penup()

        # 更新 
        screen.update()

# class Ellipse(Geom):
#     def __init__(
#         self,
#         center: Point,      # 椭圆中心
#         a: float,           # 长轴半径
#         b: float,           # 短轴半径
#         angle: float = 0,   # 椭圆旋转角度（弧度）
#         steps: float = 120,  # 椭圆点数，越大越平滑
#         color = "black",
#     ):
#         super().__init__()
#         self.center = center
#         self.a = a
#         self.b = b
#         self.angle = angle
#         self.steps = steps
#         self.color = color

#         # 创建turtle用于画线
#         self.turtle = turtle.Turtle()
#         self.turtle.hideturtle()
#         self.turtle.pensize(self.pensize)
#         self.turtle.speed(self.speed)
#         self.turtle.color(self.color)

#     def show(self):
#         # 获取屏幕对象
#         screen = self.turtle.getscreen()
#         # 关闭动画，立即显示
#         screen.tracer(0)

#         # 获取椭圆点坐标
#         points = []
#         for i in range(self.steps + 1):
#             theta = 2 * math.pi * i / self.steps
#             x = self.a * math.cos(theta)
#             y = self.b * math.sin(theta)
#             x_rot = x * math.cos(self.angle) - y * math.sin(self.angle)
#             y_rot = x * math.sin(self.angle) + y * math.cos(self.angle)
#             px = self.center.x + x_rot
#             py = self.center.y + y_rot
#             screen_x, screen_y = Point(px, py).get_screen_coords()
#             points.append((screen_x, screen_y))

#         # 画
#         self.turtle.penup()
#         if points:
#             self.turtle.goto(points[0][0], points[0][1])
#             self.turtle.pendown()
#             for x, y in points[1:]:
#                 self.turtle.goto(x, y)
#             self.turtle.goto(points[0][0], points[0][1])
#             self.turtle.penup()

#         screen.update()

