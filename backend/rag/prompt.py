from __future__ import annotations


SYSTEM_PROMPT = """You are a retrieval-augmented assistant for MSL LiDAR annotation operations.
Be conversational but only answer from the provided documentation context.
If the documentation does not contain the answer, reply with: Sorry, I cannot provide you with the accurate answer to your question given my current content.
Do not infer undocumented policy.

Answer:
<grounded answer>

Sources:
* Document: <name> | Section: <section>
"""


def build_context(chunks: list[dict]) -> str:
    formatted_chunks: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        page = f" | Page: {chunk['page_number']}" if chunk.get("page_number") else ""
        formatted_chunks.append(
            (
                f"[Context {index}] Document: {chunk['document_name']} | "
                f"Section: {chunk['section_title']} | Type: {chunk['chunk_type']}{page}\n"
                f"{chunk['text']}"
            )
        )
    return "\n\n".join(formatted_chunks)


def build_messages(question: str, chunks: list[dict]) -> list[dict[str, str]]:
    context = build_context(chunks)
    user_prompt = (
        f"Question:\n{question}\n\n"
        f"Documentation Context:\n{context}\n\n"
        "Use only the context above."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
