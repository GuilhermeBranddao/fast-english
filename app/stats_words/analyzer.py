import pandas as pd
import matplotlib.pyplot as plt

class WordStatsAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare_data()

    def _prepare_data(self):
        df = self.df

        # Preenchendo campos nulos
        df["correct_guessed_letters"] = df["correct_guessed_letters"].fillna("")
        df["incorrect_guessed_letters"] = df["incorrect_guessed_letters"].fillna("")
        df["list_of_typed_letters"] = df["list_of_typed_letters"].fillna("")
        df["clicks_on_guess"] = df["clicks_on_guess"].fillna(999)
        df["time_taken"] = df["time_taken"].fillna(0)

        # Cálculo de métricas
        df["qtd_correct_guessed_letters"] = df["correct_guessed_letters"].str.replace(",", "").str.len()
        df["qtd_incorrect_guessed_letters"] = df["incorrect_guessed_letters"].str.replace(",", "").str.len()

        max_time = df["time_taken"].max() or 1
        df["difficulty_wrong"] = df["qtd_incorrect_guessed_letters"] / df["qtd_correct_guessed_letters"].replace(0, 1)
        df["difficulty_time"] = (df["time_taken"] / max_time) * 10
        df["difficulty"] = df["difficulty_wrong"] + df["difficulty_time"]

        df["perfect_guess"] = (
            (df["list_of_typed_letters"] == df["correct_guessed_letters"]) &
            (df["clicks_on_guess"] < 2)
        )

        self.df = df
        self.grouped = self._aggregate_data()

    def _aggregate_data(self):
        return self.df.groupby("word").agg(
            vezes_jogada=("word", "count"),
            dificuldade_media=("difficulty", "mean"),
            erros_médios=("qtd_incorrect_guessed_letters", "mean"),
            acertos_perfeitos=("perfect_guess", "sum"),
            tempo_medio=("time_taken", "mean"),
            taxa_acerto_perfeito=("perfect_guess", "mean"),
        ).reset_index()

    def get_word_info(self, word: str) -> pd.DataFrame:
        result = self.grouped[self.grouped["word"] == word]

        if result.empty:
            print(f"A palavra '{word}' não foi encontrada.")
            return pd.DataFrame()
        return result

    def get_top_words(self, top_n: int = 10, easier: bool = True) -> pd.DataFrame:
        return self.grouped.sort_values(by="dificuldade_media", ascending=easier).head(top_n)

    def get_summary(self) -> pd.DataFrame:
        return pd.DataFrame({
            "total_palavras": [self.grouped.shape[0]],
            "palavra_mais_fácil": [self.get_top_words(1, easier=True)["word"].values[0]],
            "palavra_mais_difícil": [self.get_top_words(1, easier=False)["word"].values[0]],
            "dificuldade_média_geral": [self.grouped["dificuldade_media"].mean()],
        })

    def get_word_difficulty_distribution(self) -> pd.Series:
        return self.grouped["dificuldade_media"]

    def plot_word_difficulty(self, top_n: int = 20):
        import seaborn as sns
        sns.set(style="whitegrid")
        top = self.get_top_words(top_n, easier=False)
        plt.figure(figsize=(12, 6))
        sns.barplot(data=top, x="word", y="dificuldade_media", palette="coolwarm")
        plt.title(f"Top {top_n} Palavras Mais Difíceis")
        plt.ylabel("Dificuldade Média")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


# Exemplo de uso
df = pd.read_csv("database/infos/game_data_hangman.csv")

analyzer = WordStatsAnalyzer(df)

# Obter info da palavra
display(analyzer.get_word_info("all"))

# Top 5 palavras mais difíceis
display(analyzer.get_top_words(5, easier=False))

# Resumo geral
display(analyzer.get_summary())
