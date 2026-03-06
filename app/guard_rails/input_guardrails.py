MAX_INPUT_CHARS = 5000

def validate_length(text: str):
    if len(text) > MAX_INPUT_CHARS:
        return False
    return True