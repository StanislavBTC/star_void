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
import urllib.request
from dotenv import load_dotenv

from src.ai.responder import respond
from src.modules import ask, distort, silence, void, psycholog
from src.utils.delay import random_delay, typing_effect

# Загружаем переменные окружения
load_dotenv("config/config.env")

# Глобальная переменная для управления процессом Ollama
ollama_process = None

def stop_ollama_local():
    global ollama_process
    if ollama_process:
        print("\n[system] Завершение работы Ollama...")
        ollama_process.terminate()
        try:
            ollama_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ollama_process.kill()
        print("[system] Ollama остановлена.")
    
    try:
        if os.name == 'posix':
            subprocess.run(["pkill", "-f", "ollama serve"], stderr=subprocess.DEVNULL)
    except Exception:
        pass

# Регистрируем функцию очистки
atexit.register(stop_ollama_local)

def ensure_ollama() -> bool:

    model_name = os.getenv('MODEL_NAME', 'deepseek-r1:8b')
    
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
            subprocess.run(["pkill", "-f", "ollama serve"], stderr = subprocess.DEVNULL)
            time.sleep(1)
    except Exception:
        pass

    # 3. Запускаем локально
    global ollama_process
    try:
        ollama_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Ждем инициализации API с постепенным увеличением времени
        for i in range(15):
            time.sleep(1)
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

def install_ollama_auto():
    """Автоматическая установка Ollama в зависимости от операционной системы"""
    import platform
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Для Windows используем PowerShell команду
            install_command = "irm https://ollama.com/install.ps1 | iex"
            full_command = [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command", install_command
            ]
            print("Установка Ollama для Windows...")
            subprocess.run(full_command, check=True)
        elif system in ["darwin", "linux"]:  # Darwin - это macOS
            # Для macOS и Linux используем curl команду
            install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
            print("Установка Ollama для macOS/Linux...")
            subprocess.run(install_cmd, shell=True, check=True)
        else:
            print(f"Автоматическая установка не поддерживается для {system} системы.")
            print("Пожалуйста, установите Ollama вручную с сайта: https://ollama.com/")
    except subprocess.CalledProcessError:
        print("Не удалось выполнить установку Ollama автоматически.")
        print("Пожалуйста, установите Ollama вручную с сайта: https://ollama.com/")
    except Exception as e:
        print(f"Ошибка при установке Ollama: {e}")


def _check_and_pull_model(model_name: str) -> None:

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
                    print("Программа может работать некорректно.\n")
                else:
                    print("Список моделей пуст.")
                    # Попробовать установить Ollama автоматически
                    try:
                        import shutil
                        if not shutil.which("ollama"):
                            print("Ollama не найдена в системе.")
                            choice = input("Хотите попробовать установить Ollama автоматически? (y/n): ")
                            if choice.lower() in ['y', 'yes', 'да']:
                                # Установка Ollama в зависимости от ОС
                                if os.name == 'nt':  # Windows
                                    install_command = "irm https://ollama.com/install.ps1 | iex"
                                    full_command = [
                                        "powershell",
                                        "-NoProfile",
                                        "-ExecutionPolicy", "Bypass",
                                        "-Command", install_command
                                    ]
                                    print("Установка Ollama для Windows...")
                                    subprocess.run(full_command, check=True)
                                else:  # Unix-like (macOS, Linux)
                                    install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
                                    print("Установка Ollama для macOS/Linux...")
                                    subprocess.run(install_cmd, shell=True, check=True)
                        else:
                            print("Пожалуйста, скачайте модель командой: ollama pull " + target_model)
                    except subprocess.CalledProcessError:
                        print("Не удалось выполнить установку Ollama автоматически.")
                        print("Пожалуйста, установите Ollama вручную с сайта: https://ollama.com/")
                    except Exception as e:
                        print(f"Ошибка при установке Ollama: {e}")
                        
                    print("Программа может работать некорректно.\n")
            else:
                print(f"[system] Модель {target_model} готова к работе.")
    except Exception as e:
        print(f"\nОшибка при проверке модели Ollama: {e}")

def print_help():
    print("""
            /ask       - диалог (краткие ответы, вопросы, дистанция)
            /distort   - искажение (фрагментация, растворение смысла)
            /void      - пустота (пассивное присутствие, молчание)
            /silence   - молчание (полный отказ от ответов)
            
            /psycholog - слушатель, может вести диалог

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
            time.sleep(0.1)
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
    
    username = input("Введи свое имя, пожалуйста: ")
    
    if not ollama_ready:
        print("Ollama недоступна. ИИ-функции не будут работать.")

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

            Star Void отличный слушатель, но не советчик.
            /help для получения помощи в выборе режима
                    """)

    mode = 'psycholog'
    modes = {
        "ask": ask,
        "distort": distort,
        "void": void,
        "silence": silence,
        "psycholog":  psycholog
    }
    
    animation = ThinkingAnimation()

    while True:
        try:
            prompt = f"[{username}] > "
            user_input = input(prompt).strip()
            
            # Обработка команд
            if user_input.startswith("/"):
                command = user_input[1:].lower()

                if command in ['exit', 'quit']:
                    print("\nДо встречи в пустоте...")
                    break

                elif command in modes:
                    mode = command
                    print(f"Режим изменен на {mode}")
                    continue

                elif command == "help":
                    print_help()
                    continue

                else:
                    print(f"Команда '{command}' не распознана. Введите /help для помощи.")
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
                    print(f"[{mode}] > " , end="" )
                    typing_effect(response)
                else:
                    if mode != "silence":
                        print(f"[{mode}] > " , end="" )
                        typing_effect("...")

        except KeyboardInterrupt:
            print("\n\nПрограмма завершена.")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            continue

if __name__ == "__main__":
    main()
