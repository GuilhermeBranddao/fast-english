class ScoreManager:
    """Gerenciador de pontuações e estatísticas de dificuldade."""
    
    def __init__(self):
        self.scores = 0
        self.word_stats = {}  # Ex.: {"word": {"correct": 0, "incorrect": 0}}

    def add_points(self, points: int):
        """Adiciona pontos ao total."""
        self.scores += points

    def deduct_points(self, points: int):
        """Deduz pontos do total."""
        self.scores -= points

    def register_word(self, word: str, correct: bool):
        """Atualiza estatísticas de palavras."""
        if word not in self.word_stats:
            self.word_stats[word] = {"correct": 0, "incorrect": 0}
        
        if correct:
            self.word_stats[word]["correct"] += 1
        else:
            self.word_stats[word]["incorrect"] += 1

    def get_word_difficulty(self, word: str):
        """Calcula a dificuldade da palavra com base nas tentativas."""
        if word not in self.word_stats:
            return None
        
        stats = self.word_stats[word]
        total_attempts = stats["correct"] + stats["incorrect"]
        if total_attempts == 0:
            return 0
        return stats["incorrect"] / total_attempts  # Percentual de erros

    def get_total_score(self):
        """Retorna a pontuação total."""
        return self.scores

    def get_difficulty_summary(self):
        """Retorna um resumo de palavras mais difíceis/fáceis."""
        sorted_words = sorted(
            self.word_stats.items(),
            key=lambda x: self.get_word_difficulty(x[0]),
            reverse=True
        )
        return sorted_words