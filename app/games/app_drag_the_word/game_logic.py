"""
Lógica principal do jogo de formação de frases.
"""

from tkinter import messagebox
from app.toolkit import word_utils as utils
from app.toolkit.mod_files.database_json_editor import DatabaseJsonEditor


class GameLogic:
    """Gerencia a lógica principal do jogo."""
    
    def __init__(self, ui_manager, word_manager, collision_detector):
        self.ui_manager = ui_manager
        self.word_manager = word_manager
        self.collision_detector = collision_detector
        
        self.attempts = 0
        self.current_phrase_data = {}
        self.id_game_task = None
        
        # Configura a área de montagem no detector de colisões
        self.collision_detector.set_assembly_area(self.ui_manager.get_assembly_area())

    def load_level(self):
        """Carrega os dados da frase para o nível atual e inicializa o jogo."""
        if not self.word_manager.has_next_level():
            messagebox.showinfo("Fim do Jogo", "Parabéns! Você completou todas as fases!")
            self.ui_manager.root.destroy()
            return

        self.current_phrase_data = self.word_manager.prepare_level_data()
        if not self.current_phrase_data:
            return

        # Atualiza a interface
        portuguese_text = self.current_phrase_data.get("text_pt_br", "")
        self.ui_manager.update_portuguese_text(portuguese_text)
        
        # Reseta tentativas e resultado
        self.attempts = 0
        self.ui_manager.update_attempts(self.attempts)
        self.ui_manager.clear_result()
        self.ui_manager.enable_check_button()
        
        # Gera ID da tarefa para o editor
        self.id_game_task = utils.gerar_hash_id()
        
        # Limpa palavras anteriores e posiciona as novas
        self.word_manager.clear_words()
        self.word_manager.place_words(
            self.ui_manager.get_words_pool_frame(), 
            self  # Passa a referência da lógica do jogo
        )

    def check_phrase_action(self):
        """Ação executada ao clicar no botão 'Verificar Frase'."""
        self.attempts += 1
        self.ui_manager.update_attempts(self.attempts)

        # Coleta palavras na área de montagem
        assembled_words = self.word_manager.get_words_in_assembly_area(self.collision_detector)
        current_phrase = [word.word_text for word in assembled_words]
        correct_phrase = self.word_manager.get_correct_word_order()

        # Verifica se a frase está correta
        if current_phrase == correct_phrase:
            self._handle_correct_answer(assembled_words)
        else:
            self._handle_incorrect_answer(assembled_words, correct_phrase)

        self._log_attempt(current_phrase, correct_phrase)

    def _handle_correct_answer(self, assembled_words):
        """Processa uma resposta correta."""
        self.ui_manager.update_result("✅ Correto! Parabéns!", "#28A745")
        self.ui_manager.disable_check_button()
        
        # Colore as palavras de verde
        for word in assembled_words:
            word.config(bg="#25BA33")
            
        messagebox.showinfo("Parabéns!", "Você montou a frase corretamente!")
        self.ui_manager.root.after(1500, self._next_level)

    def _handle_incorrect_answer(self, assembled_words, correct_phrase):
        """Processa uma resposta incorreta."""
        self.ui_manager.update_result("❌ Incorreto! Tente novamente.", "#DC3545")
        self._verify_word_matches(correct_phrase, assembled_words)

    def _verify_word_matches(self, expected_phrase, assembled_words):
        """
        Verifica correspondências palavra por palavra e colore adequadamente.
        """
        for index, expected_word in enumerate(expected_phrase):
            if index < len(assembled_words):
                if assembled_words[index].word_text == expected_word:
                    assembled_words[index].config(bg="#25BA33")  # Verde para correto
                else:
                    assembled_words[index].config(bg="#BF1D12")  # Vermelho para incorreto

    def _log_attempt(self, current_phrase, correct_phrase):
        """Registra a tentativa no console para debug."""
        current_level = self.word_manager.get_current_level()
        print(f"Nível: {current_level + 1} | Tentativas: {self.attempts}")
        print("Frase esperada:", correct_phrase)
        print("Frase montada:", current_phrase)
        print("-" * 40)

    def _next_level(self):
        """Avança para o próximo nível do jogo."""
        self.word_manager.next_level()
        self.load_level()

    def reset_level(self):
        """Reseta o nível atual."""
        confirm = messagebox.askyesno("Resetar Nível", "Tem certeza que deseja resetar este nível?")
        if confirm:
            self.attempts = 0
            self.ui_manager.update_attempts(self.attempts)
            self.ui_manager.clear_result()
            self.ui_manager.enable_check_button()
            
            self.word_manager.clear_words()
            self.word_manager.place_words(
                self.ui_manager.get_words_pool_frame(), 
                self
            )

    def edit_button_action(self):
        """Ação executada ao clicar no botão de editar."""
        if self.id_game_task and self.current_phrase_data:
            DatabaseJsonEditor(
                master=self.ui_manager.root, 
                task_id=self.id_game_task, 
                task_list=self.current_phrase_data
            )

    def check_all_collisions(self):
        """Verifica colisões entre todas as palavras."""
        all_words = self.word_manager.get_draggable_words()
        self.collision_detector.check_all_collisions(all_words)

    def is_colliding_with_any_other_word(self, target_word):
        """Verifica se uma palavra está colidindo com outras."""
        all_words = self.word_manager.get_draggable_words()
        return self.collision_detector.is_colliding_with_any_other_word(target_word, all_words)