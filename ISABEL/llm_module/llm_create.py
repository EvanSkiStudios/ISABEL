import os
import sys
from types import SimpleNamespace

from dotenv import load_dotenv
from ollama import Client

from utility_scripts.system_logging import setup_logger

from llm_module.system_prompts import personality_system_prompt

# configure logging
logger = setup_logger(__name__)

load_dotenv()
os.environ["OLLAMA_API_KEY"] = os.getenv("OLLAMA_API")


def ns(d: dict) -> SimpleNamespace:
    return SimpleNamespace(**{
        k: ns(v) if isinstance(v, dict) else v for k, v in d.items()
    })


# model settings for easy swapping
llm_config = {
    "ISABEL": {
        "MODEL_NAME": "ISABEL",
        "OLLAMA_MODEL": "huihui_ai/deepseek-r1-abliterated",
        "VISION_MODEL": "qwen3-vl:4b",
        "TOOL_MODEL": "qwen3-vl:4b",
        "DEFAULT_CONTEXT": 8192,
        "DEFAULT_TEMPERATURE": 0.6
    }
}
LLM_CONFIG = ns(llm_config)


def get_llm_config():
    return LLM_CONFIG


def llm_create():
    try:
        client = Client(
            headers={"Authorization": f"Bearer {os.getenv('OLLAMA_API')}"}
        )
        response = client.create(
            model=LLM_CONFIG.ISABEL.MODEL_NAME,
            from_=LLM_CONFIG.ISABEL.OLLAMA_MODEL,
            system=personality_system_prompt,
            stream=False,
        )
        logger.info(f"# Client Response: {response.status}")
        return client

    except ConnectionError as e:
        logger.error('Ollama is not running!')
        sys.exit(1)  # Exit program with error code 1

    except Exception as e:
        # Catches any other unexpected errors
        logger.error("❌ An unexpected error occurred:", e)
        sys.exit(1)
