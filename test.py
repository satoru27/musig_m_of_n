#import tkinter as tk


# class Application(tk.Frame):
#     def __init__(self, master=None):
#         tk.Frame.__init__(self, master)
#         self.grid()
#         self.createWidgets()
#
#     def createWidgets(self):
#         self.quitButton = tk.Button(self, text='Quit',command=self.quit())
#         self.quitButton.grid()
#
#
# app = Application()
# app.master.title('Sample application')
# app.mainloop()


#root = tk.Tk()

# label_1 = tk.Label(root, text='Name')
# label_2 = tk.Label(root, text='Password')
# entry_1 = tk.Entry(root)
# entry_2 = tk.Entry(root)
#
# label_1.grid(row=0, sticky=tk.E)
# label_2.grid(row=1, sticky=tk.E)
#
# entry_1.grid(row=0, column=1)
# entry_2.grid(row=1, column=1)
#
# c = tk.Checkbutton(root, text= "Keep me logged in")
# c.grid(columnspan=2)

# def printName():
#     print('potato')
#
#
# button_1 = tk.Button(root, text='Print my name', command=printName)
# button_1.pack()

# def printName2(event):
#     print('potato!')
#
#
# button_2 = tk.Button(root, text='Print my name')
# button_2.bind("<Button-1>", printName2)
# button_2.pack()

# def leftClick(event):
#     print('left')
#
# def rightClick(event):
#     print('right')
#
# def middleClick(event):
#     print('middle')
#
# frame = tk.Frame(root, width=300, height=250)
# frame.bind('<Button-1>', leftClick)
# frame.bind('<Button-2>', middleClick)
# frame.bind('<Button-3>', rightClick)
# frame.pack()

# class Buttons:
#     def __init__(self, master):
#         frame = tk.Frame(master)
#         frame.pack()
#
#         self.print_button = tk.Button(frame, text='Print message', command=self.print_message)
#         self.print_button.pack(side=tk.LEFT)
#
#         self.quit_button = tk.Button(frame, text='Quit', command=frame.quit)
#         self.quit_button.pack(side=tk.LEFT)
#
#     def print_message(self):
#         print('Ayyyyyyyy')
#
#
# root = tk.Tk()
# app = Buttons(root)
# root.mainloop()

# toolbar = Frame(root, bg='blue')
# insertButton =  Button(toolbar, text='Insert', command=doNothing)
# insertButton.pack(side=LEFT,padx=2,pady=)
# printButton = Button(...)
#
# status = Label(root, text='Test', bd=1,relief=SUNKEN,anchor=W)
# status.pack(side=BOTTOM,fill=X)
#
# tk.messagebox.showinfo('Window title','Description')
# answer = tk.messagebox.askquestion('question 1','sure')
# if answer == 'yes'

import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
#import Tkinter as tk     # python 2
#import tkFont as tkfont  # python 2
#
# class SampleApp(tk.Tk):
#
#     def __init__(self, *args, **kwargs):
#         tk.Tk.__init__(self, *args, **kwargs)
#
#         self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
#
#         # the container is where we'll stack a bunch of frames
#         # on top of each other, then the one we want visible
#         # will be raised above the others
#         container = tk.Frame(self)
#         container.pack(side="top", fill="both", expand=True)
#         container.grid_rowconfigure(0, weight=1)
#         container.grid_columnconfigure(0, weight=1)
#
#         self.frames = {}
#         for F in (StartPage, PageOne, PageTwo):
#             page_name = F.__name__
#             frame = F(parent=container, controller=self)
#             self.frames[page_name] = frame
#
#             # put all of the pages in the same location;
#             # the one on the top of the stacking order
#             # will be the one that is visible.
#             frame.grid(row=0, column=0, sticky="nsew")
#
#         self.show_frame("StartPage")
#
#     def show_frame(self, page_name):
#         '''Show a frame for the given page name'''
#         frame = self.frames[page_name]
#         frame.tkraise()
#
#
# class StartPage(tk.Frame):
#
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         self.controller = controller
#         label = tk.Label(self, text="This is the start page", font=controller.title_font)
#         label.pack(side="top", fill="x", pady=10)
#
#         button1 = tk.Button(self, text="Go to Page One",
#                             command=lambda: controller.show_frame("PageOne"))
#         button2 = tk.Button(self, text="Go to Page Two",
#                             command=lambda: controller.show_frame("PageTwo"))
#         button1.pack()
#         button2.pack()
#
#
# class PageOne(tk.Frame):
#
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         self.controller = controller
#         label = tk.Label(self, text="This is page 1", font=controller.title_font)
#         label.pack(side="top", fill="x", pady=10)
#         button = tk.Button(self, text="Go to the start page",
#                            command=lambda: controller.show_frame("StartPage"))
#         button.pack()
#
#
# class PageTwo(tk.Frame):
#
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         self.controller = controller
#         label = tk.Label(self, text="This is page 2", font=controller.title_font)
#         label.pack(side="top", fill="x", pady=10)
#         button = tk.Button(self, text="Go to the start page",
#                            command=lambda: controller.show_frame("StartPage"))
#         button.pack()
#
#
# if __name__ == "__main__":
#     app = SampleApp()
#     app.mainloop()

# import tkinter as tk
#
# def cbc(id, tex):
#     return lambda : callback(id, tex)
#
# def callback(id, tex):
#     s = 'At {} f is {}\n'.format(id, id**id/0.987)
#     tex.insert(tk.END, s)
#     tex.see(tk.END)             # Scroll if necessary
#
# top = tk.Tk()
# tex = tk.Text(master=top)
# tex.pack(side=tk.RIGHT)
# bop = tk.Frame()
# bop.pack(side=tk.LEFT)
# for k in range(1,10):
#     tv = 'Say {}'.format(k)
#     b = tk.Button(bop, text=tv, command=cbc(k, tex))
#     b.pack()
#
# tk.Button(bop, text='Exit', command=top.destroy).pack()
# top.mainloop()

# from fastecdsa import curve,keys
#
# priv, pub = keys.gen_keypair(curve.secp256k1)
# print(type(priv))
# #keys.export_key(priv, curve=curve.secp256k1, filepath='/home/satoru/PycharmProjects/ecc/key.pem')
# keys.export_key(pub, curve=curve.secp256k1, filepath='/home/satoru/PycharmProjects/ecc/key2.pem')
# print(keys.import_key('/home/satoru/PycharmProjects/ecc/key2.pem'))

# from fastecdsa import point
# import re
#
# def point_handler(parameters):
#     x_value = re.search('X:(.*)Y:', parameters).group(1).strip(' ')
#     y_value = re.search('Y:(.*)\\(', parameters).group(1).strip(' ')
#     curve_name = re.search('<(.*)>', parameters).group(1).strip(' ')
#
#     x_value = int(x_value, 0)
#     y_value = int(y_value, 0)
#     curves = {"secp256k1": curve.secp256k1, "secp224k1": curve.secp224k1
#         , "brainpoolP256r1": curve.brainpoolP256r1, "brainpoolP384r1": curve.brainpoolP384r1,
#                      "brainpoolP512r1": curve.brainpoolP512r1}
#     p = point.Point(x_value, y_value, curves[curve_name])
#
#     return p
#
#
# p = 'X: 0xfea64471d4be76a86c2d954a01f7bd77d07aad13203557437fdf8db2d617a65a Y: 0x5180fd4c6b37b75090e10e2ac737063df29e49db1e7cf3ce864d99b9861181e7 (On curve <secp256k1>)'
# print(p)
# point_handler(p)

# signer 1: key90,'127.0.0.1', 2436
# signer 2: key2, '127.0.0.1', 2437
# signer 3: key4, '127.0.0.1', 2438

#from musigdistr import *
from musig_distr_final import *
import musig
import sys
import keystorage
import os
import merkle

def test1():
    input('FIRE_1>')
    hostname, port = '127.0.0.1', 2436

    my_key = keystorage.import_keys('key90.pem')
    key2 = keystorage.import_keys('key2.pem')
    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('k2.pem')

    #restriction = [(my_key[1], key2[1], key3[1], key4[1])]
    restriction = None

    key2 = (None, key2[1])
    key3 = (None, key3[1])
    key4 = (None, key4[1])

    addr2 = ('127.0.0.1', 2437)
    addr3 = ('127.0.0.1', 2438)
    addr4 = ('127.0.0.1', 2439)

    m = 'teste39826c4b39'

    address_dict = {str(key2[1]): addr2, str(key3[1]): addr3, str(key4[1]):addr4}

    pub_key_lst = [key2[1], key3[1], key4[1]]

    # R, s = musig_distributed(m, my_key, pub_key_lst, address_dict, hostname, port)
    # #os.system('clear')
    # print(f'\nR: {R}\ns: {s}\n')
    #
    # pub_key_lst.append(my_key[1])
    # #adicionar a chave do assinanete a list de chaves publicas
    # print(musig_ver(R, s, m, pub_key_lst, ec=curve.secp256k1, hash=hs.sha256))

    r_point, signature, aggregated_key, proof = musig_distributed_with_key_verification(m, my_key, pub_key_lst,
                                                                                        address_dict, hostname,
                                                                                        port, ec=curve.secp256k1,
                                                                                        hash=hs.sha256,
                                                                                        complete_pub_keys_list=None,
                                                                                        restrictions=restriction)

    print(80*'-')
    print(f'{r_point}')
    print(f'{signature}')
    print(f'{aggregated_key}')
    print(f'{proof}')

    pub_key_lst.append(my_key[1])
    result = musig_ver_with_key_verification(r_point, signature, m, pub_key_lst, aggregated_key, proof,
                                             restrictions=restriction,
                                             ec=curve.secp256k1)
    print(f'RESULT: {result}')

def test2():
    input('FIRE_2>')
    hostname, port = '127.0.0.1', 2437

    my_key = keystorage.import_keys('key2.pem')
    key2 = keystorage.import_keys('key90.pem')
    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('k2.pem')

    key2 = (None, key2[1])
    key3 = (None, key3[1])
    key4 = (None, key4[1])

    # restriction = [(my_key[1], key2[1], key3[1], key4[1])]
    restriction = None

    addr2 = ('127.0.0.1', 2436)
    addr3 = ('127.0.0.1', 2438)
    addr4 = ('127.0.0.1', 2439)

    m = 'teste39826c4b39'

    address_dict = {str(key2[1]): addr2, str(key3[1]): addr3, str(key4[1]): addr4}

    pub_key_lst = [key2[1], key3[1], key4[1]]

    # R, s = musig_distributed(m, my_key, pub_key_lst, address_dict, hostname, port)
    # #os.system('clear')
    # print(f'\nR: {R}\ns: {s}\n')
    # pub_key_lst.append(my_key[1])
    # print(musig_ver(R, s, m, pub_key_lst, ec=curve.secp256k1, hash=hs.sha256))
    r_point, signature, aggregated_key, proof = musig_distributed_with_key_verification(m, my_key, pub_key_lst,
                                                                                        address_dict, hostname,
                                                                                        port, ec=curve.secp256k1,
                                                                                        hash=hs.sha256,
                                                                                        complete_pub_keys_list=None,
                                                                                        restrictions=restriction)

    print(80 * '-')
    print(f'{r_point}')
    print(f'{signature}')
    print(f'{aggregated_key}')
    print(f'{proof}')

    pub_key_lst.append(my_key[1])
    result = musig_ver_with_key_verification(r_point, signature, m, pub_key_lst, aggregated_key, proof,
                                             restrictions=restriction,
                                             ec=curve.secp256k1)
    print(f'RESULT: {result}')

def test3():
    input('FIRE_3>')
    hostname, port = '127.0.0.1', 2438

    my_key = keystorage.import_keys('key4.pem')
    key2 = keystorage.import_keys('key90.pem')
    key3 = keystorage.import_keys('key2.pem')
    key4 = keystorage.import_keys('k2.pem')

    key2 = (None, key2[1])
    key3 = (None, key3[1])
    key4 = (None, key4[1])

    # restriction = [(my_key[1], key2[1], key3[1], key4[1])]
    restriction = None

    addr2 = ('127.0.0.1', 2436)
    addr3 = ('127.0.0.1', 2437)
    addr4 = ('127.0.0.1', 2439)

    m = 'teste39826c4b39'

    address_dict = {str(key2[1]): addr2, str(key3[1]): addr3, str(key4[1]): addr4}

    pub_key_lst = [key2[1], key3[1], key4[1]]

    # R, s = musig_distributed(m, my_key, pub_key_lst, address_dict, hostname, port)
    # #os.system('clear')
    # print(f'\nR: {R}\ns: {s}\n')
    # pub_key_lst.append(my_key[1])
    # print(musig_ver(R, s, m, pub_key_lst, ec=curve.secp256k1, hash=hs.sha256))

    r_point, signature, aggregated_key, proof = musig_distributed_with_key_verification(m, my_key, pub_key_lst,
                                                                                        address_dict, hostname,
                                                                                        port, ec=curve.secp256k1,
                                                                                        hash=hs.sha256,
                                                                                        complete_pub_keys_list=None,
                                                                                        restrictions=restriction)

    print(80 * '-')
    print(f'{r_point}')
    print(f'{signature}')
    print(f'{aggregated_key}')
    print(f'{proof}')

    pub_key_lst.append(my_key[1])
    result = musig_ver_with_key_verification(r_point, signature, m, pub_key_lst, aggregated_key, proof,
                                             restrictions=restriction,
                                             ec=curve.secp256k1)
    print(f'RESULT: {result}')

def test4():
    input('FIRE_4>')
    hostname, port = '127.0.0.1', 2439

    my_key = keystorage.import_keys('k2.pem')
    key2 = keystorage.import_keys('key2.pem')
    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('key90.pem')

    key2 = (None, key2[1])
    key3 = (None, key3[1])
    key4 = (None, key4[1])

    # restriction = [(my_key[1], key2[1], key3[1], key4[1])]
    restriction = None

    addr2 = ('127.0.0.1', 2437)
    addr3 = ('127.0.0.1', 2438)
    addr4 = ('127.0.0.1', 2436)

    m = 'teste39826c4b39'

    address_dict = {str(key2[1]): addr2, str(key3[1]): addr3, str(key4[1]): addr4}

    pub_key_lst = [key2[1], key3[1], key4[1]]

    # R, s = musig_distributed(m, my_key, pub_key_lst, address_dict, hostname, port)
    # #os.system('clear')
    # print(f'\nR: {R}\ns: {s}\n')
    #
    # pub_key_lst.append(my_key[1])
    # #adicionar a chave do assinante a list de chaves publicas
    # print(musig_ver(R, s, m, pub_key_lst, ec=curve.secp256k1, hash=hs.sha256))

    r_point, signature, aggregated_key, proof = musig_distributed_with_key_verification(m, my_key, pub_key_lst,
                                                                                        address_dict, hostname,
                                                                                        port, ec=curve.secp256k1,
                                                                                        hash=hs.sha256,
                                                                                        complete_pub_keys_list=None,
                                                                                        restrictions=restriction)

    print(80 * '-')
    print(f'{r_point}')
    print(f'{signature}')
    print(f'{aggregated_key}')
    print(f'{proof}')

    pub_key_lst.append(my_key[1])
    result = musig_ver_with_key_verification(r_point, signature, m, pub_key_lst, aggregated_key, proof, restrictions=restriction,
                                    ec=curve.secp256k1)
    print(f'RESULT: {result}')

def test10(restriction_flag):
    input('FIRE_10>')
    hostname, port = '127.0.0.1', 2436

    my_key = keystorage.import_keys('key90.pem')
    key2 = keystorage.import_keys('key2.pem')

    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('k2.pem')

    restriction = None
    if restriction_flag:
        restriction = [(my_key[1], key2[1], key3[1], key4[1])]

    key2 = (None, key2[1])
    key3 = (None, key3[1])
    key4 = (None, key4[1])

    addr2 = ('127.0.0.1', 2437)
    addr3 = ('127.0.0.1', 2438)
    addr4 = ('127.0.0.1', 2439)

    m = 'teste39826c4b39'

    address_dict = {str(key2[1]): addr2,str(key3[1]): addr3,str(key4[1]): addr4}
    pub_key_lst = [key2[1], key3[1], key4[1]]

    complete_pub_key_lst = [my_key[1], key2[1], key3[1], key4[1]]

    # R, s = musig_distributed(m, my_key, pub_key_lst, address_dict, hostname, port)
    # #os.system('clear')
    # print(f'\nR: {R}\ns: {s}\n')
    #
    # pub_key_lst.append(my_key[1])
    # #adicionar a chave do assinanete a list de chaves publicas
    # print(musig_ver(R, s, m, pub_key_lst, ec=curve.secp256k1, hash=hs.sha256))


    r_point, signature, aggregated_key, proof = musig_distributed_with_key_verification(m, my_key, pub_key_lst,
                                                                                        address_dict, hostname,
                                                                                        port, ec=curve.secp256k1,
                                                                                        complete_pub_keys_list=complete_pub_key_lst,
                                                                                        restrictions=restriction)

    print(80*'-')
    print(f'{r_point}')
    print(f'{signature}')
    print(f'{aggregated_key}')
    print(f'{proof}')


    pub_key_lst.append(my_key[1])
    #merkle_tree = merkle.build_merkle_tree(complete_pub_key_lst, sorted_keys=False, restrictions=restriction)
    merkle_tree = merkle.build_merkle_tree(pub_key_lst, complete_public_key_list=complete_pub_key_lst,restrictions=restriction)

    print('$' * 80)
    print(f'MERKLE TREE:\n{merkle_tree}')
    print('$' * 80)


    # result = musig_ver_with_key_verification(r_point, signature, m, pub_key_lst, aggregated_key, proof,root = merkle_tree[0],
    #                                          complete_pub_key_lst=complete_pub_key_lst,
    #                                          restrictions=restriction,
    #                                          ec=curve.secp256k1)

    result = musig_ver_with_key_verification(r_point, signature, m, proof, aggregated_key, merkle_tree[0],
                                             ec=curve.secp256k1, h_sig=hs.sha256, h_tree=hs.sha256)

    print(f'RESULT: {result}')


def test20(restriction_flag):
    input('FIRE_20>')
    hostname, port = '127.0.0.1', 2437

    my_key = keystorage.import_keys('key2.pem')
    key2 = keystorage.import_keys('key90.pem')

    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('k2.pem')

    restriction = None
    if restriction_flag:
        restriction = [(my_key[1], key2[1], key3[1], key4[1])]

    key2 = (None, key2[1])
    key3 = (None, key3[1])
    key4 = (None, key4[1])

    addr2 = ('127.0.0.1', 2436)
    addr3 = ('127.0.0.1', 2438)
    addr4 = ('127.0.0.1', 2439)


    m = 'teste39826c4b39'

    address_dict = {str(key2[1]): addr2,str(key3[1]): addr3,str(key4[1]): addr4}
    pub_key_lst = [key2[1],key3[1],key4[1]]

    complete_pub_key_lst = [my_key[1], key2[1], key3[1], key4[1]]

    # R, s = musig_distributed(m, my_key, pub_key_lst, address_dict, hostname, port)
    # #os.system('clear')
    # print(f'\nR: {R}\ns: {s}\n')
    #
    # pub_key_lst.append(my_key[1])
    # #adicionar a chave do assinanete a list de chaves publicas
    # print(musig_ver(R, s, m, pub_key_lst, ec=curve.secp256k1, hash=hs.sha256))

    r_point, signature, aggregated_key, proof= musig_distributed_with_key_verification(m, my_key,
                                                                                                      pub_key_lst,
                                                                                                      address_dict,
                                                                                                      hostname,
                                                                                                      port,
                                                                                                      ec=curve.secp256k1,
                                                                                                      complete_pub_keys_list=complete_pub_key_lst,
                                                                                                      restrictions=restriction)

    print(80 * '-')
    print(f'{r_point}')
    print(f'{signature}')
    print(f'{aggregated_key}')
    print(f'{proof}')

    pub_key_lst.append(my_key[1])
    # merkle_tree = merkle.build_merkle_tree(complete_pub_key_lst, sorted_keys=False, restrictions=restriction)
    merkle_tree = merkle.build_merkle_tree(pub_key_lst, complete_public_key_list=complete_pub_key_lst,restrictions=restriction)

    print('$' * 80)
    print(f'MERKLE TREE:\n{merkle_tree}')
    print('$' * 80)

    # result = musig_ver_with_key_verification(r_point, signature, m, pub_key_lst, aggregated_key, proof,root = merkle_tree[0],
    #                                          complete_pub_key_lst=complete_pub_key_lst,
    #                                          restrictions=restriction,
    #                                          ec=curve.secp256k1)

    result = musig_ver_with_key_verification(r_point, signature, m, proof, aggregated_key, merkle_tree[0],
                                             ec=curve.secp256k1, h_sig=hs.sha256, h_tree=hs.sha256)
    print(f'RESULT: {result}')

def test30(restriction_flag):
    input('FIRE_30>')
    hostname, port = '127.0.0.1', 2438

    my_key = keystorage.import_keys('key4.pem')
    key2 = keystorage.import_keys('key2.pem')

    key3 = keystorage.import_keys('key90.pem')
    key4 = keystorage.import_keys('k2.pem')

    restriction = None
    if restriction_flag:
        restriction = [(my_key[1], key2[1], key3[1], key4[1])]

    key2 = (None, key2[1])
    key3 = (None, key3[1])
    key4 = (None, key4[1])

    addr2 = ('127.0.0.1', 2437)
    addr3 = ('127.0.0.1', 2436)
    addr4 = ('127.0.0.1', 2439)

    m = 'teste39826c4b39'

    address_dict = {str(key2[1]): addr2,str(key3[1]): addr3,str(key4[1]): addr4}
    pub_key_lst = [key2[1],key3[1],key4[1]]

    complete_pub_key_lst = [my_key[1], key2[1], key3[1], key4[1]]

    # R, s = musig_distributed(m, my_key, pub_key_lst, address_dict, hostname, port)
    # #os.system('clear')
    # print(f'\nR: {R}\ns: {s}\n')
    #
    # pub_key_lst.append(my_key[1])
    # #adicionar a chave do assinanete a list de chaves publicas
    # print(musig_ver(R, s, m, pub_key_lst, ec=curve.secp256k1, hash=hs.sha256))

    r_point, signature, aggregated_key, proof = musig_distributed_with_key_verification(m, my_key,
                                                                                                      pub_key_lst,
                                                                                                      address_dict,
                                                                                                      hostname,
                                                                                                      port,
                                                                                                      ec=curve.secp256k1,
                                                                                                      complete_pub_keys_list=complete_pub_key_lst,
                                                                                                      restrictions=restriction)

    print(80 * '-')
    print(f'{r_point}')
    print(f'{signature}')
    print(f'{aggregated_key}')
    print(f'{proof}')

    pub_key_lst.append(my_key[1])
    # merkle_tree = merkle.build_merkle_tree(complete_pub_key_lst, sorted_keys=False, restrictions=restriction)
    merkle_tree = merkle.build_merkle_tree(pub_key_lst, complete_public_key_list=complete_pub_key_lst,restrictions=restriction)

    print('$' * 80)
    print(f'MERKLE TREE:\n{merkle_tree}')
    print('$' * 80)

    print('_'*80)
    print(f'VER:')
    result = musig_ver_with_key_verification(r_point, signature, m, proof, aggregated_key, merkle_tree[0],
                                             ec=curve.secp256k1, h_sig=hs.sha256, h_tree=hs.sha256)
    print(result)



def test40(restriction_flag):
    input('FIRE_40>')
    hostname, port = '127.0.0.1', 2439

    my_key = keystorage.import_keys('k2.pem')
    key2 = keystorage.import_keys('key2.pem')

    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('key90.pem')

    restriction = None
    if restriction_flag:
        restriction = [(my_key[1], key2[1], key3[1], key4[1])]


    key2 = (None, key2[1])
    key3 = (None, key3[1])
    key4 = (None, key4[1])

    addr2 = ('127.0.0.1', 2437)
    addr3 = ('127.0.0.1', 2438)
    addr4 = ('127.0.0.1', 2436)

    m = 'teste39826c4b39'

    address_dict = {str(key2[1]): addr2, str(key3[1]): addr3, str(key4[1]): addr4}
    pub_key_lst = [key2[1],key3[1],key4[1]]

    complete_pub_key_lst = [my_key[1], key2[1], key3[1], key4[1]]

    # R, s = musig_distributed(m, my_key, pub_key_lst, address_dict, hostname, port)
    # #os.system('clear')
    # print(f'\nR: {R}\ns: {s}\n')
    #
    # pub_key_lst.append(my_key[1])
    # #adicionar a chave do assinanete a list de chaves publicas
    # print(musig_ver(R, s, m, pub_key_lst, ec=curve.secp256k1, hash=hs.sha256))

    r_point, signature, aggregated_key, proof = musig_distributed_with_key_verification(m, my_key,
                                                                                                      pub_key_lst,
                                                                                                      address_dict,
                                                                                                      hostname,
                                                                                                      port,
                                                                                                      ec=curve.secp256k1,
                                                                                                      complete_pub_keys_list=complete_pub_key_lst,
                                                                                                      restrictions=restriction)

    print(80 * '-')
    print(f'{r_point}')
    print(f'{signature}')
    print(f'{aggregated_key}')
    print(f'{proof}')

    pub_key_lst.append(my_key[1])
    # merkle_tree = merkle.build_merkle_tree(complete_pub_key_lst, sorted_keys=False, restrictions=restriction)
    merkle_tree = merkle.build_merkle_tree(pub_key_lst, complete_public_key_list=complete_pub_key_lst,restrictions=restriction)

    print('$' * 80)
    print(f'MERKLE TREE:\n{merkle_tree}')
    print('$' * 80)

    # result = musig_ver_with_key_verification(r_point, signature, m, pub_key_lst, aggregated_key, proof,root = merkle_tree[0],
    #                                          complete_pub_key_lst=complete_pub_key_lst,
    #                                          restrictions=restriction,
    #                                          ec=curve.secp256k1)

    result = musig_ver_with_key_verification(r_point, signature, m, proof, aggregated_key, merkle_tree[0],
                                             ec=curve.secp256k1, h_sig=hs.sha256, h_tree=hs.sha256)
    print(f'RESULT: {result}')


def main():
    restriction_flag = False
    print(len(sys.argv))
    if len(sys.argv) > 2:
        if sys.argv[2] == '1':
            restriction_flag = True
    if sys.argv[1] == '1':
        os.system('clear')
        test1()
    elif sys.argv[1] == '2':
        os.system('clear')
        test2()
    elif sys.argv[1] == '3':
        os.system('clear')
        test3()
    elif sys.argv[1] == '10':
        os.system('clear')
        test10(restriction_flag)
    elif sys.argv[1] == '20':
        os.system('clear')
        test20(restriction_flag)
    elif sys.argv[1] == '30':
        os.system('clear')
        test30(restriction_flag)
    elif sys.argv[1] == '40':
        os.system('clear')
        test40(restriction_flag)
    else:
        os.system('clear')
        test4()


if __name__ == "__main__":
    main()