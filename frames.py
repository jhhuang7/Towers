import tkinter as tk
from tkinter import messagebox, Toplevel
from tower import SimpleTower, MissileTower, EnergyTower, FireTower
from view import GameView
from advanced_view import TowerView
import math

class StatusBar(tk.Frame):
    """
    Used to display information to the user about their status in the game.
    """

    def __init__(self, top_frame, bottom_frame, lives_image, coin_img):
        """Initialise the widget, with its subwidgets."""
        
        super().__init__(top_frame, bg = "pink")

        self._wave_label = tk.Label(top_frame, text = "Wave:", bg = "pink")
        self._wave_label.pack(side = tk.TOP, anchor = tk.CENTER)

        self._score_label = tk.Label(top_frame, text = "Score:", bg = "pink")
        self._score_label.pack(side = tk.TOP, anchor = tk.CENTER)
        
        self._coin_img = tk.PhotoImage(file = coin_img)
        self._gold_image = tk.Label(bottom_frame, image = self._coin_img,
                                    bg = "pink")
        self._gold_image.pack(side = tk.LEFT)

        self._gold_label = tk.Label(bottom_frame, text = "Gold:",
                                    bg = "pink")
        self._gold_label.pack(side = tk.LEFT)

        self._lives_label = tk.Label(bottom_frame, text = "Lives:",
                                     bg = "pink")
        self._lives_label.pack(side = tk.RIGHT)

        self.lives_image = lives_image
        self.lives_image.pack(side = tk.RIGHT)

    def set_score(self, score):
        """Updates the score label with the player's current score (int)."""

        self._score_label.config(text = "Score: {}".format(score))

    def set_wave(self, wave):
        """Updates the wave label with the game's current wave (int)."""

        self._wave_label.config(text = "Wave: {} of 20".format(wave))

    def set_coins(self, coins):
        """Updates the wave label with the player's current coins (int)."""

        self._gold_label.config(text = "Gold: {}".format(coins))

    def set_lives(self, lives):
        """Updates the wave label with the player's current lives (int)."""

        self._lives_label.config(text = "Lives: {}".format(lives))

class ShopTowerView(tk.Frame):
    """
    The shop allows the user to select other types of towers to use against
    the enemies. If the player cannot afford the currently selected tower,
    do not allow them to place it. Otherwise, after placing a tower
    successfully, deduct the value of the tower from the player's wallet.
    Allows the player to sell a tower by right clicking on it.
    The tower should be removed from the grid and 80% of its value
    should be put back into the player's wallet.
    """

    def __init__(self, master, tower, click_command):
        """
        master: The Tkinter parent widget
        tower: The tower to display (an instance of AbstractTower)
        click_command: A callback function to be called when the tower
        is clicked.
        *args & **kwargs: Positional & keyword arguments to be passed
        to the tk.Frame constructor
        """

        super().__init__(master, bg = "light blue")

        self._master = master
        
        self._tower = tower

        self._click_command = click_command

        self._shop_frame = tk.Frame(self, bg = "light blue")
        self._shop_frame.pack(side = tk.TOP, expand = True, fill = tk.BOTH)
        self._shop_frame.bind("<Button-1>", self._click_command)
        self._shop_frame.bind("<Motion>", self.hover)
        self._shop_frame.bind("<Leave>", self.leave)
        
        self._image_canvas = tk.Canvas(self._shop_frame, height=30, width = 30,
                                       bg = "light blue", 
                                       highlightthickness=0)
        self._tower.position = (self._tower.cell_size // 2,
                                    self._tower.cell_size // 2) #In centre
        self._tower.rotation = 3 * math.pi / 2 #Point up
        TowerView.draw(self._image_canvas, self._tower)
        self._image_canvas.pack(side = tk.LEFT, anchor = tk.W, fill = tk.X)
        self._image_canvas.bind("<Button-1>", self._click_command)
        self._image_canvas.bind("<Motion>", self.hover)
        self._image_canvas.bind("<Leave>", self.leave)

        self._tower_label = tk.Label(self._shop_frame, text = self._tower.name
                                     + ": " + str(self._tower.base_cost)
                                     + " coins",
                                     bg = "light blue", fg = "black")
        self._tower_label.pack(side = tk.LEFT)
        self._tower_label.bind("<Button-1>", self._click_command)
        self._tower_label.bind("<Motion>", self.hover)
        self._tower_label.bind("<Leave>", self.leave)
        
    def set_available(self, available):
        """
        available: bool
        Updates the widget to show whether the tower is available (white text)
        or not (red text)
        """

        self._available = available
        
        if self._available is True:
            self._tower_label.config(fg = "black")
        else:
            self._tower_label.config(fg = "red")

    def hover(self, event):
        """Changes colour of shopview, when mouse is hovering."""

        self._tower_label.config(bg = "aqua")
        self._image_canvas.config(bg = "aqua")
        self._shop_frame.config(bg = "aqua")

    def leave(self, event):
        """Changes colour of shopview back, when mouse is left."""
        
        self._tower_label.config(bg = "light blue")
        self._image_canvas.config(bg = "light blue")
        self._shop_frame.config(bg = "light blue")
            
class TowerPopUp(object):
    """A pop up fram which shows the options for sell or upgrade tower."""

    def __init__(self, master, app, sell, tower_upgrade):
        
        self._master = master
        self._app = app
        self._sell = sell
        self._tower_upgrade = tower_upgrade

        self._master. title("What do you want to do?")
        self._master.maxsize(500, 500)
        self._master.minsize(500, 500)

        self._sell_frame = tk.Frame(self._master, bg = "white")
        self._sell_frame.pack(side = tk.LEFT, anchor = tk.W,
                           expand = True, fill = tk.BOTH)

        self._sell_button = tk.Button(self._sell_frame, text = "Sell Tower",
                                      bg = "white", fg = "black",
                                      command = self._sell)
        self._sell_button.pack(side = tk.LEFT, anchor = tk.W,
                                 expand = True, fill = tk.BOTH)

        self._upgrade_frame = tk.Frame(self._master, bg = "black")
        self._upgrade_frame.pack(side = tk.RIGHT, anchor = tk.E,
                           expand = True, fill = tk.BOTH)

        self._upgrade_label = tk.Label(self._upgrade_frame,
                                        text = "Upgrade to:",
                                         bg = "black", fg = "white")
        self._upgrade_label.pack(side = tk.TOP, anchor = tk.N)

        self._simple_button = tk.Button(self._upgrade_frame,
                                        text = "Simple Tower",
                                      bg = "black", fg = "orange",
                                      command = lambda: self._tower_upgrade(SimpleTower))
        self._simple_button.pack(side = tk.TOP,
                                 expand = True, fill = tk.BOTH)

        self._missile_button = tk.Button(self._upgrade_frame,
                                        text = "Missile Tower",
                                      bg = "black", fg = "white",
                                      command = lambda: self._tower_upgrade(MissileTower))
        self._missile_button.pack(side = tk.TOP,
                                 expand = True, fill = tk.BOTH)

        self._energy_button = tk.Button(self._upgrade_frame,
                                        text = "Energy Tower",
                                      bg = "black", fg = "yellow",
                                      command = lambda: self._tower_upgrade(EnergyTower))
        self._energy_button.pack(side = tk.TOP,
                                 expand = True, fill = tk.BOTH)

        self._fire_button = tk.Button(self._upgrade_frame,
                                        text = "Fire Tower",
                                      bg = "black", fg = "red",
                                      command = lambda: self._tower_upgrade(FireTower))
        self._fire_button.pack(side = tk.TOP,
                                 expand = True, fill = tk.BOTH)

    def destroy(self):
        """Destroys the pop-up after function is called."""
        
        self._master.destroy()
