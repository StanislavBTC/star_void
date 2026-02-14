# единая точка общения с ИИ
import os
import sys
import json
import time
import requests
from typing import Optional
from dotenv import load_dotenv
from src.ai.filters import filter_advice, filter_empathy, filter_length, filter_thinking


# Загружаем конфигурацию
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv("config/config.env")

def _load_prompt(filename: str) -> str:

    # Файлы промптов находятся в config/ai/
    path = os.path.join('config', 'ai', filename)
    if not os.path.exists(path):
        return ""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return ""

def respond(user_input: str, mode: str = "ask") -> Optional[str]:
    # Получаем провайдера ИИ
    provider = os.getenv('LLM_PROVIDER', 'local').lower()
    
    if provider == 'local' or provider == 'ollama':  
        return _call_ollama_api(user_input, mode)  
        
def _call_ollama_api(user_input: str, mode: str = "ask") -> Optional[str]:
    # Получаем модель из конфига
    model = os.getenv('MODEL_NAME', 'deepseek-r1:8b')
    if model == 'default':
        model = 'deepseek-r1:8b'

    base_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/chat').replace('/api/chat', '').replace('/api/generate', '')
    chat_url = f"{base_url}/api/chat"
    gen_url = f"{base_url}/api/generate"

    # Загружаем промпты
    core_prompt = _load_prompt('core.txt')
    mode_prompt = _load_prompt(f'{mode}.txt')
    system_content = f"{core_prompt}\n\n{mode_prompt}".strip()

    # Подготовка опций
    options = {}
    max_tokens = os.getenv('MAX_TOKENS')
    if max_tokens:
        options['num_predict'] = int(max_tokens)
    temperature = os.getenv('TEMPERATURE')
    if temperature:
        options['temperature'] = float(temperature)

    # 1. Сначала пробуем Chat API
    payload_chat = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_input}
        ],
        'options': options,
        'stream': False
    }

    timeout = int(os.getenv('OLLAMA_TIMEOUT', '30'))
    retries = int(os.getenv('OLLAMA_RETRY_ATTEMPTS', '3'))
    retry_delay = int(os.getenv('OLLAMA_RETRY_DELAY', '2'))

    for attempt in range(retries + 1):
        try:
            response = requests.post(chat_url, json=payload_chat, timeout=timeout)
            if response.status_code == 200:
                content = response.json().get('message', {}).get('content', '')
                return _process_content(content, mode)
            elif response.status_code == 404:
                # Если Chat API не найден, пробуем Generate API
                full_prompt = f"{system_content}\n\nUser: {user_input}\nAssistant:"
                payload_gen = {
                    'model': model,
                    'prompt': full_prompt,
                    'options': options,
                    'stream': False
                }
                response = requests.post(gen_url, json=payload_gen, timeout=timeout)
                if response.status_code == 200:
                    content = response.json().get('response', '')
                    return _process_content(content, mode)

            print(f"Ollama error: {response.status_code}")
            break # Не ретраим при ошибках типа 404 или 500, если это не таймаут
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt < retries:
                time.sleep(retry_delay)
                continue
            print(f"Ollama connection error after {retries} retries: {e}")
        except Exception as e:
            print(f"Ollama unexpected error: {e}")
            break

    return None

def _process_content(content: str, mode: str = "ask") -> str:
    if content:
        content = filter_thinking(content)
        content = filter_advice(content)
        content = filter_empathy(content, mode)
        content = filter_length(content)
    return content

