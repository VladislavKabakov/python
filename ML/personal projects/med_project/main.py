import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer as Cv
from sklearn.metrics.pairwise import cosine_similarity as cs

translate_to_eng = {'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
                    'Ж': 'J', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
                    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
                    'Ф': 'F', 'Х': 'CH', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SH',
                    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'A', 'Ю': 'U', 'Я': 'YA'}
eng_letters = [_ for _ in range(ord('A'), ord('Z') + 1)]
rus_letters = [_ for _ in range(ord('А'), ord('Я') + 1)]
alphabet = eng_letters + rus_letters
cnt_vec = Cv(ngram_range=(2, 2), analyzer='char')
hash_table = {}
second_chance = []


def get_all_info(row_index):
    global Cli, Prod, Full, Group
    cli_text, cli_prod, full_text, ref_group = str(Cli[row_index]), str(Prod[row_index]), str(Full[row_index]), str(
        Group[row_index])
    sh_cli, sh_prod = find_words_in_text(cli_text), find_words_in_text(cli_prod)
    ref_name, ref_group = find_words_in_text(full_text), find_words_in_text(ref_group)
    return sh_cli, sh_prod, ref_name, ref_group, cli_text, full_text


def get_text(array):
    return ''.join(sorted(list(set(array))))


def clear(arr):
    return [pos for pos in arr if pos != '']


def get_new_nums(arr):
    new_arr = clear([''.join([s for s in str(num) if s in '123456789']) for num in arr])
    return set([int(num) for num in new_arr])


def get_abbreviation(words):
    return ''.join([word[0] for word in words])


def filter_words(inp_words):
    first_filter = ["ТБ" if word in ("ТАБ", "ТБ", "ТАБЛ", "ТАБЛЕТКИ") else word for word in inp_words]
    second_filter = ["ВНУТРЕНН" if word in ("ВН", "ВНУТ", "ВНУТР", "ОРАЛН") else word for word in first_filter]
    third_filter = ["НАРУЖН" if word in ("НАР", "НАРУЖ") else word for word in second_filter]
    fourth_filter = ["ПОРОШОК" if word in ("ПОР", "ПОРОШ") else word for word in third_filter]
    for word in fourth_filter:
        if "НЕОПР" in word:
            return ''
    return fourth_filter


def find_numbers_in_text(text):
    text = text.replace(',', '.')
    nums = re.findall(r'\d*\.\d+|\d+', text)
    return [float(num) for num in nums]


def find_figures_in_ref(text):
    figures = re.findall(r'[№N]\s?\d*', text)
    return [int(f.replace(' ', '0').replace('№', '0').replace('N', '0')) for f in figures]


def find_figures_in_sh(text):
    text = text.replace('N', '№').replace('X', '№')
    figures = re.findall(r'[№]\s*\d*', text)
    return [int(f.replace(' ', '0').replace('№', '0').replace('N', '0')) for f in figures]


def find_extra_fg(txt):
    numbs = re.findall(r'[N]\s*\d*\s*[X]\s*\d*', txt)
    return find_numbers_in_text([n.replace(' ', '') for n in numbs][0]) if len(numbs) > 0 else []


def find_words_in_text(st):
    words = clear(''.join([sym if ord(sym) in alphabet else ' ' for sym in st]).split(' '))
    filtered_words = filter_words(words)
    return [''.join([translate_to_eng[sym] if ord(sym) in rus_letters else sym for sym in word]) for word in
            filtered_words if len(word) > 1]


def find_similarity(word1, word2):
    return cs(np.array(cnt_vec.fit_transform([word1, word2]).toarray()))[0][1]


def similar_word_exists(shop_wds, to_find):
    for word in shop_wds:
        if find_similarity(to_find, word) > 0.23:
            return True
    return False


def check_type(sh_name, ref_name):
    if (("VNUTRENN" in sh_name or "POROSHOK" in sh_name) and ("NARUJN" not in sh_name) and ("NARUJN" in ref_name)) or (
            ("VNUTRENN" in sh_name or "POROSHOK" in ref_name) and ("NARUJN" in sh_name) and (
            "NARUJN" not in ref_name)):
        return 0
    return 1


def numbers_comparison(sh_text, ref_text):
    shop_nums, ref_nums = find_numbers_in_text(sh_text), find_numbers_in_text(ref_text)
    if (len(shop_nums) > 0) and (len(ref_nums) > 0):
        ref_figures = find_figures_in_ref(ref_text)
        sh_figures = find_extra_fg(sh_text) if len(find_extra_fg(sh_text)) > 0 else find_figures_in_sh(sh_text)
        if (len(ref_figures) > 0) and (len(sh_figures) > 0):
            sh_curr = int(sh_figures[0]) if len(sh_figures) == 1 else int(sh_figures[0] * sh_figures[1])
            fml = 0.6 if sh_curr == int(ref_figures[0]) else 0
        else:
            fml = 1
        shop_nums = set(shop_nums).difference(set(ref_figures)).difference(set(sh_figures))
        ref_nums = set(ref_nums).difference(set(ref_figures)).difference(set(sh_figures))
        if (len(shop_nums) > 0) and (len(ref_nums) > 0):
            shop_nums, ref_nums = get_new_nums(shop_nums), get_new_nums(ref_nums)
            nml = 1.4 if len(shop_nums.intersection(ref_nums)) >= min(len(shop_nums), len(ref_nums)) / 2 else 0
        else:
            nml = 1
        return (fml + nml) / 2
    return 1


def name_comparison(sh_name, ref_name, sh_text, ref_text):
    key_name = ref_name[0]
    s_name, r_name = get_text(sh_name), get_text(ref_name)
    if numbers_comparison(sh_text, ref_text) > 0:
        name_similarity = find_similarity(s_name, r_name)
        if (name_similarity > 0.3) and (check_type(sh_name, ref_name)):
            return 1
        else:
            if similar_word_exists(sh_name, key_name):
                return 1
            return 0
    return 0


def full_comparison(s_cli, s_prod, r_name, r_group, s_text, r_text, tab_row):
    global hash_table, second_chance
    if name_comparison(s_cli, r_name, s_text, r_text) == 0:
        return 0
    if (len(r_group) == 0) or ((len(r_group) > 0) and (len(s_prod) == 0)):
        return 1
    else:
        key_group = r_group[0]
        new_prod, new_group = get_text(s_prod), get_text(r_group)
        if (find_similarity(new_prod, new_group) > 0.3) or (
                find_similarity(new_prod, get_abbreviation(r_group)) > 0.15) or (
                similar_word_exists(s_prod, key_group)) or similar_word_exists(s_cli, key_group):
            if key_group in hash_table.keys():
                hash_table[key_group].update(set(s_prod))
            else:
                hash_table[key_group] = set(s_prod)
            return 1
        else:
            second_chance.append([set(s_prod), key_group, tab_row])
            return 0


med_table = pd.read_excel('idcheck.xlsx')
Cli, Prod, Full, Group = med_table["NM_CLI"], med_table["PROD"], med_table["NM_FULL"], med_table["GROUP_NM_RUS"]
comparison_column = []
for table_row in range(99999):
    shop_product, shop_group, reference_name, reference_group, shop_text, reference_text = get_all_info(table_row)
    comparison_column.append(
        full_comparison(shop_product, shop_group, reference_name, reference_group, shop_text, reference_text,
                        table_row))
for i in range(3):
    for chance in second_chance:
        key_word = chance[1]
        if (key_word in list(hash_table.keys())) and (len(set(hash_table[key_word]).intersection(chance[0])) > 0):
            hash_table[key_word].update(chance[0])
            comparison_column[chance[2]] = 1
            second_chance.remove(chance)
        else:
            comparison_column[chance[2]] = 0
med_table["ARE_EQUAL"] = comparison_column
med_table = med_table.sort_values(by='ARE_EQUAL')
med_table.to_excel('./test.xlsx', sheet_name='Equals', index=False)
