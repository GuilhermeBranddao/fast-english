import json
import os

class DataManager:
    """
    Gerencia o carregamento e acesso aos dados do dicionário a partir de um arquivo JSON.
    """
    def __init__(self, filepath="seu_arquivo_dicionario.json"):
        """
        Inicializa o DataManager.

        Args:
            filepath (str): O caminho para o arquivo JSON do dicionário.
        """
        self.filepath = filepath
        self.data = self._load_data()

    def _load_data(self):
        """
        Carrega os dados do arquivo JSON.

        Returns:
            dict: Os dados do dicionário ou um dicionário vazio em caso de erro.
        """
        if not os.path.exists(self.filepath):
            print(f"Erro: Arquivo de dados '{self.filepath}' não encontrado.")
            return {}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Erro: Falha ao decodificar o arquivo JSON '{self.filepath}'.")
            return {}
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
            return {}

    def buscar_palavra(self, palavra):
        """
        Busca uma palavra no dicionário (case-insensitive).

        Args:
            palavra (str): A palavra a ser buscada.

        Returns:
            dict or None: Os dados da palavra se encontrada, caso contrário None.
        """
        palavra_lower = palavra.lower()
        return self.data.get(palavra_lower)

if __name__ == '__main__':
    # Teste rápido do DataManager
    dm = DataManager()
    if dm.data:
        print("Dados carregados com sucesso!")
        
        palavra_teste = "story"
        resultado = dm.buscar_palavra(palavra_teste)
        if resultado:
            print(f"\nDados para '{palavra_teste}':")
            print(json.dumps(resultado, indent=2))
        else:
            print(f"\nPalavra '{palavra_teste}' não encontrada.")

        palavra_inexistente = "xyz123"
        resultado_inexistente = dm.buscar_palavra(palavra_inexistente)
        if not resultado_inexistente:
            print(f"Palavra '{palavra_inexistente}' corretamente não encontrada.")
    else:
        print("Falha ao carregar os dados.")