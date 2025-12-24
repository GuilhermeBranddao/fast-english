import pyperclip
import time

def monitor_clipboard(output_file="palavras_copiadas.txt"):
    print("Monitorando área de transferência. Pressione Ctrl+C para parar.")
    recent_value = ""
    try:
        while True:
            tmp_value = pyperclip.paste()
            if tmp_value != recent_value:
                recent_value = tmp_value
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(tmp_value.strip() + "\n")
                print(f"Salvo: {tmp_value.strip()}")
            time.sleep(0.5)  # verifica a cada meio segundo
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado.")

if __name__ == "__main__":
    monitor_clipboard()