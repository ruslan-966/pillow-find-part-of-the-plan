from PIL import Image
import numpy as np
import time
from params_of_program import *


def two_for_high_y(x_, y_, array):
    for j_ in range(0, y_):  # Пробегаем по координате y
        for i_ in range(0, x_):  # Пробегаем по коорденате x
            if not np.array_equal(array[j_][i_], [255, 255, 255]):
                return j_


def two_for_low_y(x_, y_, array):
    for j_ in range(y_ - 1, -1, -1):  # Пробегаем по координате y
        for i_ in range(0, x_):  # Пробегаем по коорденате x
            if not np.array_equal(array[j_][i_], [255, 255, 255]):
                return j_


def two_for_left_x(x_, y_, array):
    for i_ in range(0, x_):       # Пробегаем по координате x
        for j_ in range(0, y_):   # Пробегаем по коорденате y
            if not np.array_equal(array[j_][i_], [255, 255, 255]):
                return i_


def two_for_right_x(x_, y_, array):
    for i_ in range(x_ - 1, -1, -1):        # Пробегаем по координате x
        for j_ in range(0, y_):             # Пробегаем по коорденате y
            if not np.array_equal(array[j_][i_], [255, 255, 255]):
                return i_


def cropped_img(img_file):
    with Image.open(img_file) as img:
        img.load()

    (x, y) = img.size  # Через атрибут size получаем кортеж с двумя элементами (размер изображения по x и y)

    img_array = np.asarray(img)
    # print(img_array[1][1])
    # Образаем план до первого черного пикселя в строке сверху, справа, снизу, слева:
    left_x = two_for_left_x(x, y, img_array)
    right_x = two_for_right_x(x, y, img_array)
    high_y = two_for_high_y(x, y, img_array)
    low_y = two_for_low_y(x, y, img_array)
    return img.crop((left_x, high_y, right_x, low_y))


def cut_wind_by_size(img, x_len, y_len, dx, dy):
    (x, y) = img.size
    if (x < x_len + dx) or (y < y_len + dy):
        return None
    return img.crop((x_len, y_len, x_len + dx, y_len + dy))


def pic_detect(search_file, template_file, step=5):
    rgb1 = template_file.getpixel((0, 0))
    size_pic = search_file.size
    size_pic_tpl = template_file.size
    p_max = 0
    x_max = 0
    y_max = 0
    for y in range(size_pic[1] - size_pic_tpl[1]):
        for x in range(size_pic[0] - size_pic_tpl[0]):
            rgb0 = search_file.getpixel((x, y))
            br = False # Индикатор досрочного выхода из циклов, если картина не совпала.....
            if rgb0 == rgb1:        # Если первые пиксели совпали, то....
                count = 0
                count_pls = 0
                # Попиксельная сверка для 100% совпадения, в большинстве случаев это излишне
                for ii in range(0, size_pic_tpl[1]-1, step):
                    for ee in range(0, size_pic_tpl[0]-1, step):
                        count += 1
                        if search_file.getpixel((x+ee, y+ii)) == template_file.getpixel((ee+1, ii+1)):
                            count_pls += 1
                p = count_pls / count * 100
                if p > p_max:
                    p_max = p
                    x_max = x
                    y_max = y
                if p_max == 100.0:
                    return True, x_max, y_max, p_max
    return False, x_max, y_max, p_max


def find_piece_of_plan():
    start_time = time.time()
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(f"Время начала расчетов: {current_time}.")
    crop_big = cropped_img(INPUT_LIVING_ROOM_FILE)
    crop_small = cropped_img(INPUT_FINDING_ROOM_FILE)
    (cbs_x, cbs_y) = crop_big.size
    (css_x, css_y) = crop_small.size
    new_cbs_x = int(cbs_x / IMAGE_COMPRESSION_RATIO)
    new_cbs_y = int(cbs_y / IMAGE_COMPRESSION_RATIO)
    new_css_x = int(css_x / IMAGE_COMPRESSION_RATIO)
    new_css_y = int(css_y / IMAGE_COMPRESSION_RATIO)
    crop_big.thumbnail(size=(new_cbs_x, new_cbs_y))
    crop_small.thumbnail(size=(new_css_x, new_css_y))
    gray_crop_big = crop_big.convert("L")  # Grayscale
    img_crop_big = gray_crop_big.convert("1")
    gray_crop_small = crop_small.convert("L")
    img_crop_small = gray_crop_small.convert("1")
    (rez, x, y, p) = pic_detect(img_crop_big, img_crop_small, STEP)
    print("--- %s seconds ---" % (time.time() - start_time))
    if rez:
        print(f'Совпало. Координаты: х = {x * IMAGE_COMPRESSION_RATIO}, y = {y * IMAGE_COMPRESSION_RATIO}')
    else:
        print(f'Не совпало! Координаты лучшего совпадения: х = {x * IMAGE_COMPRESSION_RATIO}, '
              f'y = {y * IMAGE_COMPRESSION_RATIO}, %% лучшего совпадения: {p}')

    size = img_crop_big.size
    new_im = Image.new('RGB', (2 * size[0], 2 * size[1]), (250, 250, 250))

    new_im.paste(img_crop_big, (0, 0))
    new_im.paste(img_crop_small, (size[0], 0))
    img_crop_big.paste(img_crop_small, (x, y))
    new_im.paste(img_crop_big, (0, size[1]))

    new_im.save("merged_images.png", "PNG")
    new_im.show()

    return rez, x, y


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    find_piece_of_plan()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
