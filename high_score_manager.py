"""Classes to assist in managing high scores"""

import json
import tkinter as tk
from tkinter import messagebox, Toplevel

__author__ = "Benjamin Martin"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.1.0"

DEFAULT_GAME = 'basic'


class HighScoreManager:
    """Manages high scores across multiple game types & persists to file"""
    _data = None
    _top_scores = 10  # The number of scores on each leader board

    def __init__(self, filename='high_scores.json'):
        self._filename = filename
        self.load(filename)

    def load(self, filename):
        """Loads high scores from file
        
        Parameters:
            filename (str): The filename of the file to load from
        """
        try:
            with open(filename) as file:
                self._data = json.load(file)
        except FileNotFoundError:
            self._data = {}

    def save(self, filename=None):
        """Saves highs cores to file
        
        Parameters:
            filename (str): The filename of the file to save to
                            If None, saves to the same file that was loaded
        """
        if filename is None:
            filename = self._filename

        with open(filename, 'w') as file:
            json.dump(self._data, file)

    def get_lowest_score(self, game=DEFAULT_GAME):
        """Gets lower score on the high score board
        
        Parameters:
            game (str): Unique ID for the high score board
             
        Return:
            (int): The lowest score on the board, else None if the board is empty
        """
        entries = self._data.get(game)

        if entries is None:
            return None

        return entries[-1]['score']

    def does_score_qualify(self, score, game=DEFAULT_GAME):
        """(bool) Returns True iff score qualifies to be added to high score board
        
        Existing scores win ties
        
        Parameters:
            game (str): Unique ID for the high score board
        """
        if score == 0:
            return False

        lowest = self.get_lowest_score(game=game)

        if lowest is None:
            return True

        return len(self._data.get(game)) < self._top_scores or score > lowest

    def add_entry(self, name, score, data=None, game=DEFAULT_GAME):
        """Adds an entry to the high score board
        
        Parameters:
            name (str): The player's name
            score (int): The player's score
            data (*): Extra data to store with the entry
            game (str): Unique ID for the high score board
             
        Preconditions:
            score qualifies for addition to the board
        """
        if game not in self._data:
            self._data[game] = []

        entries = self._data[game]

        entries.append({
            'name': name,
            'score': score,
            'data': data
        })

        entries.sort(key=lambda entry: int(entry['score']), reverse=True)

        if len(entries) > self._top_scores:
            return entries.pop()

        return None

    def get_entries(self, game=DEFAULT_GAME):
        """Gets all entries on high score board, sorted by ascending rank (1st, 2nd, ...)
        
        Parameters:
             game (str): Unique ID for the high score board
             
        Return:
            dict: {
                'name': The player's name,
                'score': The player's score,
                'data': Extra data stored with the entry
            }
        """
        return self._data.get(game, [])

class HighScoreFrame(object):
    """A frame displaying all the stuff relating to high scores."""

    def __init__(self, master, app):
        
        self._master = master
        self._app = app
        self._high_scores = HighScoreManager()

        self._master. title("High Scores")
        self._master.maxsize(400, 400)
        self._master.minsize(400, 400)

        self._display = tk.Frame(self._master, bg = "white")
        self._display.pack(side = tk.TOP, anchor = tk.N,
                           expand = True, fill = tk.BOTH)

        self._high_scores.load("high_scores.json")

        self._info = self._high_scores.get_entries()
        self._sorted_info = sorted(self._info,
                                   key = lambda record: int(record["score"]),
                                   reverse = True)

        for record in self._sorted_info:
            self._info_frame = tk.Frame(self._display, bg = "black")
            self._info_frame.pack(side = tk.TOP, expand = True, fill = tk.BOTH)

            self.number_label = tk.Label(self._info_frame, bg = "black",
                                         fg = "white",
                                             text =str(self._sorted_info.
                                                       index(record) + 1) + ":")
            self.number_label.pack(side = tk.LEFT, anchor = tk.W)
            
            self._name_label = tk.Label(self._info_frame, bg = "black",
                                        fg = "white",
                                                 text = record.get("name"))
            self._name_label.pack(side = tk.LEFT, padx = 5)
            
            self._score_label = tk.Label(self._info_frame, bg = "black",
                                         fg = "white",
                                            text = record.get("score"))
            self._score_label.pack(side = tk.LEFT, padx = 5)

class HighScoreEnter(object):
    """A frame displaying all the stuff relating to high scores."""

    def __init__(self, master, app, score, restart):
        
        self._master = master
        self._app = app
        self._score = score
        self._restart = restart
        self._high_scores = HighScoreManager()

        self._master. title("High Scores")
        self._master.maxsize(300, 100)
        self._master.minsize(300, 100)

        self._player_insert = tk.Frame(self._master, bg = "black")
        self._player_insert.pack(side = tk.BOTTOM, anchor = tk.S,
                                 expand = True, fill = tk.BOTH)

        self._name_frame = tk.Frame(self._master, bg = "black")
        self._name_frame.pack(side = tk.BOTTOM, fill = tk.BOTH)

        self._name_label = tk.Label(self._name_frame, bg = "black",
                                          fg = "white", text = "Name:")
        self._name_label.pack(side = tk.LEFT, anchor = tk.W)

        self._name_box = tk.StringVar()
        self._name_box.set("No name")
        self._name_box = tk.Entry(self._name_frame,
                                  textvariable = self._name_box)
        self._name_box.pack(side = tk.LEFT)

        self._enter_button = tk.Button(self._name_frame, bg = "white",
                                       fg = "black", text = "Submit",
                                       command = self.submit)
        self._enter_button.pack(side = tk.LEFT, padx = 5)
        self._enter_button.bind("<Motion>", self.submit_button_hover)
        self._enter_button.bind("<Leave>", self.submit_button_leave)

        self._score_frame = tk.Frame(self._master, bg = "black")
        self._score_frame.pack(side = tk.TOP, fill = tk.BOTH)

        self._score_label = tk.Label(self._score_frame, bg = "black",
                                          fg = "white",
                                     text = "New High Score: " +
                                     str(self._score))
        self._score_label.pack(side = tk.LEFT, anchor = tk.N)

    def submit_button_hover(self, event):
        """Changes colour of submit button, when mouse is hovering."""

        self._enter_button.config(bg = "grey")

    def submit_button_leave(self, event):
        """Changes colour of submit button back, when mouse is left."""
        
        self._enter_button.config(bg = "white")

    def submit(self):
        """Adds the high score entered and saves it."""
        
        self._high_scores.add_entry(self._name_box.get(), self._score)
        self._high_scores.save()

        messagebox.showinfo("Entered", "A new game will be started.")

        self._master.destroy()

        self._restart()
