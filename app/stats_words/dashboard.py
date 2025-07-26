import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Classe WordStatsAnalyzer deve estar definida antes aqui
# (você já tem ela, conforme mensagem anterior)

class WordStatsDashboard:
    def __init__(self, analyzer: 'WordStatsAnalyzer'):
        self.analyzer = analyzer
        self.grouped = analyzer.grouped
        sns.set(style="whitegrid")

    def plot_summary(self):
        summary = self.analyzer.get_summary().iloc[0]
        print("Resumo Geral:")
        print(summary)
        print("\n")

    def plot_top_words(self, top_n=10):
        top_easy = self.analyzer.get_top_words(top_n, easier=True)
        top_hard = self.analyzer.get_top_words(top_n, easier=False)

        fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
        
        sns.barplot(data=top_easy, x="dificuldade_media", y="word", ax=axes[0], palette="Greens_r")
        axes[0].set_title(f"Top {top_n} Palavras Mais Fáceis")

        sns.barplot(data=top_hard, x="dificuldade_media", y="word", ax=axes[1], palette="Reds_r")
        axes[1].set_title(f"Top {top_n} Palavras Mais Difíceis")

        for ax in axes:
            ax.set_xlabel("Dificuldade Média")
            ax.set_ylabel("Palavra")
        
        plt.tight_layout()
        plt.show()

    def plot_difficulty_distribution(self):
        plt.figure(figsize=(10, 5))
        sns.histplot(self.grouped["dificuldade_media"], bins=20, kde=True, color="steelblue")
        plt.title("Distribuição da Dificuldade Média das Palavras")
        plt.xlabel("Dificuldade Média")
        plt.ylabel("Frequência")
        plt.tight_layout()
        plt.show()

    def plot_time_vs_difficulty(self):
        df = self.analyzer.df
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x="time_taken", y="difficulty", hue="perfect_guess", palette="Set1")
        plt.title("Relação entre Tempo Gasto e Dificuldade")
        plt.xlabel("Tempo (s)")
        plt.ylabel("Dificuldade")
        plt.legend(title="Acerto Perfeito")
        plt.tight_layout()
        plt.show()

    def show_all(self):
        self.plot_summary()
        self.plot_top_words()
        self.plot_difficulty_distribution()
        self.plot_time_vs_difficulty()

word_stats_dashboard = WordStatsDashboard(analyzer=analyzer)

word_stats_dashboard.show_all()