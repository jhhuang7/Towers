#Importing tkinter so the game can actually function
import tkinter as tk
from tkinter import messagebox, Toplevel

#Importing code from support files so that this main file isn't too long
from model import TowerGame
from tower import SimpleTower, MissileTower, EnergyTower, FireTower
from enemy import SimpleEnemy, InvincibleEnemy, AdvancedEnemy
from utilities import Stepper
from view import GameView
from level import AbstractLevel, MyLevel
from high_score_manager import HighScoreManager, HighScoreFrame, HighScoreEnter
from frames import StatusBar, ShopTowerView, TowerPopUp 

import logging
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format = FORMAT)
logger = logging.getLogger('towerlogger')
logger.setLevel(logging.DEBUG)

BACKGROUND_COLOUR = "#4a2f48"

__author__ = "Juhua Huang (45309151)"
__copyright__ = "The University of Queensland"

class TowerGameApp(Stepper):
    """Top-level GUI application for a simple tower defence game"""

    #All private attributes for ease of reading
    _current_tower = None
    _paused = False
    _won = None
    _level = None
    _wave = None
    _score = None
    _coins = None
    _lives = None
    _master = None
    _game = None
    _view = None

    def __init__(self, master: tk.Tk, delay: int = 20):
        """
        Construct a tower defence game in a root window

        Parameters:
            master (tk.Tk): Window to place the game into
        """

        #Initiating the basics of the GUI
        self._master = master
        master.title("Towers")
        master.maxsize(700, 400)
        master.minsize(700, 400)
        super().__init__(master, delay = delay)
        self._game = game = TowerGame()
        self.setup_menu()

        #Create a game view and draw grid borders to pack into a game frame
        self._game_frame = tk.Frame(master, bg = "black")
        self._game_frame.pack(side = tk.LEFT, anchor = tk.NW,
                              expand = True, fill = tk.BOTH)
        
        self._view = view = GameView(self._game_frame, size = game.grid.cells,
                                     cell_size = game.grid.cell_size,
                                     bg ="light yellow")
        view.pack(side = tk.LEFT, expand = True)

        #Bind game events
        game.on("enemy_death", self._handle_death)
        game.on("enemy_escape", self._handle_escape)
        game.on("cleared", self._handle_wave_clear)

        #1.2 Bind mouse events to canvas
        view.bind("<Motion>", self._move)
        view.bind("<Leave>", self._mouse_leave)
        view.bind("<Button-1>", self._left_click)
        view.bind("<Button-3>", self._right_click)

        #Create Right Frame for all the stuff next to GameView
        self._right_frame = tk.Frame(master, bg = "light blue")
        self._right_frame.pack(side = tk.RIGHT, anchor = tk.NE,
                         expand = True, fill = tk.BOTH)
        
        #1.3 Status Bar
        self._up_frame = tk.Frame(self._right_frame, bg = "pink")
        self._up_frame.pack(side = tk.TOP, expand = False, fill = tk.BOTH)

        self._down_frame = tk.Frame(self._right_frame, bg = "pink")
        self._down_frame.pack(side = tk.TOP, expand = False, fill = tk.BOTH)

        self._lives_img = tk.PhotoImage(file = "images/heart.gif")
        self._lives_image = tk.Button(self._down_frame,
                                      image = self._lives_img,
                                     bg = "pink", command = self.buy_lives)
        self._lives_image.bind("<Motion>", lambda event, :
            self.toggle_callback(event, self._lives_image, "violet"))
        self._lives_image.bind("<Leave>", lambda event, :
            self.toggle_callback(event, self._lives_image, "pink"))
        
        self._status = StatusBar(self._up_frame, self._down_frame,
                                 self._lives_image, "images/coins.gif")
        self._status.pack(side=tk.TOP, anchor = tk.N,
                          expand = True, fill = tk.BOTH)

        #1.5 Play Controls
        self._controls_frame = tk.Frame(self._right_frame, bg = "light green")
        self._controls_frame.pack(side = tk.BOTTOM, fill = tk.BOTH,
                                  anchor = tk.S)

        self._button_frame = tk.Frame(self._controls_frame, bg = "black")
        self._button_frame.pack(side = tk.BOTTOM, anchor = tk.S, expand = True)
        
        self._next_wave_button = tk.Button(self._button_frame, bg = "white",
                                           text = "Next Wave",
                                           command = self.next_wave)
        self._next_wave_button.pack(side = tk.LEFT, expand = True)
        self._next_wave_button.bind("<Motion>", lambda event, :
            self.toggle_callback(event, self._next_wave_button, "grey"))
        self._next_wave_button.bind("<Leave>", lambda event, :
            self.toggle_callback(event, self._next_wave_button, "white"))

        self._play_button = tk.Button(self._button_frame, bg = "white",
                                text = "Play", command = self._toggle_paused)
        self._play_button.pack(side = tk.RIGHT, expand = True)
        self._play_button.bind("<Enter>", lambda event, :
            self.toggle_callback(event, self._play_button, "grey"))
        self._play_button.bind("<Leave>", lambda event, :
            self.toggle_callback(event, self._play_button, "white"))

        #Shop Frame (2.3)
        towers = [SimpleTower, MissileTower, EnergyTower, FireTower]

        self._shop_frame = tk.Frame(self._right_frame, bg = "light blue")
        self._shop_frame.pack(fill = tk.BOTH)

        #Create views for each tower & store to update if availability changes
        self._tower_views = []
        
        for tower_class in towers:
            tower = tower_class(self._game.grid.cell_size // 2)

            self._shop_view = ShopTowerView(self._shop_frame, tower,
                         click_command = lambda event, class_ =
                                 tower_class: self.select_tower(class_))
            self._shop_view.pack(expand = True, fill = tk.BOTH)
            
            #Can use to check if tower is affordable when refreshing view
            self._tower_views.append((tower, self._shop_view))

        #Getting ready for the game
        self.game_over_restart()

    def toggle_callback(self, event, button, colour):
        """Changes colour of button during hover and leave."""

        button.config(bg = colour)
    
    def buy_lives(self):
        """Shows pop-up allowing user to buy more lives"""

        if (messagebox.askyesno("Buy lives",
                                "Do you want to buy 5 lives for 30 coins?"))\
                                == True:
            if self._coins > 30:
                self._coins -= 30
                self._lives += 5
                self._status.set_lives(self._lives)
            else:
                messagebox.showinfo("", "You don't have enough coins.")

    def setup_menu(self):
        """Makes a file menu with new game, exit, high scores."""
        
        #Task 1.4: construct file menu
        menubar = tk.Menu(self._master)
        self._master.config(menu = menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label = "File", menu = filemenu)
        filemenu.add_command(label = "New Game", command = self._new_game)
        filemenu.add_command(label = "Exit", command = self._exit)
        filemenu.add_command(label = "High Scores",
                             command = self.high_score_open)
        
    def _toggle_paused(self, paused = None):
        """Toggles or sets the paused state

        Parameters:
            paused (bool): Toggles/pauses/unpauses if None/True/False,
            respectively
        """

        #Task 1.5 (Play Controls): Reconfigure the pause button
        if paused is None:
            paused = not self._paused

        if paused:
            self.pause()
            self._play_button.config(text = "Play")
            
        else:
            self.start()
            self._play_button.config(text = "Pause")
            
        self._paused = paused

    def _initial_tower_placement(self):
        """Places towers at the start of the game."""

        #Task 1.2 (Initial Tower Placement)
        towers = [([(2, 2),(4, 2)], SimpleTower),
                  ([(2, 5)], MissileTower), ([(5,0)], EnergyTower)]

        for positions, tower in towers:
            for position in positions:
                self._game.place(position, tower_type = tower)
    
    def _setup_game(self):
        """Sets up the game at the start."""
        
        self._wave = 0
        self._score = 0
        self._coins = 50
        self._lives = 20
        self._won = False

        #Task 1.3 (Status Bar): Update status
        self._status.set_score(self._score)
        self._status.set_wave(self._wave)
        self._status.set_coins(self._coins)
        self._status.set_lives(self._lives)

        #Task 1.5 (Play Controls): Re-enable the play controls 
            #if they were ever disabled
        if self._paused == True:
            self._paused = False

        self._game.reset()

        self._toggle_paused(paused = True)

        self.can_afford()

    def can_afford(self):
        """Checks whether user can afford tower and config labels accordingly"""

        for item in self._tower_views:
            if self._coins < item[0].get_value():
                item[1].set_available(False)
            else:
                item[1].set_available(True)
    
    def _new_game(self):
        """Restarts the game"""
        
        if (messagebox.askyesno("New Game",
                                "Do you want to restart the game?")) == True:
            self.game_over_restart()
        
    def _exit(self):
        """Close the application."""

        if (messagebox.askyesno("Exit", "Do you want to exit?")) == True:
            self._master.destroy()

    def refresh_view(self):
        """Refreshes the game view"""
        
        if self._step_number % 2 == 0:
            self._view.draw_enemies(self._game.enemies)
        self._view.draw_towers(self._game.towers)
        self._view.draw_obstacles(self._game.obstacles)

    def _step(self):
        """
        Perform a step every interval

        Triggers a game step and updates the view

        Returns:
            (bool) True if the game is still running
        """
        
        self._game.step()
        self.refresh_view()

        return not self._won

    #Task 1.2 (Tower Placement): Complete event handlers:
        #_move, _mouse_leave, _left_click
    def _move(self, event):
        """
        Handles the mouse moving over the game view canvas

        Parameter:
            event (tk.Event): Tkinter mouse event
        """
        
        if self._current_tower.get_value() > self._coins:
            return

        #Move the shadow tower to mouse position
        position = event.x, event.y
        self._current_tower.position = position

        legal, grid_path = self._game.attempt_placement(position)

        #Find the best path and covert positions to pixel positions
        path = [self._game.grid.cell_to_pixel_centre(position)
                for position in grid_path.get_shortest()]

        #Task 1.2 (Tower placement): Draw the tower preview
        self._view.draw_preview(self._current_tower, legal = legal)
        self._view.draw_path(path)

        logger.info("Previewing Tower Placement")

    def _mouse_leave(self, event):
        """
        Deletes the previewed tower when mouse leaves the hovered grid
        and left clicked is not clicked.
        """
        
        #Task 1.2 (Tower placement): Delete the preview
            #Delete all canvas items are tagged with:
                #"path", "range", "shadow"

        self._view.delete("shadow", "range", "path")

        logger.info("Preview Stopped")

    def _left_click(self, event):
        """
        Handles drawing a tower onto a certain grid after it is clicked.
        """
        
        #Retrieve position to place tower
        if self._current_tower is None or \
           self._current_tower.get_value() > self._coins:
            return

        position = event.x, event.y
        cell_position = self._game.grid.pixel_to_cell(position)
        
        if self._game.place(cell_position,
                            tower_type = self._current_tower.__class__):
            #Task 1.2 (Tower placement): Attempt to place the tower previewed
            self._game.place(cell_position, self._current_tower)
            self._coins -= self._current_tower.base_cost
            logger.info("Tower has been placed")

    #2.2 Sell Towers
    def sell(self):
        """Sells the tower being clicked on."""

        self._coins += self._game.towers[self._cell_position].level_cost
        self._game.remove(self._cell_position)
        self._pop_up.destroy()

    #3.3 Upgrade Tower    
    def tower_upgrade(self, tower):
        selected_tower = self._game.towers[self._cell_position]
        if selected_tower.name != tower.name:
            cost = tower.base_cost - selected_tower.base_cost
            if cost <= self._coins:
                self._game.remove(self._cell_position)
                self._game.place(self._cell_position, tower)
                self._coins -= cost
                logger.info('cost=%d, coins_remaining=%d', cost, self._coins)
            else:
                messagebox.showinfo("Warning", "Insufficient funds")
            self._pop_up.destroy()
        else:
            messagebox.showerror("Error", "Cannot upgrade to same tower")
    
    def _right_click(self, event):
        """
        A feature that allows the player to sell a tower by right clicking.
        The tower should be removed from the grid and 80% of its value should
        be put back into the player's wallet.
        Further to , if the player cannot afford the currently selected tower,
        do not allow them to place it. Otherwise, after placing a tower
        successfully, deduct the value of the tower from the player's wallet.
        """

        position = event.x, event.y
        self._cell_position = self._game.grid.pixel_to_cell(position)
        
        #2.2 Sell Towers; 3.3 Upgrade Tower
        
        if not self._game.grid.is_cell_valid(self._cell_position) or \
        self._cell_position not in self._game.towers:
            messagebox.showerror("Error", "No tower selected.")
        else:
            self._sell_upgrade_window = Toplevel(self._master)
            self._pop_up = TowerPopUp(self._sell_upgrade_window, self, self.sell,
                                      self.tower_upgrade)
            self.can_afford()
        
        logger.info("Tower Options")

    def next_wave(self):
        """Sends the next wave of enemies against the player"""
        
        if self._wave == self._level.get_max_wave():
            return

        self._wave += 1

        #Task 1.3 (Status Bar): Update the current wave display here
        self._status.set_wave(self._wave)

        #Task 1.5 (Play Controls): Disable the add wave button if last wave
        if self._wave == 20:
            self._next_wave_button.config(command = None)
            self._next_wave_button.config(bg = "grey")

        #Generate wave and enqueue
        wave = self._level.get_wave(self._wave)
        for step, enemy in wave:
            enemy.set_cell_size(self._game.grid.cell_size)

        self._game.queue_wave(wave)

        logger.info("Next wave")

    def select_tower(self, tower):
        """
        Set "tower" as the current tower

        Parameters:
            tower (AbstractTower): The new tower type
        """
        
        self._current_tower = tower(self._game.grid.cell_size)

    def _handle_death(self, enemies):
        """
        Handles enemies dying

        Parameters:
            enemies (list<AbstractEnemy>): The enemies which died in a step
        """
        
        bonus = len(enemies) ** 0.5
        for enemy in enemies:
            self._coins += enemy.points
            self._score += int(enemy.points * bonus)

        #Task 1.3 (Status Bar): Update coins & score displays
        self._status.set_coins(self._coins)
        self._status.set_score(self._score)

        self.can_afford()

    def _handle_escape(self, enemies):
        """
        Handles enemies escaping (not being killed before moving through
        the grid

        Parameters:
            enemies (list<AbstractEnemy>): The enemies which escaped in a step
        """
        
        self._lives -= len(enemies)

        #3.2 Advanced enemy damage (if they don't kill it, they lose)!
        if enemies[0].name == "Advanced Enemy":
            self._lives -= 50
        
        if self._lives < 0:
            self._lives = 0

        #Task 1.3 (Status Bar): Update lives display
        self._status.set_lives(self._lives)

        #Handle game over
        if self._lives == 0:
            messagebox.showinfo("Loser", "You have lost!")
            self.enter_high_score()
            self._handle_game_over(won = False)

    def _handle_wave_clear(self):
        """Handles an entire wave being cleared (all enemies killed)"""
        
        if self._wave == self._level.get_max_wave() and \
           self._lives > 0:
            self._handle_game_over(won = True)

        #Task 1.5 (Play Controls)
        self.next_wave()

    def _handle_game_over(self, won = False):
        """Handles game over
        
        Parameter:
            won (bool): If True, signals the game was won (otherwise lost)
        """
        
        self._won = won
        self.stop()

        #Task 1.4 (Dialogs): show game over dialog
        if self._won == True:
            messagebox.showinfo("Winner", "You have won!")
            self.enter_high_score()
            
    def game_over_restart(self):
        """Restarts the game when a player has won or lost and at the start."""
        
        self._level = MyLevel()
        self.select_tower(SimpleTower)
        self._view.delete(tk.ALL)
        self._view.draw_borders(self._game.grid.get_border_coordinates())
        self._setup_game()
        self._initial_tower_placement()

    def high_score_open(self):
        """Opens a pop-up showing high-scores."""

        #2.4 Display High Scores
        self._high_score_window = Toplevel(self._master)
        self._pop_up = HighScoreFrame(self._high_score_window, self)

    def enter_high_score(self):
        """Opens a pop-up showing high-scores."""

        #2.4 Ask to enter High Scores
        self._final_score = self._score + self._coins + \
                            (self._wave * self._lives)
        
        self._high_score_pop = Toplevel(self._master)
        self._pop_up = HighScoreEnter(self._high_score_pop, self,
                                      self._final_score, self.game_over_restart)

#A main function that launches the GUI (1.1)
if __name__ == "__main__" :
    root = tk.Tk()
    app = TowerGameApp(root)
    root.mainloop()
