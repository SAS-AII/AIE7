from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
import openai
from typing import List, Optional
import os
import asyncio


class EmbeddingModel:
    def __init__(self, embeddings_model_name: str = "text-embedding-3-small", api_key: Optional[str] = None):
        load_dotenv()
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.embeddings_model_name = embeddings_model_name
        
        # Initialize clients only if API key is available
        if self.openai_api_key:
            self.async_client = AsyncOpenAI(api_key=self.openai_api_key)
            self.client = OpenAI(api_key=self.openai_api_key)
            openai.api_key = self.openai_api_key
        else:
            self.async_client = None
            self.client = None
            
        self.embeddings_model_name = embeddings_model_name

    def _ensure_client(self):
        """Ensure clients are initialized, raise error if not"""
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please provide it via parameter or environment variable."
            )
        if not self.async_client or not self.client:
            self.async_client = AsyncOpenAI(api_key=self.openai_api_key)
            self.client = OpenAI(api_key=self.openai_api_key)

    async def async_get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
        self._ensure_client()
        response = await self.async_client.embeddings.create(
            input=list_of_text, model=self.embeddings_model_name
        )
        return [embedding.embedding for embedding in response.data]

    async def async_get_embedding(self, text: str) -> List[float]:
        self._ensure_client()
        response = await self.async_client.embeddings.create(
            input=[text], model=self.embeddings_model_name
        )
        return response.data[0].embedding

    def get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
        self._ensure_client()
        response = self.client.embeddings.create(
            input=list_of_text, model=self.embeddings_model_name
        )
        return [embedding.embedding for embedding in response.data]

    def get_embedding(self, text: str) -> List[float]:
        self._ensure_client()
        response = self.client.embeddings.create(
            input=[text], model=self.embeddings_model_name
        )
        return response.data[0].embedding

    async def async_get_embeddings_with_backoff(self, list_of_text: List[str]) -> List[List[float]]:
        """Get embeddings with exponential backoff for rate limiting"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return await self.async_get_embeddings(list_of_text)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
        return []


if __name__ == "__main__":
    embedding_model = EmbeddingModel()
    print(asyncio.run(embedding_model.async_get_embedding("Hello, world!")))
    print(
        asyncio.run(
            embedding_model.async_get_embeddings(["Hello, world!", "Goodbye, world!"])
        )
    )
