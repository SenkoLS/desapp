import time
from ConfDes import ConfDes as cf


# Класс, предоставляющий интерфейсы реализации шифрования и дешифрования алгоритма DES
class Des():
    def __init__(self):
        self.password = None
        self.text = None
        self.keys = list()

    def encrypt(self, key, text, padding=False):
        return self.run(key, text, cf.ENCRYPT, padding)

    def decrypt(self, key, text, padding=False):
        return self.run(key, text, cf.DECRYPT, padding)

    def run(self, key, text, action=cf.ENCRYPT, padding=False):
        if len(key) < 8:
            raise "Некорректная длина ключа!"
        elif len(key) > 8:
            key = key[:8]

        self.password = key
        self.text = text

        self.start_alg = time.time()

        if padding and action == cf.ENCRYPT:
            self.add_padding()
        elif len(self.text) % 8 != 0:
            raise "Размер текста должен быть кратным 8"

        # Создаем ключи
        self.get_keys()
        text_blocks = self.nsplit(self.text, 8)
        result = list()
        for block in text_blocks:
            block = self.string_to_bit_array(block)
            # Первоначальная перестановка в блоке в соответствии с матрицей IP
            block = self.permut(block, cf.IP)
            left, right = self.nsplit(block, 32)
            tmp = None
            for i in range(16):
                # Расширяем правую часть с 32 битной последовательности до 48 битной последовательности
                d_e = self.permut(right, cf.E)
                if action == cf.ENCRYPT:
                    tmp = self.xor(self.keys[i], d_e)
                else:
                    tmp = self.xor(self.keys[15 - i], d_e)
                tmp = self.substitute(tmp)
                tmp = self.permut(tmp, cf.P)
                tmp = self.xor(left, tmp)
                left = right
                right = tmp
            # Мердж частей и завершающая перестановка
            result += self.permut(right + left, cf.IP_1)
        final_res = self.bit_array_to_string(result)
        # Расчет времени работы алгоритма
        self.time_spent = time.time() - self.start_alg
        if padding and action == cf.DECRYPT:
            # Возвращаем дешифроваанную строку с предварительным удалением отступов PKCS5
            return self.remove_padding(final_res)
        else:
            return final_res

    # Замена байтов в соответствии с матрицами S
    def substitute(self, array_bytes):
        subblocks = self.nsplit(array_bytes, 6)
        result = list()
        for i in range(len(subblocks)):
            block = subblocks[i]
            # Получаем строку с 1 и 6 битом
            row = int(str(block[0]) + str(block[5]), 2)
            # Получить столбец с битами 2-5
            column = int(''.join([str(x) for x in block[1:][:-1]]), 2)
            # Получаем значение из матрицы S для соответствующего раунда i
            value = cf.S[i][row][column]
            bin = self.get_bin_as_str(value, 4)
            result += [int(x) for x in bin]
        return result

    # Перестановка элементов блока в соответствии с матрицей
    def permut(self, block, matrix):
        return [block[x - 1] for x in matrix]

    # Поэлементный XOR элементов двух списков
    def xor(self, t1, t2):
        return [x ^ y for x, y in zip(t1, t2)]

    # Получение всех ключей в итоговый массив
    def get_keys(self):
        self.keys = []
        key = self.string_to_bit_array(self.password)
        # Первоначальная перестановка ключа по матрице G
        key = self.permut(key, cf.G)
        # Разбивка ключа пополам
        left, right = self.nsplit(key, 28)
        for i in range(16):
            left, right = self.shift(left, right, cf.SHIFT[i])
            merged_key = left + right
            # Завершающая обработка ключа по матрице H
            self.keys.append(self.permut(merged_key, cf.H))

    # Сдвигает список заданных значений
    def shift(self, left, right, n):
        return left[n:] + left[:n], right[n:] + right[:n]

    # Добавление отступа к даннм в соответствии со спецификацией PKCS5
    # Примеры кода и дополнения (http://www.herongyang.com/Cryptography/DES-JDK-What-Is-PKCS5Padding.html)
    # If numberOfBytes(clearText) mod 8 == 7, PM = M + 0x01
    # If numberOfBytes(clearText) mod 8 == 6, PM = M + 0x0202
    # If numberOfBytes(clearText) mod 8 == 5, PM = M + 0x030303
    # ...
    # If numberOfBytes(clearText) mod 8 == 0, PM = M + 0x0808080808080808
    def add_padding(self):
        add_size = 8 - (len(self.text) % 8)
        self.text += add_size * chr(add_size)

    # Добавление пробелов в конец текста (только для незашифрованного текста)
    def add_spaces_to_end_file(self):
        add_size = 8 - (len(self.text) % 8)
        self.text += add_size * chr(32)

    # Удаление отступов у текста
    def remove_padding(self, data):
        size_pad = ord(data[-1])
        return data[:-size_pad]

    # Преобразование строки в список бит
    def string_to_bit_array(self, text):
        array = list()
        for char in text:
            # Получить значение символа (1 байт)
            binval = self.get_bin_as_str(char, 8)
            # Добавление бит в окончательный список
            array.extend([int(x) for x in list(binval)])
        return array

    # Преобразовывает список бит в строку
    def bit_array_to_string(self, array):
        res = ''.join([chr(int(y, 2)) for y in [''.join([str(x) for x in _bytes]) for _bytes in self.nsplit(array, 8)]])
        return res

    # Возвращает двоичное значение в виде строки заданного размера
    def get_bin_as_str(self, val, bitsize):
        binstr = bin(val)[2:] if isinstance(val, int) else bin(ord(val))[2:]
        if len(binstr) > bitsize:
            raise "Двоичное значение больше ожидаемого размера"
        while len(binstr) < bitsize:
            binstr = "0" + binstr
        return binstr

    # Разбивает список на подсписки размера "n"
    def nsplit(self, s, n):
        return [s[k:k + n] for k in range(0, len(s), n)]
