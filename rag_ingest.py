from pathlib import Path


DOCS_DIR = Path("demo_docs")


def parse_front_matter(text):
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)

    if len(parts) < 3:
        return {}, text

    metadata = {}

    for line in parts[1].strip().splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()

    body = parts[2].strip()
    return metadata, body


def split_sections(body):
    chunks = []
    current_section = "正文"
    current_lines = []

    for line in body.splitlines():
        if line.startswith("## "):
            if current_lines:
                chunks.append({
                    "section": current_section,
                    "text": "\n".join(current_lines).strip(),
                })

            current_section = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append({
            "section": current_section,
            "text": "\n".join(current_lines).strip(),
        })

    return chunks


def is_title_only_chunk(section):
    return (
        section["section"] == "正文"
        and section["text"].startswith("# ")
    )


def load_chunks():
    chunks = []

    for file_path in sorted(DOCS_DIR.glob("*.md")):
        text = file_path.read_text(encoding="utf-8")
        metadata, body = parse_front_matter(text)

        for section in split_sections(body):
            if is_title_only_chunk(section):
                continue

            chunk = {
                "model": metadata.get("model", ""),
                "doc_type": metadata.get("doc_type", ""),
                "version": metadata.get("version", ""),
                "source": metadata.get("source", file_path.name),
                "section": section["section"],
                "text": section["text"],
            }

            chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    chunks = load_chunks()

    print("分段数量：", len(chunks))
    print()

    for index, chunk in enumerate(chunks, start=1):
        print("=" * 60)
        print("序号：", index)
        print("型号：", chunk["model"])
        print("文档类型：", chunk["doc_type"])
        print("来源：", chunk["source"])
        print("章节：", chunk["section"])
        print("正文：")
        print(chunk["text"])