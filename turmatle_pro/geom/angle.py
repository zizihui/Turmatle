import turtle
import math
import time
from geom.base import Geom, Point


class Angle(Geom):

    def __init__(
        self,
        vertex: Point,
        start_point: Point,
        angle_deg: float,
        direction: int = 1,
        color="red",
        pensize=5,
        animate=True,
        step=2,
        show_degree=True,
        fontsize=None
    ):
        super().__init__()
        self.vertex = vertex
        self.start_point = start_point
        self.angle_deg = angle_deg
        self.direction = direction
        self.color = color
        self.pensize = pensize
        self.animate = animate
        self.step = step
        self.show_degree = show_degree
        self.fontsize = fontsize

        # 静态边 turtle
        self.static_turtle = turtle.Turtle()
        self.static_turtle.hideturtle()
        self.static_turtle.speed(0)
        self.static_turtle.pensize(self.pensize)

        # 动画 turtle
        self.anim_turtle = turtle.Turtle()
        self.anim_turtle.hideturtle()
        self.anim_turtle.speed(0)
        self.anim_turtle.pensize(self.pensize)

    # ================= 数学核心 =================
    def _rotate_point(self, angle_deg):
        theta = math.radians(angle_deg)
        dx = self.start_point.x - self.vertex.x
        dy = self.start_point.y - self.vertex.y

        x = self.vertex.x + dx * math.cos(theta) - dy * math.sin(theta)
        y = self.vertex.y + dx * math.sin(theta) + dy * math.cos(theta)

        return Point(x, y)

    # ================= 显示 =================
    def show(self):
        screen = self.static_turtle.getscreen()
        screen.tracer(0)

        self.clear()

        vx, vy = self.vertex.get_screen_coords()
        sx, sy = self.start_point.get_screen_coords()

        # ---- 起始边（只画一次）----
        self.static_turtle.color(self.color)
        self.static_turtle.penup()
        self.static_turtle.goto(vx, vy)
        self.static_turtle.pendown()
        self.static_turtle.goto(sx, sy)
        self.static_turtle.penup()

        # ---- 动画 ----
        angles = range(0, int(self.angle_deg) + 1, self.step)
        if not self.animate:
            angles = [self.angle_deg]

        for a in angles:
            self.anim_turtle.clear()

            end_point = self._rotate_point(self.direction * a)
            ex, ey = end_point.get_screen_coords()

            # 旋转边
            self.anim_turtle.color(self.color)
            self.anim_turtle.penup()
            self.anim_turtle.goto(vx, vy)
            self.anim_turtle.pendown()
            self.anim_turtle.goto(ex, ey)
            self.anim_turtle.penup()

            # 角度标注
            if self.show_degree:
                mx = (self.vertex.x + end_point.x) / 2
                my = (self.vertex.y + end_point.y) / 2
                tx, ty = Point(mx, my).get_screen_coords()

                self.anim_turtle.goto(tx, ty)
                self.anim_turtle.write(
                    f"{a}°",
                    font=("Arial", self.fontsize, "normal"),
                    align="left"
                )

            screen.update()

            if self.animate:
                time.sleep(0.05)

    # ================= 清除 =================
    def clear(self):
        self.static_turtle.clear()
        self.anim_turtle.clear()