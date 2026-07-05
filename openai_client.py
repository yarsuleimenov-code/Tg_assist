import logging

import aiohttp

from prompts import SYSTEM_PROMPT, build_user_prompt


class OpenAIClient:
    def __init__(self, api_key: str, api_base: str, model: str) -> None:
        self.api_key = api_key
        self.api_base = api_base
        self.model = model

    async def generate_answer(
        self,
        question: str,
        context: str,
        recent_user_messages: list[str],
    ) -> str:
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "max_tokens": 500,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(
                        question=question,
                        context=context,
                        recent_user_messages=recent_user_messages,
                    ),
                },
            ],
        }

        timeout = aiohttp.ClientTimeout(total=45)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response_text = await response.text()
                if response.status >= 400:
                    logging.error("DeepSeek API error %s: %s", response.status, response_text)
                    raise RuntimeError("DeepSeek API request failed")

                data = await response.json()

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            logging.error("Unexpected DeepSeek API response: %s", data)
            raise RuntimeError("Unexpected DeepSeek API response") from exc
