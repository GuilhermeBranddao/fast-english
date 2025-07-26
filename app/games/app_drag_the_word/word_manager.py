"""
Gerenciador de palavras para o jogo de formação de frases.
"""

import random
from app.toolkit import word_utils as utils
from app.games.drag_the_word.draggable_word import DraggableWord


class WordManager:
    """Gerencia as palavras do jogo, incluindo carregamento e posicionamento."""
    
    def __init__(self):
        self.phrases = self._load_phrases()
        self.current_level = 0
        self.list_draggable_words = []
        self.correct_word_order = []
        self.distractors = ["apple", "my", "go", "run", "dog"]

    def _load_phrases(self):
        """Carrega e filtra as frases do arquivo JSON."""
        all_words = utils.open_json('database/vocabulary/study_word_list.json')
        random.shuffle(all_words)
        filtered_words = []
        
        for word in all_words:
            if len(word['text_eng'].split()) > 3:
                word['text_eng'] = word['text_eng'].lower()
                filtered_words.append(word)
        
        return filtered_words

    def get_current_phrase_data(self):
        """Retorna os dados da frase atual."""
        if self.current_level < len(self.phrases):
            return self.phrases[self.current_level]
        return None

    def has_next_level(self):
        """Verifica se existe um próximo nível."""
        return self.current_level < len(self.phrases)

    def prepare_level_data(self):
        """Prepara os dados para o nível atual."""
        phrase_data = self.get_current_phrase_data()
        if not phrase_data:
            return None
            
        sentence = phrase_data.get("text_eng", "")
        sentence = sentence.translate(str.maketrans('', '', ',.?!')).lower().split()
        self.correct_word_order = sentence
        
        return phrase_data

    def clear_words(self):
        """Remove todas as palavras da tela."""
        for word_data in self.list_draggable_words:
            word_data.get("word_box").destroy()
        self.list_draggable_words.clear()

    def place_words(self, parent_frame, game_app):
        """Posiciona as palavras no frame especificado."""
        all_words_for_level = self.correct_word_order + self.distractors
        random.shuffle(all_words_for_level)

        words_per_row = 7
        x_offset = 20
        y_offset = 20
        word_spacing_x = 120
        word_spacing_y = 60

        for i, word_text in enumerate(all_words_for_level):
            row = i // words_per_row
            col = i % words_per_row
            
            x = x_offset + col * word_spacing_x
            y = y_offset + row * word_spacing_y
            
            is_correct = word_text in self.correct_word_order
            
            word_box = DraggableWord(parent_frame, word_text, game_app, is_correct_word=is_correct)
            word_box.place(x=x, y=y)
            
            self.list_draggable_words.append({
                "index": i, 
                "word_text": word_text, 
                "is_correct": is_correct, 
                "word_box": word_box
            })

    def get_words_in_assembly_area(self, collision_detector):
        """Retorna as palavras que estão na área de montagem."""
        assembled_words = []
        
        for word_data in self.list_draggable_words:
            word_widget = word_data.get("word_box")
            if collision_detector.is_word_in_assembly_area(word_widget):
                assembled_words.append(word_widget)
        
        # Ordena as palavras pela posição X (da esquerda para a direita)
        assembled_words.sort(key=lambda w: w.winfo_rootx())
        return assembled_words

    def get_correct_word_order(self):
        """Retorna a ordem correta das palavras."""
        return self.correct_word_order

    def get_draggable_words(self):
        """Retorna a lista de palavras arrastáveis."""
        return self.list_draggable_words

    def next_level(self):
        """Avança para o próximo nível."""
        self.current_level += 1

    def reset_level(self):
        """Reseta o nível atual."""
        # O reset será feito através do clear_words e place_words
        pass

    def get_total_levels(self):
        """Retorna o total de níveis disponíveis."""
        return len(self.phrases)

    def get_current_level(self):
        """Retorna o nível atual."""
        return self.current_level