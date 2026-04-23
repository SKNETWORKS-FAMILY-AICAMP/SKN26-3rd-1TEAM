import asyncio
import traceback
from pprint import pformat
from langchain_core.messages import BaseMessage

from exaone import exaone_infer


def call_runpod_ollama(messages: list[BaseMessage]) -> str:
    """
    RunPod Serverless를 호출하여 EXAONE 추론 결과를 가져옵니다.
    """
    try:
        payload = {
            "input": {
                "messages": messages,
                "temperature": 0.7,
            }
        }

        result = asyncio.run(exaone_infer(payload))

        print("DEBUG result:")
        print(pformat(result, width=120))

        if not isinstance(result, dict):
            raise TypeError(
                f"unexpected response type: {type(result).__name__}, value={result!r}"
            )

        if result.get("ok") is True:
            return result.get("text", "")

        error_msg = result.get("error", "생성이 제대로 되지 않았습니다.")
        raise RuntimeError(error_msg)

    except Exception as e:
        print("DEBUG traceback:")
        traceback.print_exc()
        return f"Error: Failed to call Runpod Serverless - {type(e).__name__}: {e}"
