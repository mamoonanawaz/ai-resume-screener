def split_long_paragraph(paragraph: str, max_words: int = 300) -> list[str]:
    words = paragraph.split()
    pieces = []

    for i in range(0, len(words), max_words):
        piece = " ".join(words[i:i + max_words]).strip()

        if piece:
            pieces.append(piece)

    return pieces


def chunk_text(
    text: str,
    target_words: int = 250,
    max_words: int = 350
) -> list[str]:
    """
    Split text into meaningful chunks.

    Roughly 250-350 English words normally falls within
    the assignment's target range of about 200-500 tokens.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = []
    current_word_count = 0

    for paragraph in paragraphs:
        paragraph_words = paragraph.split()
        paragraph_word_count = len(paragraph_words)

        # Split unusually large paragraphs first
        if paragraph_word_count > max_words:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_word_count = 0

            pieces = split_long_paragraph(
                paragraph,
                max_words=max_words
            )

            chunks.extend(pieces)
            continue

        # Add paragraph if it still fits
        if current_word_count + paragraph_word_count <= max_words:
            current_chunk.append(paragraph)
            current_word_count += paragraph_word_count

        else:
            if current_chunk:
                chunks.append("\n".join(current_chunk))

            current_chunk = [paragraph]
            current_word_count = paragraph_word_count

        # Close a chunk once it reaches useful size
        if current_word_count >= target_words:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_word_count = 0

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks