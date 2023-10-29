import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showwarning, showerror

from src import engine
from .frames import MainFrame
from .menu import MainMenu


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Ubiquitous Dollop")
        self.geometry("1920x1080")
        self.maxsize(3840, 2160)
        self.minsize(1280, 720)
        self.resizable(True, True)

        # layout on the root window
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)


class App:
    def __init__(self):
        self.app = MainWindow()
        self._define_styles()

        self.main_menu = self.create_main_menu()

        self.tab_control = self.create_tabs()

    def start(self):
        self.app.mainloop()

    def _define_styles(self):
        style = ttk.Style(self.app)
        style.configure('southwest.TNotebook', tabposition='sw')

    def create_main_menu(self):
        main_menu = MainMenu(self.app)

        self.app.config(menu=main_menu)
        return main_menu

    def create_tabs(self):
        tabControl = ttk.Notebook(self.app, style='southwest.TNotebook')

        self.create_tab_graphical_petri(tabControl)
        self.create_tab_matricial_petri(tabControl)
        tabControl.pack(expand=1, fill="both")

    def create_tab_graphical_petri(self, tabControl: ttk.Notebook):
        grafical_tab = ttk.Frame(tabControl)

        tabControl.add(grafical_tab, text='Graph Visualization')

    def create_tab_matricial_petri(self, tabControl: ttk.Notebook):
        grafical_tab = ttk.Frame(tabControl)

        tabControl.add(grafical_tab, text='Matrix Visualization')
