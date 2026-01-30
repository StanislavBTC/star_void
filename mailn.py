# mailn.py
from src.ai.responder import respond


def main() -> None:
    print("""Star_Void - терминальный софт на Python.
            Он не повышает продуктивность, не лечит и не мотивирует.
            Это программа для паузы""")

    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue

            answer = respond(user_input)

            if answer:
                print(answer)

        except KeyboardInterrupt:
            print("\nGoodbye!")


if __name__ == "__main__":
    main()
