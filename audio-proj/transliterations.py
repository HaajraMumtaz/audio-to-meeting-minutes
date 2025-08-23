URDU_TO_ROMAN = {
    "ا": "a",
    "ب": "b",
    "پ": "p",
    "ت": "t",
    "ٹ": "t",
    "ث": "s",
    "ج": "j",
    "چ": "ch",
    "ح": "h",
    "خ": "kh",
    "د": "d",
    "ڈ": "d",
    "ر": "r",
    "ڑ": "r",
    "ز": "z",
    "ژ": "zh",
    "س": "s",
    "ش": "sh",
    "ص": "s",
    "ض": "z",
    "ط": "t",
    "ظ": "z",
    "ع": "a",
    "غ": "gh",
    "ف": "f",
    "ق": "q",
    "ک": "k",
    "گ": "g",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "ں": "n",
    "و": "w",
    "ہ": "h",
    "ھ": "h",
    "ء": "'",
    "ی": "y",
    "ے": "e",
}

def transliterate_urdu(word: str) -> str:
    result = []
    for char in word:
        if char in URDU_TO_ROMAN:
            result.append(URDU_TO_ROMAN[char])
        else:
            result.append(char)  # keep original if not mapped
    return "".join(result)