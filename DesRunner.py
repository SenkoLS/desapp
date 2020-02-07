import tkinter as tk
import datetime
from Des import Des
from tkinter import *
from tkinter import filedialog
import codecs


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.initMain()

    def initMain(self):
        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.open_file_image = tk.PhotoImage(file="open.png")
        self.save_file_image = tk.PhotoImage(file="save.png")
        self.open_key_image = tk.PhotoImage(file="key.png")
        self.encrypt_image = tk.PhotoImage(file="encrypt.png")
        self.decrypt_image = tk.PhotoImage(file="decrypt.png")

        key_frame = Frame(self)
        key_frame.pack(fill=X)
        key_lbl = Label(key_frame, text="Ключ:", width=15)
        key_lbl.pack(side=LEFT, padx=5, pady=5)
        self.key_entry = Entry(key_frame)
        self.key_entry.pack(fill=X, padx=5, expand=True)

        text_frame = Frame(self)
        text_frame.pack(fill=BOTH, expand=True)
        text_lbl = Label(text_frame, text="Текст файла:", width=15)
        text_lbl.pack(side=LEFT, anchor=N, padx=5, pady=5)
        self.txt = Text(text_frame, height=10)
        self.txt.pack(fill=BOTH, pady=5, padx=5, expand=True)

        chipered_frame = Frame(self)
        chipered_frame.pack(fill=BOTH, expand=True)
        chipered_lbl = Label(chipered_frame, text="Шифр/Текст", width=15)
        chipered_lbl.pack(side=LEFT, anchor=N, padx=5, pady=5)
        self.chipered_text_frame = Text(chipered_frame, height=10)
        self.chipered_text_frame.pack(fill=BOTH, pady=5, padx=5, expand=True)

        log_frame = Frame(self)
        log_frame.pack(fill=BOTH, expand=True)
        log_lbl = Label(log_frame, text="Лог:", width=15)
        log_lbl.pack(side=LEFT, anchor=N, padx=5, pady=5)
        self.log = Text(log_frame)
        self.log.pack(fill=BOTH, pady=5, padx=5, expand=True)

        btn_open_text_file_dialog = tk.Button(toolbar,
                                              text="Выбрать файл",
                                              command=self.open_file_dialog,
                                              bg="#d7d8e0",
                                              bd=0,
                                              compound=tk.BOTTOM,
                                              image=self.open_file_image)
        btn_open_text_file_dialog.pack(side=tk.LEFT, padx=5, pady=5)

        btn_open_key_file_dialog = tk.Button(toolbar,
                                             text="Выбрать ключ",
                                             command=self.open_key_dialog,
                                             bg="#d7d8e0",
                                             bd=0,
                                             compound=tk.BOTTOM,
                                             image=self.open_key_image)
        btn_open_key_file_dialog.pack(side=tk.LEFT, padx=5, pady=5)

        btn_encrypt = tk.Button(toolbar,
                                text="Шифровать",
                                command=self.btn_encryption_handler,
                                bg="#d7d8e0",
                                bd=0,
                                compound=tk.BOTTOM,
                                image=self.encrypt_image)
        btn_encrypt.pack(side=tk.LEFT, padx=5, pady=5)

        btn_decrypt = tk.Button(toolbar,
                                text="Дешифровать",
                                command=self.btn_decryption_handler,
                                bg="#d7d8e0",
                                bd=0,
                                compound=tk.BOTTOM,
                                image=self.decrypt_image)
        btn_decrypt.pack(side=tk.LEFT, padx=5, pady=5)

        btn_save_file_dialog = tk.Button(toolbar,
                                         text="Сохранить в файл",
                                         command=self.save_file_dialog,
                                         bg="#d7d8e0",
                                         bd=0,
                                         compound=tk.BOTTOM,
                                         image=self.save_file_image)
        btn_save_file_dialog.pack(side=tk.LEFT, padx=5, pady=5)

    def open_file_dialog(self):
        self.chipered_text_frame.delete("1.0", END)
        self.string_from_file = open(self.get_path_to_file_name(1), encoding="utf-8").read()
        self.txt.delete("1.0", END)
        self.txt.insert(END, self.string_from_file)

    def open_key_dialog(self):
        self.chipered_text_frame.delete("1.0", END)
        self.string_from_key = open(self.get_path_to_file_name(2), encoding="utf-8").read()
        self.key_entry.delete(0, END)
        self.key_entry.insert(END, self.string_from_key)

    def get_path_to_file_name(self, type):
        name = "Файл"
        if type == 2:
            name = "Ключ"
        root.filename = filedialog.askopenfilename(initialdir="/", title="Выберите " + name.lower() + ":",
                                                   filetypes=(("Text files", "*.txt"), ("all files", "*.*")))

        self.log.insert(END, str(str(datetime.datetime.now()) +
                                 " \r\n" +
                                 name +
                                 " " +
                                 root.filename +
                                 " загружен\r\n"
                                 "===================================================\r\n\r\n"))
        return root.filename

    def save_file_dialog(self):
        if self.type_saving_file == 1:
            text = self.ciphered_text

        if self.type_saving_file == 2:
            text = self.deciphered_text

        save_file_name = filedialog.asksaveasfilename(initialdir="/", title="Сохранить файл:",
                                                      filetypes=(("Text files", "*.txt"), ("all files", "*.*")))

        self.log.insert(END, str(str(datetime.datetime.now()) +
                                 " \r\n"
                                 "Файл " +
                                 save_file_name +
                                 " сохранен\r\n"
                                 "===================================================\r\n\r\n"))
        new_file = open(save_file_name, 'wb')
        new_file.write(str(text).encode('UTF-8'))
        new_file.close()

    def get_key_and_text_changes(self, key, text):
        key_e = self.key_entry.get()
        if key_e != key:
            key = key_e
        text_t = self.txt.get("1.0", END)
        if text_t != text:
            text = text_t
        return key, text[:len(text) - 1]

    def btn_encryption_handler(self):
        self.type_saving_file = 1
        key = self.string_from_key
        text = self.string_from_file
        des = Des()
        key, text = self.get_key_and_text_changes(key, text)
        self.ciphered_text = des.encrypt(key, text)
        self.time_spent = des.time_spent

        message = str(str(datetime.datetime.now()) +
                      "\r\nПроизведено шифрование."
                      "\r\nЗатраченное время: " +
                      str(self.time_spent) +
                      "\r\nВы можете сохранить шифрограмму в файл,"
                      "\r\nдля этого нажмите кнопку \"Сохранить в файл\""
                      "\r\n===================================================\r\n\r\n")
        self.log.insert(END, message)
        self.chipered_text_frame.delete("1.0", END)
        self.chipered_text_frame.insert(END, self.ciphered_text)

    def btn_decryption_handler(self):
        self.type_saving_file = 2
        key = self.string_from_key
        text = self.string_from_file
        des = Des()
        key, text = self.get_key_and_text_changes(key, text)
        self.deciphered_text = des.decrypt(key, text)
        self.time_spent = des.time_spent
        message = str(str(datetime.datetime.now()) +
                      "\r\nПроизведено дешифрование."
                      "\r\nЗатраченное время: " +
                      str(self.time_spent) +
                      "\r\nВы можете сохранить шифрограмму в файл,"
                      "\r\nдля этого нажмите кнопку \"Сохранить в файл\""
                      "\r\n===================================================\r\n\r\n")
        self.log.insert(END, message)
        self.chipered_text_frame.delete("1.0", END)
        self.chipered_text_frame.insert(END, self.deciphered_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title("Шифрование данных алгоритмом Des")
    root.geometry("800x700+300+45")
    root.resizable(False, False)
    root.mainloop()