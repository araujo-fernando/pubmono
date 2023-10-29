from tkinter import Menu, filedialog, simpledialog


class MainMenu(Menu):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._parent = parent
        self._create_file_cascade()
        self._create_simulation_cascade()
        self._create_algorithms_cascade()
        self._create_settings_cascade()

    def _create_file_cascade(self):
        menu = Menu(self, tearoff=0)

        def onNew():
            size = simpledialog.askinteger(
                title="Petri Network Size", prompt="Size of matrix A:", minvalue=1, initialvalue=2
            )

        def onOpen():
            print(
                filedialog.askopenfilename(
                    initialdir="/",
                    title="Open file",
                    filetypes=(("Plain text files", "*.txt"),),
                )
            )

        def onSave():
            print(
                filedialog.asksaveasfilename(
                    initialdir="/",
                    title="Save as",
                    filetypes=(("Plain text files", "*.txt"),),
                )
            )

        def onExit():
            onSave()
            quit()

        menu.add_command(label="New", command=onNew)
        menu.add_command(label="Open", command=onOpen)
        menu.add_command(label="Save", command=onSave)
        menu.add_command(label="Exit", command=onExit)

        self.add_cascade(label="File", menu=menu)

    def _create_simulation_cascade(self):
        menu = Menu(self, tearoff=0)

        menu.add_command(label="Run 1 Random Step")
        menu.add_command(label="Run N Random Steps")
        menu.add_command(label="Execute Transitions")

        self.add_cascade(label="Simulation", menu=menu)

    def _create_algorithms_cascade(self):
        menu = Menu(self, tearoff=0)

        menu.add_command(label="Label Transitions")
        menu.add_command(label="Generate State Tree")

        self.add_cascade(label="Algorithms", menu=menu)

    def _create_settings_cascade(self):
        menu = Menu(self, tearoff=0)

        def onWindowResolution_4k():
            self._parent.geometry("3840x2160")

        def onWindowResolution_full_hd():
            self._parent.geometry("1920x1080")

        def onWindowResolution_hd():
            self._parent.geometry("1280x720")

        res_menu = Menu(menu, tearoff=0)
        res_menu.add_command(label="4K", command=onWindowResolution_4k)
        res_menu.add_command(label="Full HD", command=onWindowResolution_full_hd)
        res_menu.add_command(label="HD", command=onWindowResolution_hd)
        menu.add_cascade(label="Window Resolution", menu=res_menu)

        self.add_cascade(label="Settings", menu=menu)
