import os
import sys

from dotenv import load_dotenv
from ollama import Client

from utility_scripts.namespace_utility import namespace
from utility_scripts.system_logging import setup_logger

from llm_module.system_prompts import personality_system_prompt

# configure logging
logger = setup_logger(__name__)

load_dotenv()
os.environ["OLLAMA_API_KEY"] = os.getenv("OLLAMA_API")


# model settings for easy swapping
llm_config = {
    "ISABEL": {
        "MODEL_NAME": "ISABEL",
        # "OLLAMA_MODEL": "huihui_ai/deepseek-r1-abliterated",
        "OLLAMA_MODEL": "qwen3.5:397b-cloud",
        "VISION_MODEL": "qwen3.5:397b-cloud",
        "TOOL_MODEL": "qwen3.5:397b-cloud",
        "DEFAULT_CONTEXT": 16384,
        "DEFAULT_TEMPERATURE": 0.6
    }
}
LLM_CONFIG = namespace(llm_config)


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
