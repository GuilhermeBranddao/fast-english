import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd

class WordLearningAnalyzer:
    """
    Analyzes word learning progress based on word accuracy data.

    Attributes:
        word_accuracy_map (Dict[str, float]): Maps words to their accuracy percentages.
    """

    def __init__(self, word_stats_df: pd.DataFrame):
        """
        Initializes the analyzer with a DataFrame containing word accuracies.

        Args:
            word_stats_df (pd.DataFrame): DataFrame with at least 'word' and 'acuracia' columns.
        """
        self.word_accuracy_map: Dict[str, float] = dict(
            zip(word_stats_df['word'].str.lower(), word_stats_df['acuracia'])
        )

    def _is_word_learned(self, word: str, threshold: float = 60.0) -> bool:
        """
        Checks if a word (or compound word with underscores) is learned.

        Args:
            word (str): The word to check.
            threshold (float, optional): Minimum accuracy percentage to consider learned. Defaults to 60.0.

        Returns:
            bool: True if all parts of the word exceed the threshold accuracy.
        """
        components = word.lower().split("_")
        accuracies = [self.word_accuracy_map.get(part, 0.0) for part in components]
        return all(acc > threshold for acc in accuracies)

    def count_learned_words(self, word_paths: List[Path], threshold: float = 60.0) -> int:
        """
        Counts how many words in the given list are learned.

        Args:
            word_paths (List[Path]): List of Paths where each path's name is the word.
            threshold (float, optional): Accuracy threshold to consider a word learned. Defaults to 60.0.

        Returns:
            int: Number of learned words.
        """
        return sum(1 for path in word_paths if self._is_word_learned(path.name, threshold))

    def generate_learning_maps(self, categories: Dict[str, Dict[str, List[Path]]], threshold: float = 60.0
                              ) -> Tuple[Dict[str, Dict[str, Dict[str, int]]], Dict[str, int]]:
        """
        Generates learning statistics maps by category and subcategory.

        Args:
            categories (Dict[str, Dict[str, List[Path]]]): Nested dict of categories > subcategories > word paths.
            threshold (float, optional): Accuracy threshold to consider a word learned. Defaults to 60.0.

        Returns:
            Tuple[
                Dict[str, Dict[str, Dict[str, int]]],  # all_word_accuracy_map with 'total' and 'learned'
                Dict[str, int]                         # total learned words per category
            ]
        """
        all_word_accuracy_map = {}
        category_learned_map = {}

        for category, subcats in categories.items():
            all_word_accuracy_map[category] = {
                subcat: {
                    "total": len(word_list),
                    "learned": self.count_learned_words(word_list, threshold)
                }
                for subcat, word_list in subcats.items()
            }

            total_learned = sum(info["learned"] for info in all_word_accuracy_map[category].values())
            category_learned_map[category] = total_learned

        return all_word_accuracy_map, category_learned_map


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
    
    def get_word_info(self, word: str, return_dict:bool=False) -> pd.DataFrame:
        result = self.stats_grouped[self.stats_grouped["word"] == word]

        if return_dict:
            if result.empty:
                return {}
            else:
                return result.to_dict("records")[0]

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

