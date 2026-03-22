# llm_module/client_instance.py
_client_instance = None


def get_client():
    """Get the global Ollama Client instance."""
    return _client_instance


def set_client(client):
    """Set the global Ollama Client instance."""
    global _client_instance
    _client_instance = client
