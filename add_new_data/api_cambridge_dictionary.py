import requests
from bs4 import BeautifulSoup
import json
import os
import time
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import threading
import collections # Para collections.deque

# --- Constantes e Globais para Headers ---
BASE_URL_CAMBRIDGE = "https://dictionary.cambridge.org"
REQUEST_BASE_URL_DICTIONARY = "https://dictionary.cambridge.org/dictionary/english/"
DATA_FILE = "cambridge_dictionary_data.json"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
]
current_user_agent_index = 0

# REQUEST_HEADERS será um dict global inicializado e modificado
# É importante notar que modificar globais diretamente de múltiplas threads pode ser arriscado
# sem locks, mas para User-Agent (lido por uma thread, modificado por uma), pode ser gerenciável.
# Uma classe Scraper seria uma melhoria para encapsular este estado.
REQUEST_HEADERS = {
    "User-Agent": USER_AGENTS[0],
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7", # pt-BR adicionado para preferência
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

MAX_CONSECUTIVE_FETCH_ERRORS_BEFORE_UA_SWITCH = 3
# Usar uma lista para consecutive_fetch_errors para que seja mutável e suas alterações
# dentro de fetch_word_html sejam refletidas globalmente (passagem por "referência de objeto")
shared_fetch_error_counter = [0] # [consecutive_fetch_errors]

REQUEST_DELAY_SECONDS = 2 # Reduzido para demonstração, aumente para uso real (ex: 3-5)

# --- Funções Auxiliares de Parsing (sem alteração) ---
def safe_get_text(element, default=""):
    """Extrai o texto de um elemento BeautifulSoup de forma segura."""
    return element.get_text() if element else default

def safe_get_attr(element, attr, default=""):
    """Extrai um atributo de um elemento BeautifulSoup de forma segura."""
    return element.get(attr, default) if element else default

# --- Funções de Persistência de Dados (sem alteração significativa) ---
def load_existing_data(filepath, gui_app_instance=None):
    """Carrega dados de um arquivo JSON, se existir."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            if gui_app_instance: gui_app_instance.log_message(f"Aviso: Arquivo '{filepath}' corrompido. Iniciando com dados vazios.")
            return {}
        except Exception as e:
            if gui_app_instance: gui_app_instance.log_message(f"Aviso: Não foi possível ler '{filepath}'. Erro: {e}. Iniciando com dados vazios.")
            return {}
    return {}

def save_data(data, filepath, gui_app_instance=None):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        if gui_app_instance: gui_app_instance.log_message(f"Erro Crítico: Não foi possível salvar dados em '{filepath}'. Erro: {e}")

# --- Função de Requisição HTTP (Modificada) ---
def fetch_word_html(word_to_search, gui_app):
    global current_user_agent_index, REQUEST_HEADERS, shared_fetch_error_counter

    # Atualiza o header com o UA corrente (caso tenha sido trocado)
    REQUEST_HEADERS["User-Agent"] = USER_AGENTS[current_user_agent_index]
    
    url = f"{REQUEST_BASE_URL_DICTIONARY}{word_to_search.lower()}"
    gui_app.log_message(f"Tentando acessar: {url} (UA: ...{USER_AGENTS[current_user_agent_index][-40:]})")

    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
        response.raise_for_status()
        gui_app.log_message(f"Status: {response.status_code} para '{word_to_search}'. Sucesso.")
        shared_fetch_error_counter[0] = 0 # Resetar contador de erros em sucesso
        return response.text
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
        gui_app.log_message(f"Erro de fetch para '{word_to_search}': {type(e).__name__} - {e}")
        shared_fetch_error_counter[0] += 1
        if shared_fetch_error_counter[0] >= MAX_CONSECUTIVE_FETCH_ERRORS_BEFORE_UA_SWITCH:
            old_ua_index = current_user_agent_index
            current_user_agent_index = (current_user_agent_index + 1) % len(USER_AGENTS)
            REQUEST_HEADERS["User-Agent"] = USER_AGENTS[current_user_agent_index] # Atualiza o header global para a próxima chamada
            gui_app.log_message(f"Muitos erros de fetch! Trocando User-Agent de ...{USER_AGENTS[old_ua_index][-40:]} para ...{USER_AGENTS[current_user_agent_index][-40:]}")
            shared_fetch_error_counter[0] = 0
    except requests.exceptions.RequestException as e:
        gui_app.log_message(f"Erro na requisição para '{word_to_search}': {type(e).__name__} - {e}")
    except Exception as e:
        gui_app.log_message(f"Erro inesperado no fetch para '{word_to_search}': {type(e).__name__} - {e}")
    return None

# --- Função Principal de Parsing (sem alteração, apenas chamada) ---
def parse_cambridge_entry(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    entry_data = {
        "word": "", "part_of_speech": "", "grammar": "",
        "pronunciations": {"uk": {}, "us": {}},
        "senses": [],
        "smart_vocabulary": {"topic": {}, "related_words": []}
    }
    entry_body = soup.find('div', class_='pr entry-body__el')
    if not entry_body: return entry_data # Retorna vazio se o corpo principal não for encontrado

    pos_header = entry_body.find('div', class_='pos-header')
    if pos_header:
        headword_span = pos_header.find('span', class_='hw dhw')
        entry_data['word'] = safe_get_text(headword_span)
        pos_span = pos_header.find('span', class_='pos dpos')
        entry_data['part_of_speech'] = safe_get_text(pos_span)
        gram_span = pos_header.find('span', class_='gram dgram')
        entry_data['grammar'] = safe_get_text(gram_span)

        uk_pron_span = pos_header.find('span', class_='uk dpron-i')
        if uk_pron_span:
            uk_audio_src = safe_get_attr(uk_pron_span.find('source', type='audio/mpeg'), 'src')

            # Tentativa de encontrar o span do IPA
            ipa_element = uk_pron_span.find('span', class_='ipa dipa')
            
            # Log para depuração:
            # print(f"Elemento IPA com 'ipa dipa': {ipa_element}")

            if not ipa_element:
                # Se não encontrou com 'ipa dipa', tente apenas com 'ipa'
                # Isso é mais robusto se a classe 'dipa' nem sempre estiver presente ou variar
                ipa_element = uk_pron_span.find('span', class_='ipa')
                # Log para depuração:
                # print(f"Elemento IPA apenas com 'ipa': {ipa_element}")
            
            ipa_text = safe_get_text(ipa_element)
            # Se o ipa_text ainda estiver vindo com as barras, ex: "/ˈstɔː.ri/", você pode limpá-las:
            if ipa_text.startswith('/') and ipa_text.endswith('/'):
               ipa_text = ipa_text.strip('/')
            # No entanto, com o seletor correto para o span interno, isso não deve ser necessário.

            entry_data['pronunciations']['uk'] = {
                'ipa': ipa_text,
                'audio': BASE_URL_CAMBRIDGE + uk_audio_src if uk_audio_src else ""
            }

        us_pron_span = pos_header.find('span', class_='us dpron-i')
        if us_pron_span:
            us_audio_src = safe_get_attr(us_pron_span.find('source', type='audio/mpeg'), 'src')
            
            ipa_element_us = us_pron_span.find('span', class_='ipa dipa')
            if not ipa_element_us:
                ipa_element_us = us_pron_span.find('span', class_='ipa')
            
            ipa_text_us = safe_get_text(ipa_element_us)

            if ipa_text_us.startswith('/') and ipa_text_us.endswith('/'):
               ipa_text_us = ipa_text_us.strip('/')

            entry_data['pronunciations']['us'] = {
                'ipa': ipa_text_us,
                'audio': BASE_URL_CAMBRIDGE + us_audio_src if us_audio_src else ""
            }
    else: # Fallback para a palavra se o cabeçalho não for encontrado
        headword_fallback = entry_body.find('span', class_='hw dhw')
        if headword_fallback: entry_data['word'] = safe_get_text(headword_fallback)

    pos_body = entry_body.find('div', class_='pos-body')
    if pos_body:
        for def_block in pos_body.find_all('div', class_='def-block ddef_block'):
            current_sense = {}
            ddef_h = def_block.find('div', class_='ddef_h')
            if ddef_h:
                epp_xref = ddef_h.find('span', class_='epp-xref')
                current_sense['cefr_level'] = safe_get_text(epp_xref)
            current_sense['definition'] = safe_get_text(def_block.find('div', class_='def ddef_d db'))
            
            examples, more_examples, see_also_terms = [], [], []
            def_body_ddef_b = def_block.find('div', class_='def-body ddef_b')
            if def_body_ddef_b:
                for ex_div in def_body_ddef_b.find_all('div', class_='examp dexamp', recursive=False):
                    examples.append(safe_get_text(ex_div.find('span', class_='eg deg')))
                
                see_xref_div = def_body_ddef_b.find('div', class_='xref see hax dxref-w')
                if see_xref_div:
                    for item_div in see_xref_div.find_all('div', class_='item lc'):
                        term_url = safe_get_attr(item_div.find('a'), 'href')
                        see_also_terms.append({
                            "term": safe_get_text(item_div.find('span', class_='x-h dx-h')),
                            "url": BASE_URL_CAMBRIDGE + term_url if term_url and not term_url.startswith('http') else term_url
                        })
            current_sense['examples'] = [ex for ex in examples if ex] # Remove exemplos vazios
            
            daccord_more_examples = def_block.find('div', class_='daccord')
            if daccord_more_examples and safe_get_text(daccord_more_examples.find('span', class_='showmore')) == "More examples":
                for li_tag in daccord_more_examples.find_all('li', class_='eg dexamp hax'):
                    more_examples.append(safe_get_text(li_tag))
            current_sense['more_examples'] = [ex for ex in more_examples if ex] # Remove exemplos vazios
            current_sense['see_also'] = see_also_terms
            
            if current_sense.get('definition') or current_sense.get('examples'):
                entry_data['senses'].append(current_sense)

    smart_vocab_div = entry_body.find('div', class_='smartt daccord')
    if smart_vocab_div:
        topic_anchor = smart_vocab_div.find('div', class_='daccord_lt').find('a') if smart_vocab_div.find('div', class_='daccord_lt') else None
        if topic_anchor:
            entry_data['smart_vocabulary']['topic'] = {
                "name": safe_get_text(topic_anchor), "url": safe_get_attr(topic_anchor, 'href')
            }
        related_words_list = smart_vocab_div.find('ul', class_='hul-u')
        if related_words_list:
            for li_tag in related_words_list.find_all('li', class_='lc'):
                word_link_tag = li_tag.find('a')
                if word_link_tag:
                    word_text = ""
                    base_span = word_link_tag.find('span', class_='base')
                    if base_span:
                        text_parts = [s.get_text() for s in base_span.find_all(True, recursive=False) if s.get_text()]
                        word_text = ' '.join(text_parts) if text_parts else safe_get_text(base_span)
                    else:
                        results_span = word_link_tag.find('span', class_='results')
                        word_text = safe_get_text(results_span) if results_span else safe_get_text(word_link_tag)
                    
                    if word_text:
                        entry_data['smart_vocabulary']['related_words'].append({
                            "word": word_text, "url": safe_get_attr(word_link_tag, 'href')
                        })
    return entry_data


# --- Lógica de Scraping para ser executada em uma Thread ---
def scraping_logic_thread(gui_app, initial_words, stop_event):
    global REQUEST_HEADERS # Para permitir a modificação do User-Agent

    all_words_data = load_existing_data(DATA_FILE, gui_app)
    
    # Conjunto para rastrear palavras já processadas ou na fila para evitar duplicatas e reprocessamento
    # Chaves são normalizadas (lowercase, strip)
    processed_or_in_queue_set = set(all_words_data.keys())
    for w in initial_words:
        processed_or_in_queue_set.add(w.lower().strip())

    # Fila de palavras a processar
    # collections.deque é eficiente para operações de adicionar/remover das extremidades
    word_processing_queue = collections.deque()
    for word in initial_words:
        normalized_initial_word = word.lower().strip()
        if normalized_initial_word: # Adiciona apenas se não for vazia
             word_processing_queue.append(normalized_initial_word)


    gui_app.log_message(f"--- Iniciando Coleta de Dados ---")
    gui_app.log_message(f"Carregados {len(all_words_data)} registros de '{DATA_FILE}'.")
    gui_app.log_message(f"Fila inicial com {len(word_processing_queue)} palavras.")

    words_newly_collected_this_session = 0
    words_skipped_this_session = 0
    words_failed_this_session = 0

    while word_processing_queue and not stop_event.is_set():
        current_word_to_process = word_processing_queue.popleft()
        # A normalização já deve ter ocorrido ao adicionar à fila/set, mas por segurança:
        normalized_key = current_word_to_process.lower().strip()

        if not normalized_key:
            continue
        
        gui_app.update_stats(
            len(all_words_data) - words_failed_this_session, # Total "bem sucedido" no arquivo
            words_skipped_this_session,
            words_failed_this_session,
            len(word_processing_queue) + 1 # +1 para a palavra atual
        )

        # Verifica se dados válidos já existem (não apenas um placeholder de erro)
        if normalized_key in all_words_data and all_words_data[normalized_key].get("word"):
            gui_app.log_message(f"Dados para '{normalized_key}' já existem. Pulando.")
            words_skipped_this_session += 1
            continue
        # Se já houve um erro registrado e não queremos tentar de novo:
        elif normalized_key in all_words_data and "error" in all_words_data[normalized_key]:
            gui_app.log_message(f"'{normalized_key}' resultou em erro anteriormente. Pulando.")
            words_skipped_this_session += 1
            continue
        
        # Se chegou aqui, a palavra é nova ou não tem dados válidos/erro registrado

        gui_app.log_message(f"Processando: '{normalized_key}' (Fila restante: {len(word_processing_queue)})")
        html_content = fetch_word_html(normalized_key, gui_app)
        
        parsed_data = None
        if html_content:
            parsed_data = parse_cambridge_entry(html_content) # parse_cambridge_entry deve existir!
            
            if parsed_data and parsed_data.get("word"): # Sucesso no parsing
                all_words_data[normalized_key] = parsed_data
                gui_app.log_message(f"Dados para '{normalized_key}' coletados.")
                words_newly_collected_this_session += 1

                # Adicionar palavras do SMART Vocabulary à fila, se houverem e forem novas
                if parsed_data.get("smart_vocabulary", {}).get("related_words"):
                    new_smart_words_added_to_queue_count = 0
                    for dict_word_info in parsed_data["smart_vocabulary"]["related_words"]:

                        url_from_smart_vocab = dict_word_info.get("url")
                        if url_from_smart_vocab:
                            url_from_smart_vocab = url_from_smart_vocab.strip() # Limpa espaços extras
                            
                            potential_new_key = None
                            
                            # Tenta extrair a palavra-chave da URL.
                            # Ex: "https://dictionary.cambridge.org/dictionary/english/be-another-story?topic=..." -> "be-another-story"
                            # REQUEST_BASE_URL_DICTIONARY deve ser "https://dictionary.cambridge.org/dictionary/english/"
                            if url_from_smart_vocab.startswith(REQUEST_BASE_URL_DICTIONARY):
                                path_after_base = url_from_smart_vocab[len(REQUEST_BASE_URL_DICTIONARY):]
                                # Remove qualquer query string (ex: ?topic=...)
                                potential_new_key = path_after_base.split('?')[0]
                            else:
                                # Fallback ou log se a URL não corresponder ao padrão esperado
                                # Você pode querer adicionar uma lógica mais robusta aqui se os padrões de URL variarem.
                                # Por exemplo, usando urllib.parse para obter o último segmento do path.
                                # from urllib.parse import urlparse
                                # path_segments = urlparse(url_from_smart_vocab).path.strip('/').split('/')
                                # if len(path_segments) > 0 and path_segments[-2] == "english": # Ex: /dictionary/english/word
                                #     potential_new_key = path_segments[-1]
                                # else:
                                gui_app.log_message(f"AVISO: URL do SMART Vocab '{url_from_smart_vocab}' não segue o padrão esperado para extração da palavra-chave.")

                            # Se uma chave válida foi extraída e ainda não está na fila/processada
                            if potential_new_key and potential_new_key not in processed_or_in_queue_set:
                                # A chave extraída da URL já deve estar no formato correto (lowercase, hifens)
                                processed_or_in_queue_set.add(potential_new_key)
                                word_processing_queue.append(potential_new_key)
                                new_smart_words_added_to_queue_count += 1
                                # gui_app.log_message(f"SMART Vocab: Adicionando '{potential_new_key}' à fila.") # Log detalhado opcional
                            # else if potential_new_key: # Opcional: logar se a palavra já estava na fila/processada
                                # gui_app.log_message(f"SMART Vocab: '{potential_new_key}' já na fila ou processada.")

                    if new_smart_words_added_to_queue_count > 0:
                        gui_app.log_message(f"Adicionadas {new_smart_words_added_to_queue_count} novas palavras do SMART Vocab à fila de processamento.")
            
            else: # Falha no parsing
                all_words_data[normalized_key] = {
                    "error": "Falha no parsing ou estrutura da página inesperada.",
                    "original_query": normalized_key, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                gui_app.log_message(f"Erro no parsing para '{normalized_key}'.")
                words_failed_this_session += 1
        else: # Falha no fetch HTML
            all_words_data[normalized_key] = {
                "error": "Falha ao buscar o conteúdo HTML.",
                "original_query": normalized_key, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            gui_app.log_message(f"Erro ao buscar HTML para '{normalized_key}'.")
            words_failed_this_session += 1
        
        save_data(all_words_data, DATA_FILE, gui_app)
        gui_app.log_message(f"Arquivo '{DATA_FILE}' atualizado. (Total: {len(all_words_data)} palavras)")

        if stop_event.is_set():
            gui_app.log_message("Processo interrompido pelo usuário.")
            break
        
        gui_app.log_message(f"Aguardando {REQUEST_DELAY_SECONDS}s...")
        time.sleep(REQUEST_DELAY_SECONDS)

    if stop_event.is_set():
        gui_app.log_message("Coleta interrompida.")
    elif not word_processing_queue:
        gui_app.log_message("Fila de processamento vazia.")
    
    gui_app.log_message("\n--- Coleta Finalizada (Sessão) ---")
    gui_app.log_message(f"Palavras novas coletadas nesta sessão: {words_newly_collected_this_session}")
    gui_app.log_message(f"Palavras puladas (já existentes ou erro anterior): {words_skipped_this_session}")
    gui_app.log_message(f"Falhas nesta sessão: {words_failed_this_session}")
    gui_app.log_message(f"Total de registros em '{DATA_FILE}': {len(all_words_data)}")
    gui_app.enable_start_button()


# --- Classe da Interface Gráfica Tkinter ---
class ScraperAppGUI:
    def __init__(self, master_root):
        self.master = master_root
        master_root.title("Cambridge Dictionary Scraper")
        master_root.geometry("700x550")

        self.stop_event = threading.Event()
        self.scraper_thread = None

        # Frame para controles
        control_frame = ttk.Frame(master_root, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Palavras Iniciais (separadas por vírgula):").pack(side=tk.LEFT, padx=(0, 5))
        self.words_entry = ttk.Entry(control_frame, width=40)
        self.words_entry.insert(0, "story, have, elegance, ubiquitous, nonexistentwordxyz")
        self.words_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.start_button = ttk.Button(control_frame, text="Iniciar Coleta", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Parar", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        # Área de Log
        log_frame = ttk.LabelFrame(master_root, text="Log de Atividades", padding="10")
        log_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        self.log_text_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
        self.log_text_area.pack(expand=True, fill=tk.BOTH)

        # Frame para Estatísticas
        stats_frame = ttk.LabelFrame(master_root, text="Estatísticas", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=(0,10))

        self.stats_label = ttk.Label(stats_frame, text="Coletadas: 0 | Puladas: 0 | Falhas: 0 | Fila: 0")
        self.stats_label.pack()
        
        master_root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log_message(self, message):
        if hasattr(self, 'log_text_area') and self.log_text_area.winfo_exists():
            self.log_text_area.config(state=tk.NORMAL)
            self.log_text_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
            self.log_text_area.see(tk.END)
            self.log_text_area.config(state=tk.DISABLED)
            self.master.update_idletasks() # Força atualização da UI

    def update_stats(self, collected, skipped, failed, queue_size):
        if hasattr(self, 'stats_label') and self.stats_label.winfo_exists():
            self.stats_label.config(text=f"Coletadas (total): {collected} | Puladas (sessão): {skipped} | Falhas (sessão): {failed} | Fila: {queue_size}")
            self.master.update_idletasks()

    def start_scraping(self):
        initial_words_str = self.words_entry.get()
        if not initial_words_str.strip():
            messagebox.showwarning("Entrada Inválida", "Por favor, insira algumas palavras iniciais.")
            return
            
        initial_words = [word.strip() for word in initial_words_str.split(',') if word.strip()]
        if not initial_words:
            messagebox.showwarning("Entrada Inválida", "Nenhuma palavra válida para processar após limpeza.")
            return

        self.log_text_area.config(state=tk.NORMAL)
        self.log_text_area.delete('1.0', tk.END) # Limpa log anterior
        self.log_text_area.config(state=tk.DISABLED)

        self.stop_event.clear()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.words_entry.config(state=tk.DISABLED)
        
        self.log_message(f"Iniciando coleta para: {', '.join(initial_words)}")
        
        # Passa a instância da GUI e o evento de parada para a thread
        self.scraper_thread = threading.Thread(target=scraping_logic_thread, args=(self, initial_words, self.stop_event))
        self.scraper_thread.daemon = True 
        self.scraper_thread.start()
        
        # Não é mais necessário, pois a thread chama enable_start_button() no final
        # self.master.after(100, self.check_thread_status)

    def stop_scraping(self):
        if self.scraper_thread and self.scraper_thread.is_alive():
            self.stop_event.set()
            self.log_message("Sinal de parada enviado à thread de coleta...")
        self.stop_button.config(state=tk.DISABLED) # Desabilita imediatamente

    def enable_start_button(self):
        """Chamado pela thread de scraping quando ela termina."""
        if self.master.winfo_exists(): # Verifica se a janela ainda existe
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.words_entry.config(state=tk.NORMAL)
            self.log_message("Pronto para nova coleta ou fechar.")
            
    def on_closing(self):
        if self.scraper_thread and self.scraper_thread.is_alive():
            self.log_message("Tentando parar a coleta antes de fechar...")
            self.stop_event.set()
            # Poderia esperar um pouco pela thread aqui, ou apenas avisar
            if messagebox.askokcancel("Sair", "A coleta de dados está em andamento. Deseja realmente sair? O progresso atual foi salvo."):
                self.master.destroy()
            else:
                return # Não fecha
        else:
            self.master.destroy()

# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    # É crucial que a função parse_cambridge_entry esteja definida e completa.
    # Se ela não estiver completa (como no placeholder acima), o parsing falhará.
    # Certifique-se de que a função `parse_cambridge_entry` da sua resposta anterior
    # está incluída integralmente neste script.
    if parse_cambridge_entry.__doc__ and "placeholder" in parse_cambridge_entry.__doc__:
         print("ERRO: A função parse_cambridge_entry está incompleta. Copie a versão completa.")
         exit()

    root = tk.Tk()
    app = ScraperAppGUI(root)
    root.mainloop()