from random import randint
from typing import Tuple


def generate_rgb_colors() -> Tuple[int, int, int]:
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    return (r, g, b)


def break_lines(text: str, limit: int) -> str:
    words = text.split()
    lines = []
    current_line = ''
    for word in words:
        if len(current_line) + len(word) <= limit:
            current_line += word + ' '
        else:
            lines.append(current_line.strip())
            current_line = word + ' '
    lines.append(current_line.strip())
    return '\n'.join(lines)
