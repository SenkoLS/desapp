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

        # Параметры для подсчета лавинного эффекта
        self.list_count_dif_bit_for_text_block = list()
        self.list_count_dif_bit_for_key_block = list()

        if padding and action == cf.ENCRYPT:
            self.add_padding()
        elif len(self.text) % 8 != 0:
            raise "Размер текста должен быть кратным 8"

        # Создаем ключи
        self.keys = self.get_keys(False)

        # Создаем ключи для расчета лавинного эффекта
        if cf.AVALANCHE_KEY:
            self.keys_ = self.get_keys(True)

        text_blocks = self.nsplit(self.text, 8)
        result = list()

        for block in text_blocks:
            block = self.string_to_bit_array(block)
            tmp = None
            tmp_ = None
            left_ = None
            right_ = None

            if cf.AVALANCHE_TEXT:
                block_ = self.invert_bit_in_block(block, self.number_bit_text)
                block_ = self.permut(block_, cf.IP)
                left_, right_ = self.nsplit(block_, 32)
                tmp_ = None

            if cf.AVALANCHE_KEY:
                block_ = list(block)
                block_ = self.permut(block_, cf.IP)
                left_, right_ = self.nsplit(block_, 32)
                tmp_ = None

            # Первоначальная перестановка в блоке в соответствии с матрицей IP
            block = self.permut(block, cf.IP)
            left, right = self.nsplit(block, 32)

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

                # Подсчет изменений количества изм-ся бит при измен-ии 1 бита исх текста
                if cf.AVALANCHE_TEXT:
                    d_e_ = self.permut(right_, cf.E)
                    if action == cf.ENCRYPT:
                        tmp_ = self.xor(self.keys[i], d_e_)
                    else:
                        tmp_ = self.xor(self.keys[15 - i], d_e_)
                    tmp_ = self.substitute(tmp_)
                    tmp_ = self.permut(tmp_, cf.P)
                    tmp_ = self.xor(left_, tmp_)
                    left_ = right_
                    right_ = tmp_
                    count_dif_bit = self.count_diff_bit_in_round(right + left, right_ + left_)
                    self.list_count_dif_bit_for_text_block.append(count_dif_bit)

                if cf.AVALANCHE_KEY:
                    d_e_ = self.permut(right_, cf.E)
                    if action == cf.ENCRYPT:
                        tmp_ = self.xor(self.keys_[i], d_e_)
                    else:
                        tmp_ = self.xor(self.keys_[15 - i], d_e_)
                    tmp_ = self.substitute(tmp_)
                    tmp_ = self.permut(tmp_, cf.P)
                    tmp_ = self.xor(left_, tmp_)
                    left_ = right_
                    right_ = tmp_
                    count_dif_bit = self.count_diff_bit_in_round(right + left, right_ + left_)
                    self.list_count_dif_bit_for_text_block.append(count_dif_bit)

            # Мердж частей и завершающая перестановка
            result += self.permut(right + left, cf.IP_1)
            # Выключаем сбор данных по лавинному эффекту (прогон только для одного блока шифрования)
            cf.AVALANCHE_TEXT = False
            cf.AVALANCHE_KEY = False
        final_res = self.bit_array_to_string(result)

        # Расчет времени работы алгоритма
        self.time_spent = time.time() - self.start_alg

        if padding and action == cf.DECRYPT:
            # Возвращаем дешифроваанную строку с предварительным удалением отступов PKCS5
            return self.remove_padding(final_res)
        else:
            return final_res

    def count_diff_bit_in_round(self, block1, block2):
        count_dif_bit = 0
        for one_tuple in zip(block1, block2):
            if one_tuple[0] != one_tuple[1]:
                count_dif_bit += 1
        return count_dif_bit

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
    def get_keys(self, flag):
        keys = []
        left_ = None
        right_ = None
        key = self.string_to_bit_array(self.password)
        # Флаг инвертирования бита в ключе (True - инвертировать нужный бит)
        if flag:
            key = self.invert_bit_in_block(key, self.number_bit_key)
        # Первоначальная перестановка ключа по матрице G
        key = self.permut(key, cf.G)
        # Разбивка ключа пополам
        left, right = self.nsplit(key, 28)
        for i in range(16):
            left, right = self.shift(left, right, cf.SHIFT[i])
            merged_key = left + right
            # Завершающая обработка ключа по матрице H
            keys.append(self.permut(merged_key, cf.H))
        return keys

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
            # Получить значение строки бит для 1 байт
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

    def set_num_bit(self, number_bit_key, number_bit_text, key, text):
        if key == 1:
            cf.AVALANCHE_KEY = True
            cf.AVALANCHE_TEXT = False
        elif text == 1:
            cf.AVALANCHE_KEY = False
            cf.AVALANCHE_TEXT = True
        else:
            cf.AVALANCHE_KEY = False
            cf.AVALANCHE_TEXT = False

        self.number_bit_key = number_bit_key
        self.number_bit_text = number_bit_text

    def get_avalanche_effect_param(self):
        round_e = [x for x in range(1, 17)]
        return [round_e, self.list_count_dif_bit_for_text_block]

    def invert_bit_in_block(self, block, type_number_bit):
        new_block = list(block)
        if new_block[type_number_bit - 1] == 1:
            new_block[type_number_bit - 1] = 0
        else:
            new_block[type_number_bit - 1] = 1
        return new_block
