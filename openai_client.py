import logging

import aiohttp

from prompts import (
    INTENT_ROUTER_SYSTEM_PROMPT,
    PORTFOLIO_SYSTEM_PROMPT,
    PROFESSIONAL_SYSTEM_PROMPT,
    build_intent_prompt,
    build_portfolio_prompt,
    build_professional_prompt,
)


class OpenAIClient:
    def __init__(self, api_key: str, api_base: str, model: str) -> None:
        self.api_key = api_key
        self.api_base = api_base
        self.model = model

    async def generate_answer(
        self,
        question: str,
        context: str,
        memory_context: str,
    ) -> str:
        return await self._chat_completion(
            system_prompt=PORTFOLIO_SYSTEM_PROMPT,
            user_prompt=build_portfolio_prompt(
                question=question,
                context=context,
                memory_context=memory_context,
            ),
            temperature=0.2,
            max_tokens=500,
        )

    async def generate_professional_answer(
        self,
        question: str,
        memory_context: str,
    ) -> str:
        return await self._chat_completion(
            system_prompt=PROFESSIONAL_SYSTEM_PROMPT,
            user_prompt=build_professional_prompt(
                question=question,
                memory_context=memory_context,
            ),
            temperature=0.4,
            max_tokens=430,
        )

    async def classify_intent(self, question: str) -> str:
        return await self._chat_completion(
            system_prompt=INTENT_ROUTER_SYSTEM_PROMPT,
            user_prompt=build_intent_prompt(question),
            temperature=0.0,
            max_tokens=20,
        )

    async def _chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        payload = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
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
