import re

from equipment_tools import FIELD_ALIASES
from rag_ingest import load_chunks


def tokenize(text):
    text = text.lower()
    tokens = []

    tokens.extend(re.findall(r"[a-z0-9\-.]+", text))

    for chinese_text in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(chinese_text) == 1:
            tokens.append(chinese_text)
        else:
            for index in range(len(chinese_text) - 1):
                tokens.append(chinese_text[index:index + 2])

    return tokens


def normalize_query(query):
    normalized = query

    for alias, canonical in FIELD_ALIASES.items():
        normalized = normalized.replace(alias, canonical)

    normalized = normalized.replace("维护流程", "维护 流程")
    normalized = normalized.replace("保养流程", "保养 流程")

    return normalized


def search(query, model=None, doc_type=None, top_k=5):
    normalized_query = normalize_query(query)
    query_tokens = set(tokenize(normalized_query))
    results = []

    for chunk in load_chunks():
        if model and chunk["model"].lower() != model.lower():
            continue

        if doc_type and chunk["doc_type"].lower() != doc_type.lower():
            continue

        searchable_text = chunk["section"] + "\n" + chunk["text"]
        text_tokens = tokenize(chunk["text"])
        section_tokens = tokenize(chunk["section"])

        score = 0

        for token in query_tokens:
            score += text_tokens.count(token)
            score += 3 * section_tokens.count(token)

        if normalized_query.lower() in searchable_text.lower():
            score += 10

        if score > 0:
            result = dict(chunk)
            result["score"] = score
            results.append(result)

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def print_results(title, results):
    print("=" * 70)
    print(title)

    if not results:
        print("没有找到结果")
        return

    for index, result in enumerate(results, start=1):
        print()
        print("排名：", index)
        print("分数：", result["score"])
        print("型号：", result["model"])
        print("文档类型：", result["doc_type"])
        print("来源：", result["source"])
        print("章节：", result["section"])
        print("正文：", result["text"][:200])


if __name__ == "__main__":
    print_results(
        "查询1：Device-A提升电机功率",
        search(
            "Device-A提升电机功率",
            model="Device-A",
            doc_type="manual",
        ),
    )

    print_results(
        "查询2：Device-B处理能力",
        search(
            "Device-B处理能力",
            model="Device-B",
            doc_type="manual",
        ),
    )

    print_results(
        "查询3：Device-B维护流程",
        search(
            "Device-B维护流程",
            model="Device-B",
            doc_type="maintenance",
        ),
    )

    print_results(
        "查询4：Device-C设备重量",
        search(
            "Device-C设备重量",
            model="Device-C",
            doc_type="manual",
        ),
    )