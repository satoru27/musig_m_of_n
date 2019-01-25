import tkinter as tk
from tkinter import font
from functools import partial


def testfunc(m):
    print(f'>> {m}')


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.menu()
        self.status_bar()
        self.switch_frame(InitialPage)

    def switch_frame(self, target_frame):
        new_frame = target_frame(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    def menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        mode_sub_menu = tk.Menu(menu)
        menu.add_cascade(label='Mode', menu=mode_sub_menu)
        mode_sub_menu.add_command(label='Simple Schnorr Signature',
                                  command=partial(self.switch_frame, PageSimpleSchnorr))
        mode_sub_menu.add_command(label='Naive Multi Signature', command=partial(self.switch_frame, PageNaiveMuSig))
        mode_sub_menu.add_command(label='Rogue-key Attack', command=partial(self.switch_frame, PageRogueKeyAttack))
        mode_sub_menu.add_command(label='Bellare Neven Multi Signature Scheme',
                                  command=partial(self.switch_frame, PageBellareNeven))
        mode_sub_menu.add_command(label='MuSig', command=partial(self.switch_frame, PageMuSig))
        mode_sub_menu.add_command(label='MuSig (Distributed)', command=partial(self.switch_frame, PageMuSigDistr))

        options_sub_menu = tk.Menu(menu)
        menu.add_cascade(label='Options', menu=options_sub_menu)
        options_sub_menu.add_command(label='Debug', command=partial(testfunc, 'Debug'))
        #options_sub_menu.add_command(label='Exit', command=frame.quit)

    def status_bar(self):
        status = tk.Label(self, text='Test label', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)


class PageBase(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.title_font = font.Font(size=18, weight="bold", slant="italic")


class InitialPage(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="Welcome", font=self.title_font).pack(side="top", fill="x", pady=10)


class PageSimpleSchnorr(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="Simple Schnorr Signature", font=self.title_font).pack(side="top", fill="x", pady=10)


class PageNaiveMuSig(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="Naive Multi Signature Scheme", font=self.title_font).pack(side="top", fill="x", pady=10)


class PageRogueKeyAttack(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="Rogue-key Attack", font=self.title_font).pack(side="top", fill="x", pady=10)


class PageBellareNeven(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="Bellare Neve Multi Signature Scheme", font=self.title_font).pack(side="top", fill="x", pady=10)


class PageMuSig(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="MuSig", font=self.title_font).pack(side="top", fill="x", pady=10)


class PageMuSigDistr(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="MuSig (Distributed)", font=self.title_font).pack(side="top", fill="x", pady=10)

app = Application()
app.mainloop()
