import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd

import pandas as pd
from datetime import datetime

class MasteryAnalyzer:
    def __init__(self,
                 min_attempts=7,
                 weight_accuracy=0.6,
                 weight_diversity=0.2,
                 weight_recency=0.2,
                 min_penalty=0.5,
                 penalty_low_exposure=0.5):
        self.min_attempts = min_attempts
        self.weight_accuracy = weight_accuracy
        self.weight_diversity = weight_diversity
        self.weight_recency = weight_recency
        self.min_penalty = min_penalty
        self.penalty_low_exposure = penalty_low_exposure

    def recency_factor(self, last_played, reference_date=None):
        if reference_date is None:
            reference_date = datetime.now()
        days_since = (reference_date - pd.to_datetime(last_played)).days
        return max(0, 1 - days_since / 180)

    def calculate_mastery(self, row):
        accuracy = row['correct_attempts'] / row['total_attempts'] if row['total_attempts'] > 0 else 0
        diversity = len(row['game_name'])
        recency = self.recency_factor(row['last_played'])

        score = (
            accuracy * self.weight_accuracy +
            (diversity / 2) * self.weight_diversity +
            recency * self.weight_recency
        )

        if row['total_attempts'] < self.min_attempts:
            exposure_ratio = row['total_attempts'] / self.min_attempts
            penalty = self.min_penalty + self.penalty_low_exposure * exposure_ratio
            score *= penalty

        return round(score, 3)

    def classify(self, score):
        if score >= 0.8:
            return '✅ Dominada'
        elif score >= 0.5:
            return '⚠️ Parcialmente'
        else:
            return '❌ Não dominada'

    def process_game_data(self, df):
        df['correct_attempt'] = df['won'].astype(int)
        summary = df.groupby('word').agg({
            'correct_attempt': 'sum',
            'word': 'count',
            'game_name': lambda x: list(set(x)),
            'datetime': 'max'
        }).rename(columns={
            'word': 'total_attempts',
            'correct_attempt': 'correct_attempts',
            'datetime': 'last_played'
        })
        return summary

    def combine_game_summaries(self, *summaries):
        df_combined = pd.concat(summaries)
        df_final = df_combined.groupby(df_combined.index).agg({
            'correct_attempts': 'sum',
            'total_attempts': 'sum',
            'game_name': lambda x: list(set(sum(x, []))),
            'last_played': 'max'
        })
        return df_final

    def generate_report(self, word_shuffle_path, hangman_path):
        df_word = pd.read_csv(word_shuffle_path)
        df_hangman = pd.read_csv(hangman_path)

        word_summary = self.process_game_data(df_word)
        hangman_summary = self.process_game_data(df_hangman)

        df_final = self.combine_game_summaries(word_summary, hangman_summary)
        df_final['mastery_score'] = df_final.apply(self.calculate_mastery, axis=1)
        df_final['status'] = df_final['mastery_score'].apply(self.classify)

        return df_final.sort_values(by='mastery_score', ascending=False)
    
    def analyze_phrase_mastery(self, phrases, mastery_df):
        """
        Recebe uma lista de frases e retorna o domínio de cada palavra.
        """
        results = []

        for phrase in phrases:
            words = phrase.lower().split()
            for word in words:
                if word in mastery_df.index:
                    score = mastery_df.loc[word, 'mastery_score']
                    status = mastery_df.loc[word, 'status']
                else:
                    score = 0.0
                    status = '❌ Não dominada'
                results.append({
                    'word': word,
                    'score': score,
                    'status': status
                })

        return pd.DataFrame(results)


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
    def accuracy_word(self, word:str|list[str]) -> dict[str]:

        if isinstance(word, str):
            word = [word]
        
        accuracies = {part:self.word_accuracy_map.get(part, 0.0) for part in list(word)}
        # return all(acc > threshold for acc in accuracies)
        return accuracies

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
    
    

