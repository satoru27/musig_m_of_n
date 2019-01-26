import tkinter as tk
from tkinter import font
from functools import partial

from ecc import *

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
        mode_sub_menu.add_command(label='Key Generation', command=partial(self.switch_frame, KeyGeneration))
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

    curve_choices_var = None

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.title_font = font.Font(size=18, weight="bold", slant="italic")
        self.curve_choices = {"secp256k1 (bitcoin curve)":curve.secp256k1, "secp224k1":curve.secp224k1
                                 , "brainpoolP256r1":curve.brainpoolP256r1, "brainpoolP384r1":curve.brainpoolP384r1,
                              "brainpoolP512r1":curve.brainpoolP512r1}
        self.curve_choices_var = tk.StringVar(master)
        self.curve_choices_var.set('secp256k1 (bitcoin curve)')

    def change_dropdown(self, *args):
        print(self.curve_choices_var.get())

class InitialPage(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="Welcome", font=self.title_font).pack(side="top", fill="x", pady=10)


class KeyGeneration(PageBase):

    def __init__(self, master):
        self.priv_key = None
        self.pub_key = None

        PageBase.__init__(self, master)
        tk.Label(self, text="Keys Generation", font=self.title_font).pack(side="top", fill="x", pady=10)

        curve_menu = tk.OptionMenu(self, self.curve_choices_var, *self.curve_choices)
        tk.Label(self, text="Curve:").pack(padx=1, pady=1)
        curve_menu.pack(padx=1, pady=1)
        self.curve_choices_var.trace('w', self.change_dropdown)

        b_generate = tk.Button(master, text="Generate keys", command=partial(self.key_generation_handler,
                                                                             self.curve_choices_var.get()))
        b_generate.pack(side="bottom")
        self.output_box = tk.Text(master)
        self.output_box.pack(side=tk.BOTTOM)

    def key_generation_handler(self, ec):
        self.pub_key, self.priv_key = key_generation(self.curve_choices[ec])
        s = f'On curve: {self.curve_choices_var.get()}\nPublic Key:\n{self.pub_key}\nPrivate Key:\n{self.priv_key}\n'
        s = s + '\n--------------------------------------------------------------------------------'
        self.output_box.insert(tk.END, s)
        self.output_box.see(tk.END)





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
