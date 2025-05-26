import random
import json
from datetime import datetime


# Embaralhar palavra preservando pontuação
def shuffle_word(word):
    # Remove pontuação do núcleo da palavra
    core = ''.join([c for c in word if c.isalpha()])
    
    if len(set(core.lower())) <= 1:  # Todas as letras são iguais
        return word
    
    shuffled = list(core)
    attempts = 0
    while True:
        random.shuffle(shuffled)
        if ''.join(shuffled).lower() != core.lower():
            break
        attempts += 1
        if attempts > 10:  # Segurança para evitar loop infinito
            return word

    shuffled_word = ''.join(shuffled)
    suffix = ''.join([c for c in word if not c.isalpha()])
    return shuffled_word + suffix


def open_json(filepath):
        try:
            with open(filepath, 'r', encoding="utf-8") as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {filepath}")
            return None
        

def filter_unknown_words(list_data_words, word_stats_analyzer, acc_min=60, filter_specific_word:str=None):
    """
    Retorna uma lista de frases (dicts) que possuem palavras com acurácia abaixo de um valor mínimo.

    :param list_data_words: Lista de dicionários com as sentenças.
    :param word_stats_analyzer: Objeto com método get_word_info(word, return_dict=True).
    :param acc_min: Acurácia mínima aceitável (padrão: 60).
    :return: Lista de dicionários contendo frases com palavras de baixa acurácia.
    """
    list_unknown_words = []

    ## Filtrando por uma palavra especifica
    if filter_specific_word:
        # filter_specific_word="i/l"
        list_specific_word = [d for d in list_data_words if filter_specific_word in d.get("text_eng", "")]
        return list_specific_word

    for dict_data_word in list_data_words:
        text_eng = dict_data_word.get("text_eng", "").lower()
        text_eng = text_eng.translate(str.maketrans('', '', ',.?!'))
        palavras = text_eng.split()

        for word in palavras:
            word_stats = word_stats_analyzer.get_word_info(word, return_dict=True)
            acc_word = word_stats.get("acuracia", 0)
            if acc_word < acc_min:
                list_unknown_words.append(dict_data_word)
                break  # pula para a próxima frase (evita adicionar a mesma várias vezes)

    return list_unknown_words


def gerar_hash_id():
    agora = datetime.now().strftime("%Y%m%d%H%M%S%f")  # AnoMesDiaHoraMinSegMicroseg
    return hex(abs(hash(agora)))[2:]  # Converte para hexadecimal e remove '0x'