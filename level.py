"""Contains abstract level for generating waves and relevant utilities functions"""

__author__ = "Benjamin Martin and Brae Webb"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.1.0"

from enemy import SimpleEnemy, InvincibleEnemy, AdvancedEnemy
from view import GameView
import tkinter as tk
from tkinter import messagebox


class AbstractLevel:
    """A level in the game, with multiple waves of enemies"""
    EASY = 0
    NORMAL = 1
    HARD = 2

    waves = None

    def __init__(self, difficulty=NORMAL):
        self.difficulty = difficulty

    def get_wave(self, wave_n):
        """Returns enemies in the 'wave_n'th wave

        Parameters:
            wave_n (int): The nth wave

        Return:
            list[tuple[int, AbstractEnemy]]: A list of (step, enemy) pairs in the
                                             wave, sorted by step in ascending order 
        """
        raise NotImplementedError("get_wave must be implemented by a subclass")

    def get_max_wave(self):
        """(int) Returns the total number of waves"""
        return self.waves

    @staticmethod
    def generate_intervals(total, intervals):
        """Divides a total into even intervals
    
        Loosely equivalent to range(0, total, total/intervals), where each yield is an integer
    
        Parameters:
            total (float|int): The total to be divided into intervals
            intervals (int): The number of intervals
    
        Yield:
            int: Each interval
        """
        interval_step = total / intervals

        for i in range(intervals):
            yield int(interval_step * i)

    @classmethod
    def generate_sub_wave(cls, steps, count, enemy_class, args=None, kwargs=None, offset=0):
        """Generates a sub-wave compatible with TowerGame.queue_wave
        
        Parameters:
            steps (int): The number of steps over which to spawn this sub-wave
            count (int): The number of enemies to distribute
            enemy_class (Class<AbstractEnemy>): The enemy constructor
            args: Positional arguments to pass to the enemy's constructor
            kwargs: Keyword arguments to pass to the enemy's constructor
            offset (int): The first step (i.e. positive offset for each step)
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        for step in cls.generate_intervals(steps, count):
            yield step + offset, enemy_class(*args, **kwargs)

    @classmethod
    def generate_sub_waves(cls, sub_waves):
        """Generates successive sub-waves compatible with TowerGame.queue_wave
        
        Parameters:
            sub_waves: list of (steps, count, enemy_class, args, kwargs) tuples, where
                       parameters align with AbstractLevel.generate_sub_wave
        """
        enemies = []
        offset = 0
        for steps, count, enemy_class, args, kwargs in sub_waves:
            if count is not None:
                enemies.extend(cls.generate_sub_wave(steps, count, enemy_class,
                                                     args=args, kwargs=kwargs, offset=offset))

            offset += steps

        return enemies

class MyLevel(AbstractLevel):
    """A simple game level containing examples of how to generate a wave"""
    waves = 20

    
    def get_wave(self, wave):
        """Returns enemies in the 'wave_n'th wave

        Parameters:
            wave_n (int): The nth wave

        Return:
            list[tuple[int, AbstractEnemy]]: A list of (step, enemy) pairs in the
                                             wave, sorted by step in ascending order 
        """
        enemies = []

        if wave == 1:
            # A hardcoded singleton list of (step, enemy) pairs

            enemies = [(10, SimpleEnemy())]
        elif wave == 2:
            # A hardcoded list of multiple (step, enemy) pairs

            enemies = [(10, SimpleEnemy()), (15, SimpleEnemy()), (30, SimpleEnemy())]
        elif 3 <= wave < 10:
            # List of (step, enemy) pairs spread across an interval of time (steps)

            steps = int(40 * (wave ** .5))  # The number of steps to spread the enemies across
            count = wave * 2  # The number of enemies to spread across the (time) steps

            for step in self.generate_intervals(steps, count):
                enemies.append((step, SimpleEnemy()))

        elif wave == 10:
            # Generate sub waves
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (50, 10, SimpleEnemy, (), {}),  # 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 10, SimpleEnemy, (), {})  # then another 10 enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)

        elif 11 <= wave < 15:
            # Now it's going to get hectic

            sub_waves = [
                (
                    int(10 * wave),  # total steps
                    int(20 * wave * (wave / 40)),  # number of enemies
                    SimpleEnemy,  # enemy constructor
                    (),  # positional arguments to provide to enemy constructor
                    {},  # keyword arguments to provide to enemy constructor
                ),
                # ...
            ]
            enemies = self.generate_sub_waves(sub_waves)
            
        elif 15 <= wave <= 19:
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (100, 15, SimpleEnemy, (), {}),  # 15 enemies over 100 steps
                (50, None, None, None, None),  # then nothing for 50 steps
                (50, 15, InvincibleEnemy, (), {})  # then another 15
                                        #invincible enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)

        else: #20th wave
            # This is gonna be impossible
            
            enemies = [(20, SimpleEnemy()), (30, InvincibleEnemy()),
                       (50, AdvancedEnemy())]

            #3.2 Advanced Enemy Message
            messagebox.showinfo("Quick!", "Kill Advanced Enemy before it kills you!")
            

        return enemies
