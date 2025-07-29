import os
import json
import uuid
import re
from datetime import datetime, timezone
from typing import Dict, Any

class CardCreator:
    """
    Uma classe para criar e salvar cards de estudo como arquivos JSON,
    seguindo uma estrutura de diretórios específica e personalizada.

    Atributos:
        BASE_PATH (str): O caminho base onde os cards personalizados serão salvos.
    """
    BASE_PATH = os.path.join(
        'database', 'extract_data_video', 'data',
        'extracted_data', 'personalized', 'data_organize'
    )

    def __init__(self, category: str, subcategory: str):
        """
        Inicializa o CardCreator com uma categoria e subcategoria específicas.

        Args:
            category (str): A categoria principal para os cards (ex: 'youtube_videos').
            subcategory (str): A subcategoria para os cards (ex: 'finanças').
        """
        if not category or not subcategory:
            raise ValueError("A categoria e a subcategoria não podem estar vazias.")
        
        # Sanitiza os nomes para uso em caminhos de diretório
        self.category = self._sanitize_path_name(category)
        self.subcategory = self._sanitize_path_name(subcategory)
        
        # Define o caminho completo para a sessão de criação atual
        self.session_path = os.path.join(self.BASE_PATH, self.category, self.subcategory)

    def _sanitize_path_name(self, text: str) -> str:
        """
        Converte uma string em um nome de pasta/arquivo sanitizado em snake_case.

        Exemplo: "How are, you?" -> "how_are_you"

        Args:
            text (str): A string de entrada.

        Returns:
            str: A string sanitizada em snake_case.
        """
        # Remove a maioria dos caracteres de pontuação, mantendo letras, números e espaços
        text = re.sub(r'[^\w\s-]', '', text).strip()
        # Substitui espaços e hífens por underscores
        text = re.sub(r'[-\s]+', '_', text)
        return text.lower()

    def _generate_card_json(
        self,
        pergunta_pt: str,
        traducao_en: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Gera o dicionário para o conteúdo JSON do card.

        Args:
            pergunta_pt (str): A pergunta ou frase em português.
            traducao_en (str): A tradução em inglês.
            **kwargs: Campos opcionais adicionais para o card.

        Returns:
            Dict[str, Any]: Um dicionário representando os dados do card.
        """
        now_utc = datetime.now().isoformat(timespec='microseconds') + "Z"
        
        card_data = {
            "id": uuid.uuid4().hex,
            "pergunta_pt-br": pergunta_pt,
            "uso_da_linguagem": "",
            "tradução_en": traducao_en,
            "fonetica": "",
            "difficulty_level": "beginner",
            "part_of_speech": "phrase",
            "category": self.category,
            "subcategory": self.subcategory,
            "context": "",
            "example_en": "",
            "example_pt": "",
            "created_at": now_utc,
            "updated_at": now_utc,
            "observations": "",
            "status": "pending",
            "author": "CardCreator Class"
        }
        
        # Atualiza o dicionário com quaisquer argumentos opcionais fornecidos
        card_data.update(kwargs)
        return card_data

    def create_card(
        self,
        pergunta_pt: str,
        traducao_en: str,
        **kwargs: Any
    ) -> str:
        """
        Cria a estrutura de diretórios e salva o card como um arquivo JSON.

        Args:
            pergunta_pt (str): A pergunta ou frase em português.
            traducao_en (str): A tradução em inglês.
            **kwargs: Campos opcionais adicionais para o card.

        Returns:
            str: O caminho completo para o arquivo JSON recém-criado.
        
        Raises:
            ValueError: Se as frases em português/inglês estiverem vazias ou
                        se um nome de pasta válido não puder ser gerado.
        """
        if not pergunta_pt or not traducao_en:
            raise ValueError("As frases em português e inglês não podem estar vazias.")

        # Cria o nome da pasta 'sentense' a partir da tradução em inglês
        sentence_folder_name = self._sanitize_path_name(traducao_en)
        if not sentence_folder_name:
            raise ValueError(f"Não foi possível gerar um nome de pasta válido a partir de: '{traducao_en}'")

        # Constrói o caminho final do diretório e do arquivo
        final_dir_path = os.path.join(self.session_path, sentence_folder_name)
        file_path = os.path.join(final_dir_path, "text_v2.json")

        # Cria os diretórios necessários, se ainda não existirem
        os.makedirs(final_dir_path, exist_ok=True)

        # Gera o conteúdo JSON para o card
        card_json_content = self._generate_card_json(
            pergunta_pt=pergunta_pt,
            traducao_en=traducao_en,
            **kwargs
        )

        # Salva o dicionário como um arquivo JSON formatado
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(card_json_content, f, ensure_ascii=False, indent=2)

        print(f"Card criado com sucesso em: {file_path}")
        return file_path