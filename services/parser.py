def parse_expense(text):

    parts = text.split()

    if not parts:
        return None

    # First word must be amount
    try:
        amount = float(parts[0])
    except:
        return None

    # Second word is category
    category = parts[1].lower() if len(parts) > 1 else "Missing"

    tags = []
    note_words = []

    # Everything after amount & category
    for word in parts[2:]:

        if word.startswith("#"):
            tags.append(word[1:])
        else:
            note_words.append(word)

    note = " ".join(note_words)

    return {
        "amount": amount,
        "category": category,
        "note": note,
        "tags": tags
    }
