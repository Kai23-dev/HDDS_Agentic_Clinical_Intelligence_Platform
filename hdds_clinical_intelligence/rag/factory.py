"""
RAG backend selector.

Selection order is controlled by the RAG_BACKEND env var.
The selected instance is cached so we don't rebuild the index on every call.
"""

import os

_cached = None

def get_rag_system():
    global _cached
    if _cached is not None:
        return _cached

    backend_choice = os.getenv("RAG_BACKEND", "").lower()
    
    # 1. Force a specific backend if environment variable demands it
    if backend_choice == "azure_search":
        print("Using Azure AI Search Vector Database RAG.")
        from rag.azure_search_rag import AzureSearchRAGSystem
        _cached = AzureSearchRAGSystem()
        return _cached
    if backend_choice == "azure":
        print("Using Azure local embeddings RAG.")
        from rag.azure_rag import AzureRAGSystem
        _cached = AzureRAGSystem()
        return _cached
    if backend_choice == "gdx":
        print("Using GDX remote RAG.")
        from rag.gdx_rag import GDXRagSystem
        _cached = GDXRagSystem()
        return _cached
    if backend_choice == "keyword":
        print("Using fallback keyword RAG.")
        from rag.keyword_rag import KeywordRAGSystem
        _cached = KeywordRAGSystem()
        return _cached

    # 2. Auto-detect based on available credentials
    if os.getenv("AZURE_SEARCH_ENDPOINT") and os.getenv("AZURE_SEARCH_KEY"):
        print("Auto-detected Azure AI Search credentials. Using AzureSearchRAGSystem.")
        from rag.azure_search_rag import AzureSearchRAGSystem
        try:
            _cached = AzureSearchRAGSystem()
            return _cached
        except Exception as e:
            print(f"Failed to init AzureSearchRAGSystem: {e}")
        
    if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"):
        print("Auto-detected Azure OpenAI credentials. Using AzureRAGSystem.")
        from rag.azure_rag import AzureRAGSystem
        try:
            _cached = AzureRAGSystem()
            return _cached
        except Exception as e:
            print(f"Failed to init AzureRAGSystem: {e}")

    print("No Azure AI Search or Azure OpenAI credentials found (or they failed). Using fallback keyword RAG.")
    from rag.keyword_rag import KeywordRAGSystem
    _cached = KeywordRAGSystem()
    return _cached

