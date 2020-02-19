"""
СТАРАЯ ВЕРСИЯ НАХОЖДЕНИЯ НОМЕРОВ, ДО ТОГО КАК МНЕ МИРАББАС СКИНУЛ НОВУЮ
"""

import numpy as np
import cv2
import imutils
import pytesseract as tes
import os
import time
import imutils
import random
import math

"""
КАК ДОЛЖНО РАБОТАТЬ

РАСПОЗНАЕТСЯ ОДНА ФОТКА
ЕСЛИ НА НЕЙ С ПЕРВОЙ ПОПЫТКИ НАШЕЛСЯ КОНТУР НОМЕРА И РАСПОЗНАЛСЯ ТЕКСТ НА НЕМ, ТО ВСЕ ЭТО СОХРАНЯЕТСЯ КУДА НАДО
ЕСЛИ НА НЕЙ НАШЕЛСЯ КОНТУР, НО В НЕМ НЕ НАШЛОСЬ ТЕКСТА, ТО ПЕРЕКЛЮЧАЕМСЯ НА ДРУГУЮ ПАПКУ, В КОТОРОЙ ЛЕЖАТ КОНТУРЫ
С ДРУГИМ КОЛИЧЕСТВОМ УГЛОВ ( НЕ ТЕМ, КОТОРОЕ УКАЗАЛИ ИЗНАЧАЛЬНО )
ТАМ ТОЖЕ КАЖДАЯ ФОТКА ОБРАБАТЫВАЕТСЯ И ПЕРЕПРИСВАИВАЕТСЯ ТЕКСТ
ЕСЛИ ПОСЛЕ ОБРАБОТКИ ВСЕХ ФОТОК ТЕКСТА НЕ ОБНАРУЖЕНО, ТО И НА НАЧАЛЬНОЙ ФОТКЕ ЕГО 


"""

"""
Эта функция создает "маски" которые фильтруют все пиксели, оставляя только те, цвет которых
указан

"""
def apply_filter(img):
    #нужно перевести картинку в формат HLS
    image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


    # маска для белого цвета в формате HLS!!!
    # эти числа получаю через прогу set_filter
    #                H   S    V
    lower = np.uint8([0, 200, 0])
    upper = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(image, lower, upper)

    #маска для серого цвета
    lower = np.uint8([0,0,141])
    upper = np.uint8([210,47,255])
    gray_mask = cv2.inRange(image, lower, upper)

    """
    Теперь с помощью операции дизъюнкции мы объеденяем все маски в одну
    В итоге, при наложении этой маски на фотографии, отсеятся все пиксели, кроме
    белых пока что (смотри return)
    Именно этими цветами обычно рисуются полосы парковки и госномера
    """
    mask = cv2.bitwise_or(white_mask, gray_mask)
    return mask


"""
Функция обрабатывает на наличие текста все фотки из указанной папки
"""
def search_in_folder(path, NumberPlateCnt):
    all_texts = []
    for idx, cnt in NumberPlateCnt.items():
        text = tes.image_to_string(path + str(idx) + ".jpg", lang="rus")  # на каждой фотке из папки ищем текст
        text = format_text(text)  # убираем мусор из текста
        if text in all_texts:  # если текст уже был найден (то есть вырезалось два одинаковых контура), то пропускаем его
            pass
        else:
            all_texts.append(text)  # добавляем текст с конкретной картинки в общий массив
    return all_texts


"""
Функция для форматирования текста и удаление мусора из него
"""
def format_text(text):
    invalid_symbols = ["-", ":", ".", "'", "`"]
    for symbol in text:
        # если символ нижнего регистра, то переводим в верхний
        text = text.replace(symbol, symbol.upper())
        # если увидели пробел - убираем
        if symbol == " ":
            text = text.replace(symbol, "")
        # если в номере были распознаны какие-то символы, кроме букв и цифр, они отбрасываются
        if symbol in invalid_symbols:
            print("Removing invalid symbol: ", symbol)
            text = text.replace(symbol, "")
    return text


"""
Функция удаляет из массива контуров все с очень маленькой площадью
"""
def sort_by_square(image, cnts):
    width, height = image.shape[:2]
    new_cnts = []
    square = width * height
    min_area = 0.0002 * square # минимальная площадь контура как часть от общей
    print("Minimum required contour area = ", min_area)
    for cnt in cnts:
        if cv2.contourArea(cnt) >= min_area:
            new_cnts.append(cnt)
        else:
            pass
    return new_cnts

"""
Функция находит расстояние между двумя точками
На вход подаются координаты точек через запятую
"""
def find_distance(x_1, y_1, x_2, y_2):
    distance = math.sqrt(abs((x_2 - x_1)**2 + (y_2 - y_1)**2))
    return distance




"""
Функция сравнивает два бокса, учитывая небольшую погрешность. Так как боксы по значениям не всегда одинаковы, но 
визуально это одини и тот же контур. Такие надо исключать
"""
def compare(box_1, box_2):
    print("Activate 'compare()' function")
    same = False # переключатель
    x_1_1 = box_1[0][0]
    y_1_1 = box_1[0][1]
    x_1_2 = box_1[1][0]
    y_1_2 = box_1[1][1]

    x_2_1 = box_2[0][0]
    y_2_1 = box_2[0][1]
    x_2_2 = box_2[1][0]
    y_2_2 = box_2[1][1]

    print("first box is:")
    print(x_1_1, " ", y_1_1, " ", x_1_2, " ", y_1_2)
    print("second box is: ")
    print(x_2_1, " ", y_2_1, " ", x_2_2, " ", y_2_2)

    min_distance = 10

    print("first distance = ", find_distance(x_1_1, y_1_1, x_2_1, y_2_1))
    print("second distance = ", find_distance(x_1_2, y_1_2, x_2_2, y_2_2))


    cond_1 = (find_distance(x_1_1, y_1_1, x_2_1, y_2_1) < min_distance)  # расстояние между верхними левыми углами
    cond_2 = (find_distance(x_1_2, y_1_2, x_2_2, y_2_2) < min_distance)  # расстояние между правыми нижниму углами

    if (cond_1 is True) and (cond_2 is True):  # если расстояние мужду обоими углами контуров меньше заданного - они примерно одинаковы
        print("Boxes are close to each other")
        same = True
        return same
    else:
        print("Boxes are way too far")

    return same

"""
Функция удаляет контуры типа [[[150,220]]], то есть очень короткие
"""
def delete_short(contours):
    long_cnts = []
    for i,cnt in enumerate(contours):
        if len(cnt) >= 4:
            long_cnts.append(cnt)  # если у контура 2 угла (по факту 4), то добавляем его в новый массив
        else:
            print("Contour №{}".format(i), " is too short (", str(len(cnt)), "), ignore it.")
    return long_cnts


"""
Функция удаляет из массива контуров одинаковые контуры
(да, такое может быть)
"""
def only_different(contours):
    cnt_box = {}  # словарь (номер контура-бокс)
    for i, c in enumerate(contours):
        rect = cv2.minAreaRect(c)  # это типа tuple
        # print("rect = ", rect)
        box = cv2.boxPoints(rect)  # поиск четырех вершин прямоугольника
        # print("box = ", box)
        box = np.int0(box)  # округление координат
        #print("tuple box = ", box, "*******")
        box = list(box)  # переводим из формала tuple внешний массив
        #print("array box = ", box, "*******")
        for j in range(len(box)):
            box[j] = list(box[j])  # переводим из формата tuple внутренние подмассивы

        cnt_box[i] = box  # заносим в словарь
        #print("cnt_box[i] = ", box)

    for i, box in cnt_box.items():  #снова проходим по словарю для сравнения
        for j in cnt_box.keys():  # от i и до конца массива ключей
            # j должна быть больше i, так как мы рассматриваем все контуры, которые в массиве находятся правее i-ого
            # j должны быть меньше длинны контуров, иначе будет ошибка
            if (j > i) and (cnt_box[j] is not None) and (j < len(contours)): # он может быть None, если мы удалил соответствующий контур (см. строка 195)
                another_box = cnt_box[j]  # выбираем для сравнения другой бокс

                #for i,cnt in enumerate(contours):
                  #  print(len(cnt), "\n")

                # если у боксов равное количество углов, то можем сравнить
                if len(box) == len(another_box):
                    if compare(box, another_box) is True:
                        print("j = ", j, "i = ", i)

                        # для проверки выведем словарь на экран
                        for key,value in cnt_box.items():
                            print(key, ": ", value)

                        print("Found similar contours...Deleting ONE of them")
                        # оказывается, некоторые контуры могут быть типа [[[150,200]]], на них вылетает ошибка их нельзя обрабатывать
                        print("Contours ", cnt_box[i], " and ", cnt_box[j], " are similar")
                        to_delete = cnt_box[j]
                        #проверим есть ли контур в контурах
                        if (to_delete in contours):
                            print("ok")
                        print("to_delete = ", to_delete, " .")
                        # to_delete неправильно определяется, его нет в контурах, если их распечатать просто

                        contours.remove(to_delete)# почему не удаляет???
                          # если нашли одинаковые контуры, то сразу из массива удаляем все, кроме первого
                        # НАДО УДАЛЯТЬ НЕ ТОЛЬКО ИЗ МАССИВА, НО И ИЗ СЛОВАРЯ, ПОТОМУ ЧТО ЕСЛИ МЫ ДОПУСТИМ УДАЛИМ 7-ОЙ ЭЛЕМЕН
                        # МАССИВА, ТО КЛЮЧ "7" ВСЕ РАВНО ОСТАНЕТСЯ В СЛОВАРЕ, А КОГДА ОН НАТКЕТСЯ НА НЕГО ЕЩЕ РАЗ, ТО НЕ
                        # СМОЖЕТ НАЙТИ СООТВЕТСТВУЮЩИЙ ЭЛЕМЕНТ МАССИВА
                        # НО УДАЛИТЬ ИЗ СЛОВРЯ МЫ НЕ МОЖЕМ. ЛЕГЧЕ ПРОСТ ПРИРАВНЯТЬ К ПУСТОМУ МЕСТУ И ПОСТАВИТЬ ПРОВЕРКУ
                        cnt_box[j] = None
                        print("Deleted it from array and dictionary")
                        print("Now the number of contours is ", str(len(contours)))
    return contours  # возвращаем массив без повторений


"""
Функция рисует все контуры случайными цветами
Третьим и четверты аргументом указывается количество изгибов контура
"""
def colored_contours(contours, img, min_dots = 1, max_dots = 10):
    for c in contours:
        red = random.randint(0,255)
        green = random.randint(0,255)
        blue = random.randint(0,255)

        cv2.drawContours(img, [c], -1, (red, green, blue), 3)

    return img



"""
Функция удаляет все картинки из папки после работы
"""
def clear(path):
    for file in os.listdir(path):
        os.remove(path + file)

"""
Функция возвращает текст, полученные с госномера и путь к вырезанному госномеру
"""
def process(img_path, show_steps):

    detect_text = True # изначально переключатель распознавания текста на положительной клемме, а потом, если не найдем контур, то выключим

    tes.pytesseract.tesseract_cmd = r"C:\CREESTL\Programming\PythonCoding\semestr_3\tesseract\tesseract.exe"

    #чтение картинки
    image = cv2.imread(img_path)

    image = imutils.resize(image, width = 800)

    #изменяем размеры картинки
    image = imutils.resize(image, width = 800)

    #вывод на экран оригинальной картинки
    if show_steps:
        cv2.imshow("original_image", image)

    # убираем шумы с фото
    image = cv2.bilateralFilter(image, 11, 17, 17)
    if show_steps:
        cv2.imshow("no_noize", image)

    gray = apply_filter(image)
    if show_steps:
        cv2.imshow("filtered_img", gray)

    #убираем шумы с фото
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    if show_steps:
        cv2.imshow("no_noize", gray)

    #находим грани
    edged = cv2.Canny(gray, 170, 200)
    if show_steps:
        cv2.imshow("edges", edged)

    #находим контуры среды граней
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    #print(list(cnts))

    print("First number of contours is ", str(len(cnts)))

    #создаем копию оригинальной картинки, чтобы на ней рисовать все контуры
    img1 = image.copy()
    cv2.drawContours(img1, cnts, -1, (0, 255, 0), 2)
    if show_steps:
        cv2.imshow("all_contours", img1)

    #удаляем все контуры, которые являются точками
    cnts = delete_short(cnts)

    #удаляем повторяющиеся контуры
    cnts = only_different(cnts)

    #убирем все контуры малой площади
    cnts = sort_by_square(image, cnts)

    print("Final number of contours is ", str(len(cnts)))
    print("Here they are:")
    for cnt in cnts:
        print(cnt)

    #рисуем все контуры разным цветом
    img11 = image.copy()
    colored_img = colored_contours(cnts, img11, 6, 9)
    cv2.imshow("colored_cnts", colored_img)

    #фильтруем контуры по их площади от большего к меньшему
    cnts = sorted(cnts, key=lambda cnt: cv2.contourArea(cnt), reverse = True)

    #NumberPlateCnt = None #контур пока что пустой
    NumberPlateCnt = {}  # словарь idx - сам контур

    #топ 30 контуров
    img2 = image.copy()
    cv2.drawContours(img2, cnts, -1, (0, 255, 0), 2)
    if show_steps:
        cv2.imshow("top_30_cnts", img2)


    img3 = image.copy()
    #проверяем все контуры и находим тот, который наиболее похож на плашку номера
    idx = 1
    for i,c in enumerate(cnts):
        perimeter = cv2.arcLength(c, True)
        #эпсилон - максимальное расстояние от настоящего угла на картинке и его "предсказания"
        #True отвечает за замыкание первой и последней точек контура
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(c, epsilon, True)
        print("for {} contour approx = ".format(i), str(len(approx)))

        #рисуем предполагаеме изгибы линий
        cv2.drawContours(img3, approx, -1, (0, 255, 0), 3)
        cv2.imshow("approx", img3)

        if len(approx) == 4:
            NumberPlateCnt[idx] = approx # в словарь помещаем контур, если его число углов равно заданному
            #вырезаем этот контур и храним его в отдельном месте
            x, y, w, h = cv2.boundingRect(c) # находим координаты плашки
            new_img = image[y:y+h, x:x+w]  # создаем новую картинку
            cv2.imwrite("txt_from_imgs/correct_cnts/" + str(idx) + ".jpg", new_img)  # сохраняем новую картинку вырезанного номера

            idx += 1

        # если изгибов контура не 7, то я просто вырезаю эти контуры и сохряняю в отдельную папку
        else:
            x, y, w, h = cv2.boundingRect(c)
            new_img = image[y:y+h, x:x+w]
            cv2.imwrite("txt_from_imgs/other_cnts/" + str(len(approx)) + ".jpg", new_img)


        idx += 1

        #после заверешения функции у нас есть две папки с подходящими и левыми контурами


    if NumberPlateCnt is not None: # если существует хотя бы один контур
        # то мы переходим в папку с фотками подходящих контуров и в ней пытаемся найти текст
        cropped_img_folder = "txt_from_imgs/correct_cnts/"
        all_texts = search_in_folder(cropped_img_folder, NumberPlateCnt)  # это все тексты, найденные на подходящих контурах
        # а также необходимо нарисовать все контуры на исходной фотке, чтобы понять правильно ли они найдены
        img3 = image.copy()
        for cnt in NumberPlateCnt.values():
            cv2.drawContours(img3, [cnt], -1, (0,255,0), 2)
        if show_steps:
            cv2.imshow("correct_cnts", img3)

    else:
        all_texts = []
        print("No text found in the RIGHT contours!!!")  #все тексты так и оставляем пустым массивом

    cv2.waitKey()

    return all_texts



#########################################################################################################################

show_steps = False

text = None
all_texts = process(r"C:\CREESTL\Programming\PythonCoding\semestr_3\OpenCV_3_KNN_Character_Recognition_Python-master\pics\paint.jpg", True)

if all_texts[0] == '':
    second_try_texts = []
    """
    В идеале у номера 4 угла. Но если нашел не 4 угла, то он вырезает этот контур и сохраняет в папку other_cnts
    Допустим, он нашел контур с 4 углами, но он оказался не номером. Тогда text == "" и нужно проанализировать все
    побочные вырезанные контуры.
    """
    print("trying to analyze contours with another number of angles:")
    for filename in os.listdir(r"C:\CREESTL\Programming\PythonCoding\semestr_3\txt_from_imgs\other_cnts\\"):
        print(r"Processing image: C:\CREESTL\Programming\PythonCoding\semestr_3\txt_from_imgs\other_cnts\\" + filename)
        text = process("C:\\CREESTL\\Programming\\PythonCoding\\semestr_3\\txt_from_imgs\\other_cnts\\" + filename, True)
        if (text is not None) and (text != []):
            second_try_texts.append(text)
            print("text found:", text)

    """
    Если и после обработки всех других контуров, текст был не найден, то выдается сообщение об этом
    """
    if text == []:
        print("THERE IS NO TEXT ON THE IMAGE!!!")
else:
    print("RESULTS:")
    for text in all_texts:
        text = format_text(text)
        print(text)


# очищаем директории после работы с ними
clear("C:/CREESTL/Programming/PythonCoding/semestr_3/txt_from_imgs/correct_cnts/")
clear("C:/CREESTL/Programming/PythonCoding/semestr_3/txt_from_imgs/other_cnts/")

cv2.destroyAllWindows()