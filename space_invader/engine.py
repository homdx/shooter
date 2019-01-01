# from enum import IntEnum
from random import randint, uniform
from time import time

from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import (
    ListProperty,
    StringProperty,
    NumericProperty,
    BooleanProperty,
    ObjectProperty,
    DictProperty,
)

from enemies import EnemyShip
from playership import PlayerShip
from bullets import EnemyBullet, PlayerBullet


# class GameState(IntEnum):
#     START = 0
#     PAUSE = 1
#     PLAY = 2
#     OPTIONS = 3


class ActorsContainer(FloatLayout):
    player = ObjectProperty(None, allownone=True)

    game_start_time = NumericProperty(0)
    pbullets = ListProperty()
    ebullets = ListProperty()
    enemies = ListProperty()
    debris = ListProperty()
    player_lives = NumericProperty(0)
    score = NumericProperty(0)

    options = DictProperty({"start_lives": 1})

    def clear_widgets(self, children=None):
        super(ActorsContainer, self).clear_widgets(children=children)
        if children is None:
            self.pbullets.clear()
            self.ebullets.clear()
            self.enemies.clear()
        else:
            for child in children:
                if child in self.pbullets:
                    self.pbullets.remove(child)

    def on_player_lives(self, instance, value):
        if value == 0:
            self.remove_player()

            info = Label(text="You died!", font_size=50, bold=True)
            self.add_widget(info)

    def init_game(self):
        if self.player_lives == 0:
            self.game_start_time = time()
            self.player_lives = self.options["start_lives"]
            self.score = 0
            self.game_start_time = time()
            self.clear_widgets()
            self.add_player(x=self.width / 2, y=30)

    def update_game(self, dt):
        # print(len(self.enemies), len(self.pbullets), len(self.ebullets))
        for child in self.children:
            if hasattr(
                child, "update"
            ):  # TODO as actor inherit from the same class? better use Animation
                child.update()

        for bullet in self.pbullets:
            for enemy in self.enemies:
                if bullet.check_collision(enemy):
                    self.score += 10

        for bullet in self.ebullets:
            bullet.check_collision(self.player)

        for enemy in self.enemies:
            enemy.check_collision(self.player)

        if len(self.enemies) < int((time() - self.game_start_time) / 10) + 1:
            self.add_enemy(
                x=randint(0, self.width),
                y=self.height + 50,
                velocity_y=uniform(-2, -1),
                velocity_x=uniform(-2, 2),
            )

    def add_enemy(self, **kwargs):
        kwargs["space_game"] = self
        enemy = EnemyShip(**kwargs)
        self.enemies.append(enemy)
        self.add_widget(enemy)

    def remove_enemy(self, enemy):
        self.enemies.remove(enemy)
        self.remove_widget(enemy)

    def add_enemy_bullet(self, **kwargs):
        kwargs["space_game"] = self
        bullet = EnemyBullet(**kwargs)
        self.ebullets.append(bullet)
        self.add_widget(bullet)

    def remove_enemy_bullet(self, bullet):
        self.ebullets.remove(bullet)
        self.remove_widget(bullet)

    def add_player(self, **kwargs):
        kwargs["space_game"] = self
        self.player = PlayerShip(**kwargs)
        self.add_widget(self.player)

    def remove_player(self):
        if self.player is not None:
            self.remove_widget(self.player)

    def add_player_bullet(self, **kwargs):
        kwargs["space_game"] = self
        bullet = PlayerBullet(**kwargs)
        self.pbullets.append(bullet)
        self.add_widget(bullet)

    def remove_player_bullet(self, bullet):
        self.pbullets.remove(bullet)
        self.remove_widget(bullet)


class SpaceGame(Screen):
    container = ObjectProperty(None)
    menu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpaceGame, self).__init__(**kwargs)
        self._update_event = None

    def on_pre_enter(self, *args):
        self.container.init_game()
        self._update_event = Clock.schedule_interval(
            self.container.update_game, 1.0 / 60.0
        )
        super(SpaceGame, self).on_pre_enter(*args)

    def on_pre_leave(self, *args):
        self._update_event.cancel()
        self.menu.but_launch.text = "Survival Mode"
        if self.container.player_lives > 0:
            self.menu.but_launch.text = "Resume"
        super(SpaceGame, self).on_pre_leave(*args)


class ShooterGame(ScreenManager):
    start_lives = NumericProperty(1)

    def __init__(self, **kwargs):
        kwargs["transition"] = FadeTransition()
        super(ShooterGame, self).__init__(**kwargs)
        self.bg_music = None  # SoundLoader.load('music.ogg')
        if self.bg_music:
            self.bg_music.play()
            self.bg_music.loop = True
