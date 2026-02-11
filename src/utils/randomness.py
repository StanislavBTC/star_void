# Утилиты для рандомизации промптов из src/config/ai
import random
import os


def random_prompt(prompts_list=None):
    """Выбирает случайный промпт из списка."""
    if prompts_list is None:
        prompts_list = ["default", "basic", "simple"]
    return random.choice(prompts_list)


def random_prompt_block(block_dict=None):
    """Выбирает случайный блок промпта из словаря."""
    if block_dict is None:
        block_dict = {"default": "default content"}
    key = random.choice(list(block_dict.keys()))
    return key, block_dict[key]


def safe_format(template: str, **kwargs):
    """Безопасное форматирование строк."""
    try:
        return template.format(**kwargs)
    except KeyError:
        return template

