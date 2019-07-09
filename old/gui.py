import tkinter as tk
from tkinter import font
from functools import partial
import os
import re

from ecc import *

from keystorage import *

from fastecdsa import point

def testfunc(m):
    print(f'>> {m}')


# mudar o dict de curvas da classe da pagina
curves = {"secp256k1": curve.secp256k1, "secp224k1": curve.secp224k1 ,"brainpoolP256r1": curve.brainpoolP256r1,
          "brainpoolP384r1": curve.brainpoolP384r1 ,"brainpoolP512r1": curve.brainpoolP512r1}

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


def point_handler(parameters):
    x_value = re.search('X:(.*)Y:', parameters).group(1).strip(' ')
    y_value = re.search('Y:(.*)\\(', parameters).group(1).strip(' ')
    curve_name = re.search('<(.*)>', parameters).group(1).strip(' ')

    x_value = int(x_value, 0)
    y_value = int(y_value, 0)
    p = point.Point(x_value, y_value, curves[curve_name])

    return p

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
        self.key_path = tk.StringVar()
        self.last_chosen_curve = None

        PageBase.__init__(self, master)
        tk.Label(self, text="Keys Generation", font=self.title_font).pack(side="top", fill="x", pady=10)

        curve_menu = tk.OptionMenu(self, self.curve_choices_var, *self.curve_choices)
        tk.Label(self, text="Curve:").pack(padx=1, pady=1)
        curve_menu.pack(padx=1, pady=1)
        self.curve_choices_var.trace('w', self.change_dropdown)

        b_generate = tk.Button(self, text="Generate keys", command=partial(self.key_generation_handler,
                                                                           self.curve_choices_var.get()))
        b_generate.pack(side="bottom")
        self.output_box = tk.Text(self)
        self.output_box.pack(side=tk.BOTTOM)

        tk.Label(self, text="Enter the file path where the keys will be saved:").pack(padx=1, pady=1)
        path_entry = tk.Entry(self, textvariable=self.key_path)
        path_entry.pack()
        b_path = tk.Button(self, text="Save keys", command=self.save_keys_handler)
        b_path.pack(side="bottom")

    def key_generation_handler(self, ec):
        self.last_chosen_curve = ec
        self.pub_key, self.priv_key = key_generation(self.curve_choices[self.last_chosen_curve])
        s = f'On curve: {self.last_chosen_curve}\nPublic Key:\n{self.pub_key}\nPrivate Key:\n{self.priv_key}\n'
        s = s + '\n--------------------------------------------------------------------------------'
        self.output_box.insert(tk.END, s)
        self.output_box.see(tk.END)

    def save_keys_handler(self):

        path = self.key_path.get()
        check_result = path_checker(path)
        print(f'PATH CHECK RESULT: {check_result}')

        if self.priv_key is None or self.pub_key is None:
            s = f'Keys were not generated!'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        if check_result == 10:
            s = f'File name is taken'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        if check_result == 11:
            s = f'Invalid path'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        if check_result == 0:
            if path == './':
                path += 'key_ecc.pem'
            else:
                path += '/key_ecc.pem'
            if os.path.isfile(path):
                s = f'File name key_ecc.pem is taken'
                s = s + '\n--------------------------------------------------------------------------------'
                self.output_box.insert(tk.END, s)
                self.output_box.see(tk.END)
                return

        if check_result == 1:
            export_keys(int(self.priv_key), self.curve_choices[self.last_chosen_curve], path)
            s = f'Keys saved on {path}'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return


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
        b_generate = tk.Button(self, text="Verify", command=partial(master.switch_frame, PageMuSigVerify))
        b_generate.pack(side=tk.BOTTOM)
        b_generate = tk.Button(self, text="Sign", command=partial(master.switch_frame, PageMuSigSign))
        b_generate.pack(side=tk.BOTTOM)


class PageMuSigSign(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="MuSig (Sign)", font=self.title_font).pack(side="top", fill="x", pady=10)
        # INPUT: n signatures from file, files that contains the priv and pub keys
        # OUTPUT: signature

        self.signature = None
        self.r = None

        self.signers_path = tk.StringVar()
        tk.Label(self, text="Signers keys paths (separated by \'|\'):").pack(padx=1, pady=1)
        e_signers = tk.Entry(self, textvariable=self.signers_path)
        e_signers.pack()

        self.message = tk.StringVar()
        tk.Label(self, text="Message:").pack(padx=1, pady=1)
        e_message = tk.Entry(self, textvariable=self.message)
        e_message.pack()

        b_sign = tk.Button(self, text="Sign", command=self.signature_handler)
        b_sign.pack()

        self.output_box = tk.Text(self)
        self.output_box.pack(side=tk.BOTTOM)

    def signature_handler(self):
        signers_path = self.signers_path.get()
        message = self.message.get()

        if message == '':
            s = f'Invalid message'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        if signers_path == '':
            s = f'Invalid path'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        signers_path = signers_path.split('|')
        print(signers_path)
        n = len(signers_path)

        for i in range(n):
            signers_path[i] = signers_path[i].strip(' ')
            s = f'{signers_path[i]}\n'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)

        s = '\n--------------------------------------------------------------------------------'
        self.output_box.insert(tk.END, s)
        self.output_box.see(tk.END)

        for i in range(n):
            if not os.path.isfile(signers_path[i]):
                s = f'Error: the file {signers_path[i]} does not exist'
                s += '\n--------------------------------------------------------------------------------'
                self.output_box.insert(tk.END, s)
                self.output_box.see(tk.END)
                return

        keys = []
        for i in range(n):
            keys.append(import_keys(signers_path[i]))


        # gambiarra --> a ordem no codigo do musig e pub,priv, a output do import key e priv,pub
        # switch
        keys_temp = keys
        for i in range(n):
            keys[i] = keys_temp[i][1], keys_temp[i][0]

        self.r, self.signature = musig(message, keys) #adicionar o switch de curvas elipticas e repassar como argumento

        s = f'Signature for message \"{message}\":\n R:\n{self.r}\n s:{self.signature}\n'
        s += '\n--------------------------------------------------------------------------------'
        self.output_box.insert(tk.END, s)
        self.output_box.see(tk.END)

class PageMuSigVerify(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="MuSig (Verification)", font=self.title_font).pack(side="top", fill="x", pady=10)
        # INPUT: n signatures from file, files that contains the priv and pub keys
        # OUTPUT: signature

        self.signers_path = tk.StringVar()
        self.signature = tk.StringVar()
        self.r = tk.StringVar()
        self.message = tk.StringVar()

        self.signers_path = tk.StringVar()
        tk.Label(self, text="Signers keys paths (separated by \'|\'):").pack(padx=1, pady=1)
        e_signers = tk.Entry(self, textvariable=self.signers_path)
        e_signers.pack()

        #temporario, salvar a assinatura em um arquivo e depois carrega - lo
        tk.Label(self, text="R:").pack(padx=1, pady=1)
        e_message = tk.Entry(self, textvariable=self.r)
        e_message.pack()

        tk.Label(self, text="s:").pack(padx=1, pady=1)
        e_message = tk.Entry(self, textvariable=self.signature)
        e_message.pack()

        tk.Label(self, text="Message:").pack(padx=1, pady=1)
        e_message = tk.Entry(self, textvariable=self.message)
        e_message.pack()

        b_sign = tk.Button(self, text="Verify", command=self.verify_handler)
        b_sign.pack()

        self.output_box = tk.Text(self)
        self.output_box.pack(side=tk.BOTTOM)

    def verify_handler(self):
        signers_path = self.signers_path.get()
        message = self.message.get()
        signature = int(self.signature.get())
        r = self.r.get()

        if message == '':
            s = f'Invalid message'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        if signers_path == '':
            s = f'Invalid path'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        if r == '':
            s = f'Invalid r'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        if signature == '':
            s = f'Invalid s'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return

        signers_path = signers_path.split('|')
        print(signers_path)
        n = len(signers_path)

        for i in range(n):
            signers_path[i] = signers_path[i].strip(' ')
            s = f'{signers_path[i]}\n'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)

        s = '\n--------------------------------------------------------------------------------'
        self.output_box.insert(tk.END, s)
        self.output_box.see(tk.END)

        for i in range(n):
            if not os.path.isfile(signers_path[i]):
                s = f'Error: the file {signers_path[i]} does not exist'
                s += '\n--------------------------------------------------------------------------------'
                self.output_box.insert(tk.END, s)
                self.output_box.see(tk.END)
                return

        keys = []
        for i in range(n):
            temp = import_keys(signers_path[i])
            keys.append(temp[1]) # pegando apenas a chave publica

        r = point_handler(r)

        ok = False
        ok = musig_ver(r, signature, message, keys) # atualizar para receber tambem a curva

        if ok:
            s = f'PASS'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return
        else:
            s = f'FAIL'
            s = s + '\n--------------------------------------------------------------------------------'
            self.output_box.insert(tk.END, s)
            self.output_box.see(tk.END)
            return


class PageMuSigDistr(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        self.n_signers = 0
        tk.Label(self, text="MuSig (Distributed)", font=self.title_font).pack(side="top", fill="x", pady=10)

        b_generate = tk.Button(self, text="Verify", command=partial(master.switch_frame, PageMuSigDistrVerify))
        b_generate.pack(side=tk.BOTTOM)
        b_generate = tk.Button(self, text="Sign", command=partial(master.switch_frame, PageMuSigDistrSign))
        b_generate.pack(side=tk.BOTTOM)


class PageMuSigDistrSign(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        tk.Label(self, text="MuSig (Distributed) Sign", font=self.title_font).pack(side="top", fill="x", pady=10)
        self.user_key_path_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.paths_var = []
        #self.path_entry = []
        self.address_var = []
        #self.address_entry = []
        self.n = 0
        self.n_signers_var = tk.StringVar()
        tk.Label(self, text="Number of signers:").pack(side=tk.LEFT, padx=1, pady=1)
        e_n_signers = tk.Entry(self, textvariable=self.n_signers_var)
        e_n_signers.pack(side=tk.LEFT)
        b_generate = tk.Button(self, text="Ok", command=self.entry_fields)
        b_generate.pack(side=tk.LEFT)

    def entry_fields(self):
        self.n = int(self.n_signers_var.get())

        tk.Label(self, text=f"User key path:").pack(padx=1, pady=1)
        path_entry = tk.Entry(self, textvariable=self.user_key_path_var)
        path_entry.pack()

        for i in range(self.n-1):
            path_var = tk.StringVar()
            self.paths_var.append(path_var)
            tk.Label(self, text=f"Path {i+1}:").pack(padx=1, pady=1)
            path_entry = tk.Entry(self, textvariable=self.paths_var[i])
            path_entry.pack()

            address_var = tk.StringVar()
            self.address_var.append(address_var)
            tk.Label(self, text=f"Address {i+1}:").pack(padx=1, pady=1)
            address_entry = tk.Entry(self, textvariable=self.address_var[i])
            address_entry.pack()

        tk.Label(self, text="Message:").pack(side=tk.LEFT, padx=1, pady=1)
        e_message = tk.Entry(self, textvariable=self.message_var)
        e_message.pack(side=tk.LEFT)

        b_generate = tk.Button(self, text="Sign", command=self.sign)
        b_generate.pack()

        self.output_box = tk.Text(self)
        self.output_box.pack(side=tk.BOTTOM)

    def address_parser(self):
        # enderecos na forma ip:port
        address = []
        for entry in self.address_var:
            s = entry.get()
            print(s)
            ip = re.search('(.*):', s).group(1).strip(' ')
            port = int(re.search(':(.*)', s).group(1).strip(' '))
            temp = (ip, port)
            address.append(temp)
        return address

    def keys_parser(self):
        keys = []
        for filepath in self.paths_var:
            keys.append(import_keys(filepath.get()))
        return keys

    def sign(self):
        addr = self.address_parser()
        print(addr)
        keys = self.keys_parser()
        print(keys)
        user_key = import_keys(self.user_key_path_var.get())
        address_dict = {}
        for key, addr in zip(keys,addr):
            address_dict.update({str(key): addr})

        print(f'\n{self.message_var.get()}\n')
        print(f'\n{user_key}\n')
        print(f'\n{keys}\n')
        print(f'\n{address_dict}\n')

        #musig_distributed(self.message_var.get(), user_key, keys, address_dict, ec=curve.secp256k1)




class PageMuSigDistrVerify(PageBase):
    def __init__(self, master):
        PageBase.__init__(self, master)
        self.n_signers = 0
        tk.Label(self, text="MuSig (Distributed) Verify", font=self.title_font).pack(side="top", fill="x", pady=10)
        self.n_signers_var = tk.StringVar()
        tk.Label(self, text="Number of signers:").pack(padx=1, pady=1)
        e_n_signers = tk.Entry(self, textvariable=self.n_signers_var)
        e_n_signers.pack()
        b_generate = tk.Button(self, text="Ok", command=partial(master.switch_frame, PageMuSigDistrSign))
        b_generate.pack(side=tk.BOTTOM)


app = Application()
app.mainloop()
