from __future__ import annotations


def wrap_text_by_words(text: str, words_per_line: int = 100) -> str:
    words = text.split()
    lines = []
    for index in range(0, len(words), words_per_line):
        line_words = words[index:index + words_per_line]
        lines.append(" ".join(line_words))
    return "\n".join(lines)

