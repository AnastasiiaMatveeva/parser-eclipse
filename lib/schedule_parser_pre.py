import re

def read_schedule(path: str, mode: str, enc: str) -> str:
    """
    read the input .inc file forming a string of text
    @param path: path to the input .inc file
    @param mode: reading mode
    @param enc: encoding
    @return: string of input text
    """
    with open(path, mode, encoding = enc) as file:
        text = file.read()
    return text

def inspect_schedule(text: str) -> bool:
    """
    inspect schedule syntax
    @param text: input text from .inc file
    @return: inspected input text from .inc file
    """
    if re.search(r'^\s*$', text):
        return False
    else:
        return True

def clean_schedule(text: str) -> str:
    """
    clean '-- ' comments
    @param text: inspected input text from .inc file
    @return: cleaned input text from .inc file
    """
    pattern_1 = re.compile('\n*--.*\n+')
    text = re.sub(pattern_1, '\n', text)

    pattern_2 = re.compile('\s*\n+\s*')
    text= re.sub(pattern_2, '\n', text)

    return text
