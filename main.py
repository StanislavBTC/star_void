# mailn.py
from src.ai.responder import respond

from src.modules import ask
from src.modules import distort
from src.modules import silence
from src.modules import void

from src.utils.delay import random_delay, typing_effect

def main() -> None:

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

        
            Это терминальный софт на питоне, созданый для ...

            А собственно говоря я не знаю для чего он создан
            просто чтобы с кем-то поговорить, выговориться

            Star Void отличный слушатель, но плохой советчик.
            
            Режимы работы /ask, /void, /distort, /silence
                    """)

    mode = 'ask'
    modes = {
        "ask": ask,
        "distort": distort,
        "void": void,
        "silence": silence
    } 
    
    while True:
        try:
            
            user_input = input(f"[{mode}] >").strip()
            
            if not user_input:
                print("Вы ничего не ввели")
                continue
                
            if user_input.startswith("/"):
                comand = user_input[1:].lower()
                
                if comand in ['exit', 'quit']:
                    print("\nGoodbye!")
                    break
                    
                elif comand in modes:
                    mode = comand
                    print(f"Режим -> {mode}")
                    continue
                    
                elif comand == "help":
                    print_help()
                    continue
                   
                else:
                    print("Команда не расспазнана")
                    
                random_delay(0.5, 1.5)
                
                response = modes[mode](user_input)
                    
                if response:
                    typing_effect(response)
                    
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nОшибка: {e}")
            continue
            
def print_help():

    print("""
        
            /ask      - диалог (краткие ответы, вопросы, дистанция)
            /distort  - искажение (фрагментация, растворение смысла)
            /void     - пустота (пассивное присутствие, молчание)
            /silence  - молчание (полный отказ от ответов)

            /quit     - выход из программы
        
        """)
                     
if __name__ == "__main__":
    main()
