import math

from kivy.animation import Animation
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
)
from kivy.uix.widget import Widget

EPS = 1e-8  # Avoid dividing by zero
MARGIN = 100  # Number of pixels outside the screen for element displacement


class Actor(Widget):
    min_y = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, **kwargs):
        super(Actor, self).__init__(**kwargs)
        self.animation = None

    def move(self):
        # Cannot be done in __init__ as the parent needs to be set
        # to start the animation (screen size needed)
        if self.parent is None:
            raise RuntimeError("Bullet needs a parent to be fired")
        vx = self.velocity_x + EPS
        vy = self.velocity_y + EPS
        width, height = self.parent.size
        d_x = math.inf
        d_y = math.inf
        if abs(self.velocity_x) > EPS:
            d_x = max((width + MARGIN - self.x) / vx, -(self.right + MARGIN) / vx)
            new_x = max(
                math.copysign(width + MARGIN, self.velocity_x),
                math.copysign(MARGIN, self.velocity_x),
            )            
        if abs(self.velocity_y) > EPS:
            d_y = max(
                (height + MARGIN - self.y) / vy, (self.min_y - self.top) / vy
            )
            new_y = max(
                math.copysign(height + MARGIN, self.velocity_y),
                math.copysign(self.min_y, - self.velocity_y),
            )

        # if type(self).__qualname__ == "EnemyShip":
        #     print("x ", new_x, d_x, self.velocity)
        #     print("y ", new_y, d_y, self.velocity)
        
        props = {}
        if d_x < d_y:
            if math.isfinite(d_y):
                props["center_y"] = self.center_y + d_x * self.velocity_y
            props["center_x"] = new_x
            props["duration"] = d_x
        else:
            if math.isfinite(d_x):
                props["center_x"] = self.center_x + d_y * self.velocity_x
            props["center_y"] = new_y
            props["duration"] = d_y

        self.animation = Animation(**props)
        if self.animation is not None:
            self.animation.bind(on_start=self.on_start)
            self.animation.bind(on_progress=self.on_progress)
            self.animation.bind(on_complete=self.on_stop)
            self.animation.start(self)

    def on_start(self, instance, value):
        pass

    def on_progress(self, instance, value, progression):
        pass

    def on_stop(self, instance, value):
        self.animation.cancel_all(self)
        if self.parent is not None:
            self.parent.remove_widget(self)


class SpaceShip:
    space_game = ObjectProperty(None)

    alive = BooleanProperty(True)

    gun_cooldown_time = 0.1
    gun_fire_interval = 2.4

    def collide_ammo(self, ammo):
        raise NotImplementedError()


class SpaceShipHive(SpaceShip):
    def __init__(self):
        self.hive = list()  # List[SpaceShip]

    def __len__(self):
        return len(self.hive)

    def collide_ammo(self, ammo):
        for ship in self.hive:
            impact = ship.collide_ammo(ammo)
            if impact:
                return True
        return False

    def clear(self):
        self.hive.clear()