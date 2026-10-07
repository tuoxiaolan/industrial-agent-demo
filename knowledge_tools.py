from rag_search import search


def search_manual(query, model=None, doc_type=None, top_k=5):
    results = search(
        query=query,
        model=model,
        doc_type=doc_type,
        top_k=top_k,
    )

    if not results:
        return {
            "ok": False,
            "query": query,
            "error": "未找到相关知识库内容",
        }

    return {
        "ok": True,
        "query": query,
        "results": results,
    }