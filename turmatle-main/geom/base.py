import turtle
import math

class Geom:
    # 设置类变量作为默认值
    default_origin_x = 0
    default_origin_y = 0
    default_scale = 100
    default_speed = 0
    default_pensize = 5
    
    # 自动收集所有实例
    _instances = []

    @classmethod
    def set_defaults(cls, origin_x=0, origin_y=0, scale=100, speed = 0, pensize = 5):
        cls.default_origin_x = origin_x
        cls.default_origin_y = origin_y
        cls.default_scale = scale
        cls.default_speed = speed
        cls.default_pensize = pensize
   
    def __init__(
        self,
        origin_x: float = None,
        origin_y: float = None,
        scale: float = None,
        speed: float = None,
        pensize: float = None,
    ) -> None:    
        self.origin_x = self.default_origin_x if origin_x is None else origin_x
        self.origin_y = self.default_origin_y if origin_y is None else origin_y
        self.scale = self.default_scale if scale is None else scale
        self.speed = self.default_speed if speed is None else speed
        self.pensize = self.default_pensize if pensize is None else pensize
        # 自动注册实例
        Geom._instances.append(self)

    @classmethod
    def show_all(cls):
        for obj in cls._instances:
            if hasattr(obj, 'show'):
                obj.show()


class Point(Geom):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

    def get_screen_coords(self):
        screen_x = (self.x + self.origin_x) * self.scale
        screen_y = (self.y + self.origin_y) * self.scale
        return screen_x, screen_y

    def __repr__(self):
        return f'Point({self.x}, {self.y})' 