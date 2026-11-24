import sys
from pathlib import Path


TOKENS = {
    "*": "RIGHT",
    "**": "LEFT",
    "***": "INC",
    "****": "DEC",
    "*****": "OUT",
    "******": "IN",
    "*******": "LOOP_START",
    "********": "LOOP_END",
}


def tokenize(source: str) -> list[str]:
    return [token for token in source.split() if token in TOKENS]


def build_brace_map(tokens: list[str]) -> dict[int, int]:
    stack = []
    braces = {}

    for i, token in enumerate(tokens):
        if token == "*******":
            stack.append(i)
        elif token == "********":
            if not stack:
                raise SyntaxError(f"Unmatched ']' at token index {i}")

            start = stack.pop()
            braces[start] = i
            braces[i] = start

    if stack:
        raise SyntaxError(f"Unmatched '[' at token index {stack[-1]}")

    return braces


def evaluate(source: str) -> None:
    tokens = tokenize(source)
    braces = build_brace_map(tokens)

    cells = bytearray(1)
    ptr = 0
    pc = 0

    while pc < len(tokens):
        token = tokens[pc]

        if token == "*":
            ptr += 1
            if ptr == len(cells):
                cells.append(0)

        elif token == "**":
            ptr = max(0, ptr - 1)

        elif token == "***":
            cells[ptr] = (cells[ptr] + 1) & 0xFF

        elif token == "****":
            cells[ptr] = (cells[ptr] - 1) & 0xFF

        elif token == "*****":
            sys.stdout.write(chr(cells[ptr]))

        elif token == "******":
            ch = sys.stdin.read(1)
            cells[ptr] = ord(ch) & 0xFF if ch else 0

        elif token == "*******" and cells[ptr] == 0:
            pc = braces[pc]

        elif token == "********" and cells[ptr] != 0:
            pc = braces[pc]

        pc += 1


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} <filename>", file=sys.stderr)
        return 1

    try:
        source = Path(sys.argv[1]).read_text(encoding="utf-8")
        evaluate(source)
    except (OSError, SyntaxError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
