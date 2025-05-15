import pandas as pd
import matplotlib.pyplot as plt

class WordStatsAnalyzer:
    def __init__(self, list_game_name:list[str]):
        self.stats_grouped = self.concat_games(list_game_name)

    def concat_games(self, list_game_name):
        df_all = pd.DataFrame()
        for game_name in list_game_name:
            df = pd.read_csv(f"database/infos/{game_name}.csv")
            df = self.calc_perfect_guess(df=df, game_name=game_name)
            df_all = pd.concat([df_all, df])

        df_stats = df_all.groupby("word").agg(
                vezes_jogada=("word", "count"),
                acertos_perfeitos=("perfect_guess", "sum"),
            ).reset_index()

        df_stats["acuracia"] = round((df_stats["acertos_perfeitos"] / df_stats["vezes_jogada"]) * 100)
        
        return df_stats
    
    def calc_perfect_guess(self, df:pd.DataFrame, game_name:str):
        if game_name == "game_data_hangman":
            df["perfect_guess"] = (
                (df["list_of_typed_letters"] == df["correct_guessed_letters"]) &
                (df["clicks_on_guess"] < 2)
            )
        
        elif game_name == "game_data_word_shuffle_game":
            df["perfect_guess"] = (df["won"]) & (df["clicks_on_guess"]==1)

        return df
    
    def get_word_info(self, word: str) -> pd.DataFrame:
        result = self.stats_grouped[self.stats_grouped["word"] == word]

        if result.empty:
            # print(f"A palavra '{word}' não foi encontrada.")
            return pd.DataFrame()
        return result

    
    def get_top_words(self, top_n: int = 10, more_difficult: bool = False) -> pd.DataFrame:
        return self.stats_grouped.sort_values(by="acuracia", ascending=more_difficult).head(top_n)
    
    def get_summary(self):
        return pd.DataFrame({
            "total_palavras": [self.stats_grouped.shape[0]],
            "palavra_mais_fácil": [self.get_top_words(1, more_difficult=False)["word"].values[0]],
            "palavra_mais_difícil": [self.get_top_words(1, more_difficult=True)["word"].values[0]],
            "Acuracia media": [self.stats_grouped["acuracia"].mean()],
        })

