class TermDecoder:
    def __init__(self) -> None:
        super().__init__()

    def run(self, string: str) -> list[str]:
        result: list[str] = []
        state = "term"
        chars = list(string)
        current_term = ""

        string_counter = 0

        while True:
            if len(chars) == 0:
                if len(current_term) > 0:
                    result.append(current_term)

                if string_counter != 0:  # means there are unmatched `"`
                    raise ValueError("Unmatched strings")

                return result

            current_char = chars.pop(0)

            if state == "term":
                if current_char == " ":
                    state = "term-done"

                elif current_char == '"':
                    string_counter += 1
                    state = "string-entered"
                    continue

                else:
                    current_term += current_char

            if state == "string-entered":
                if current_char == '"':
                    string_counter -= 1
                    state = "term-done"
                else:
                    current_term += current_char

            if state == "term-done":
                if len(current_term) > 0:
                    result.append(current_term)

                current_term = ""
                state = "term"


if __name__ == "__main__":
    manager = TermDecoder()

    string = 'term1 "stringed terms" !inv_term2 !"inverted stringed terms"'
    result = manager.run(string)

    print(f"{string=} -> {result=}")
