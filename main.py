import docker
import time
import os
import requests
import json
import subprocess
import atexit
import signal
import threading
import sys
from dotenv import load_dotenv

from src.ai.responder import respond
from src.modules import ask, distort, silence, void
from src.utils.delay import random_delay, typing_effect

# Загружаем переменные окружения
load_dotenv("config/config.env")

# Глобальная переменная для управления процессом Ollama
ollama_process = None

def stop_ollama_local():
    """Останавливает локальный процесс Ollama при выходе из программы."""
    global ollama_process
    if ollama_process:
        print("\n[system] Завершение работы Ollama...")
        ollama_process.terminate()
        try:
            ollama_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ollama_process.kill()
        print("[system] Ollama остановлена.")
    
    # Дополнительная очистка на случай, если процесс "отвязался"
    try:
        if os.name == 'posix':
            subprocess.run(["pkill", "-f", "ollama serve"], stderr=subprocess.DEVNULL)
    except Exception:
        pass

# Регистрируем функцию очистки
atexit.register(stop_ollama_local)

def ensure_ollama() -> bool:
    """
    Гарантирует запуск Ollama: убивает старые процессы и запускает новый.
    """
    model_name = os.getenv('MODEL_NAME', 'deepseek-r1:14b')
    
    # 1. Сначала попробуем проверить, не запущена ли она уже и работает ли
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=1)
        if response.status_code == 200:
            print("[system] Ollama уже запущена и отвечает.")
            _check_and_pull_model(model_name)
            return True
    except Exception:
        pass

    # 2. Если не отвечает, очищаем старые процессы (на случай зависания)
    print("[system] Подготовка к запуску Ollama...")
    try:
        if os.name == 'posix':
            subprocess.run(["pkill", "-f", "ollama serve"], stderr=subprocess.DEVNULL)
            time.sleep(1)
    except Exception:
        pass

    # 3. Запускаем локально
    global ollama_process
    try:
        ollama_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Ждем инициализации API с постепенным увеличением времени
        for i in range(15):
            time.sleep(2)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    print("[system] Ollama успешно запущена.")
                    _check_and_pull_model(model_name)
                    return True
            except Exception:
                print(f"[system] Ожидание API Ollama... ({i+1}/15)")
                continue
    except FileNotFoundError:
        print("[error] Команда 'ollama' не найдена. Установите Ollama с сайта ollama.com")
        return False
    except Exception as e:
        print(f"[error] Ошибка запуска: {e}")
        return False

    return False

def _check_and_pull_model(model_name: str) -> None:
    """Проверяет наличие модели и выводит список доступных, если нужная не найдена."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            target_model = model_name if ':' in model_name else f"{model_name}:latest"

            if target_model not in model_names and model_name not in model_names:
                print(f"\nВНИМАНИЕ: Модель {target_model} не найдена в Ollama.")
                if model_names:
                    print(f"Доступные модели: {', '.join(model_names)}")
                else:
                    print("Список моделей пуст. Пожалуйста, скачайте модель командой: ollama pull " + target_model)
                print("Программа может работать некорректно.\n")
            else:
                print(f"Модель {target_model} готова к работе.")
    except Exception as e:
        print(f"\nОшибка при проверке модели Ollama: {e}")

def print_help():
    print("""
            /ask      - диалог (краткие ответы, вопросы, дистанция)
            /distort  - искажение (фрагментация, растворение смысла)
            /void     - пустота (пассивное присутствие, молчание)
            /silence  - молчание (полный отказ от ответов)

            /quit     - выход из программы
        """)

class ThinkingAnimation:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None

    def _animate(self):
        chars = [".  ", ".. ", "...", "  .", "   "]
        i = 0
        while not self._stop_event.is_set():
            sys.stdout.write(f"\r{chars[i % len(chars)]}")
            sys.stdout.flush()
            time.sleep(0.4)
            i += 1
        sys.stdout.write("\r   \r")
        sys.stdout.flush()

    def start(self):
        if os.getenv("USE_THINKING_ANIMATION", "true").lower() == "true":
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._animate)
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            self._thread = None

def main() -> None:
    print("Проверка и запуск Ollama...")
    ollama_ready = ensure_ollama()
    
    if not ollama_ready:
        print("ВНИМАНИЕ: Ollama недоступна. ИИ-функции не будут работать.")

    print("""
                 .   * .      .   .        .
                 * .     * .  * .   *
                 .    * .    __  . _ .     *
            * .    * .__ ___   ____ ___.      .
                    |   _             | * .
              * .  |  S T A R       | * .  * .
            .    .  |       V O I D  |   .
                .   * |___ ______  ____|      *
              *     .     _.   . __   .  * .
                 *   .  * . * .  *    .     * .
                    * .   * .  * .      .
                    .    * .      .  * .

            Star Void отличный слушатель, но плохой советчик.
            /help для получения помощи в выборе режима
                    """)

    mode = 'ask'
    modes = {
        "ask": ask,
        "distort": distort,
        "void": void,
        "silence": silence
    }
    
    animation = ThinkingAnimation()

    while True:
        try:
            prompt = f"[{mode}] > "
            user_input = input(prompt).strip()

            if not user_input:
                print("Вы ничего не ввели")
                continue

            # Обработка команд
            if user_input.startswith("/"):
                command = user_input[1:].lower()

                if command in ['exit', 'quit']:
                    print("\nДо встречи в пустоте...")
                    break

                elif command in modes:
                    mode = command
                    print(f"Режим изменен на -> {mode}")
                    continue

                elif command == "help":
                    print_help()
                    continue

                else:
                    print(f"Команда '{command}' не распознана. Введите /help для списка.")
                    continue

            # Логика ответа
            random_delay()
            mode_func = modes.get(mode)
            
            if mode_func:
                animation.start()
                
                try:
                    response = mode_func(user_input)
                finally:
                    animation.stop()

                if response:
                    typing_effect(response)
                else:
                    if mode != "silence":
                        typing_effect("...")

        except KeyboardInterrupt:
            print("\n\nПрограмма завершена.")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            continue

if __name__ == "__main__":
    main()
