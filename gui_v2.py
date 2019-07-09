import tkinter as tk
from tkinter import font
from functools import partial
import os
import re

from ecc import *

from keystorage import *

from fastecdsa import point

import parser

import musig_distr_final as ms


def testfunc(m):
    print(f'>> {m}')


def path_checker(path):
    if os.path.isfile(path):
        # if path is a file, then file name is taken
        return 10 #valid path, filename taken
    elif os.path.isdir(path):
        # if path is not a file, then check if its a directory
        return 0 #valid directory
    else:
        # if path is neither an existing file, nor a dir, then it can be a new file or an invalid path
        directory, filename = os.path.split(path)
        if os.path.isdir(directory):
            return 1 # valid new file
        else:
            return 11 # invalid path


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

        mode_sub_menu.add_command(label='MuSig', command=partial(self.switch_frame, PageMuSig))
        mode_sub_menu.add_command(label='Verification', command=partial(self.switch_frame, PageMuSigVer))


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


# class PageMuSig(PageBase):
#     def __init__(self, master):
#         PageBase.__init__(self, master)
#         tk.Label(self, text="MuSig", font=self.title_font).pack(side="top", fill="x", pady=10)
#         b_generate = tk.Button(self, text="Verify", command=partial(master.switch_frame, PageMuSigVerify))
#         b_generate.pack(side=tk.BOTTOM)
#         b_generate = tk.Button(self, text="Sign", command=partial(master.switch_frame, PageMuSigSign))
#         b_generate.pack(side=tk.BOTTOM)


class PageMuSig(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="MuSig (Sign)", font=self.title_font).pack(side="top", fill="x", pady=10)
        # INPUT: n signatures from file, files that contains the priv and pub keys
        # OUTPUT: signature

        self.r_point = None
        self.partial_signature = None
        self.aggregated_key = None
        self.proof = None

        self.path = tk.StringVar()
        tk.Label(self, text="Signer setup file path:").pack(padx=1, pady=1)
        e_signers = tk.Entry(self, textvariable=self.path)
        e_signers.pack()

        self.output_file = tk.StringVar()
        tk.Label(self, text="Output file:").pack(padx=1, pady=1)
        e_output = tk.Entry(self, textvariable=self.output_file)
        e_output.pack()

        b_sign = tk.Button(self, text="Sign", command=self.signature_handler)
        b_sign.pack()

        self.output_box = tk.Text(self)
        self.output_box.pack(side=tk.BOTTOM)

    def signature_handler(self):
        path = self.path.get()
        output_file = self.output_file.get()

        if path == '':
            s = f'Invalid path'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        # setup info
        si = parser.Info(path)

        s = '\n--------------------------------------------------------------------------------'
        self.output_box.insert(tk.END, s)
        self.output_box.see(tk.END)

        self.r_point, self.partial_signature, self.aggregated_key, self.proof = ms.musig_distributed_with_key_verification(
            si.message, si.my_key, si.public_key_list, si.address_dict, si.hostname, si.port,
            ec=si.ec, h_com=si.h_com, h_agg=si.h_agg, h_sig=si.h_sig,
            h_tree=si.h_tree, complete_pub_keys_list=si.complete_pub_key_lst, restrictions=si.restrictions
        )

        #si.print_test()

        parser.signature_output(output_file, self.r_point, self.partial_signature, si.message, self.aggregated_key, self.proof, si.ec, si.h_sig, si.h_tree)

        s = f'Resulting signature:\n(R,s): ({self.r_point},{self.partial_signature})\nAggregated key: {self.aggregated_key}\nProof: {self.proof}'
        s += '\n--------------------------------------------------------------------------------'
        self.output_box.insert(tk.END, s)
        self.output_box.see(tk.END)

class PageMuSigVer(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="MuSig - Signature Verification", font=self.title_font).pack(side="top", fill="x", pady=10)
        # INPUT: n signatures from file, files that contains the priv and pub keys
        # OUTPUT: signature

        self.root = None
        self.result = None

        self.path = tk.StringVar()
        tk.Label(self, text="Signer setup file path:").pack(padx=1, pady=1)
        e_signers = tk.Entry(self, textvariable=self.path)
        e_signers.pack()

        self.root_path = tk.StringVar()
        tk.Label(self, text="Merkle tree root setup file path:").pack(padx=1, pady=1)
        e_root = tk.Entry(self, textvariable=self.root_path)
        e_root.pack()

        b_sign = tk.Button(self, text="Verify", command=self.verification_handler)
        b_sign.pack()

        self.output_box = tk.Text(self)
        self.output_box.pack(side=tk.BOTTOM)

    def verification_handler(self):
        path = self.path.get()
        root_path = self.root_path.get()

        if path == '':
            s = f'Invalid path'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        # setup info
        si = parser.Info(path)

        root_info = parser.Info(root_path)

        s = '\n--------------------------------------------------------------------------------'
        self.output_box.insert(tk.END, s)
        self.output_box.see(tk.END)

        self.root = root_info.root

        self.result = ms.musig_ver_with_key_verification(si.r_point, si.signature, si.message, si.proof, si.aggregated_key, self.root, ec=si.ec, h_sig=si.h_sig,
                                    h_tree=si.h_tree)
        #si.print_test()
        #root_info.print_test()

        s = f'Verification result: {self.result}\n'
        s += '\n--------------------------------------------------------------------------------'
        self.output_box.insert(tk.END, s)
        self.output_box.see(tk.END)




app = Application()
app.mainloop()
