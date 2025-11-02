"""
Litestar + Datastar POC

This demonstrates how Litestar and Datastar can simplify the stack:
- Litestar: More intuitive routing, built-in DI, less boilerplate
- Datastar: Hypermedia-driven reactivity without React/Vue/etc.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import AsyncGenerator

from litestar import Litestar, get, post
from litestar.response import Stream, Template
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.datastructures import State
from openai import AsyncOpenAI


# Simple data classes - no need for complex Pydantic models
# Litestar handles validation via type hints
async def get_openai_client(state: State) -> AsyncOpenAI:
    """Get OpenAI client from app state (dependency injection)"""
    endpoints = json.loads(os.getenv("COOKBOOK_ENDPOINTS", "[]"))
    if not endpoints:
        # Fallback for testing
        return AsyncOpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

    endpoint = endpoints[0]
    return AsyncOpenAI(base_url=endpoint["baseUrl"], api_key=endpoint["apiKey"])


@get("/")
async def index() -> Template:
    """Serve the main page with Datastar"""
    return Template(name="index.html")


@post("/chat")
async def chat(data: dict, state: State) -> Stream:
    """
    Handle chat messages and stream responses via SSE

    Litestar automatically:
    - Parses JSON body to dict
    - Validates required fields
    - Handles errors gracefully

    No need for separate Pydantic request/response models!
    """
    message = data.get("message", "")
    if not message:
        return Stream(iter([]))

    async def generate_sse() -> AsyncGenerator[str, None]:
        """Generate SSE events for Datastar"""
        client = await get_openai_client(state)

        try:
            stream = await client.chat.completions.create(
                model="meta-llama/Llama-3.2-3B-Instruct",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Keep responses concise."},
                    {"role": "user", "content": message}
                ],
                stream=True,
            )

            full_response = ""
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content

                    # Datastar SSE format: send HTML fragments
                    fragment = f'<div id="response" class="response">{full_response}</div>'
                    yield f"data: {json.dumps({'fragment': fragment})}\n\n"

                    await asyncio.sleep(0.01)  # Smooth streaming

            # Send final state
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_fragment = f'<div id="response" class="error">Error: {str(e)}</div>'
            yield f"data: {json.dumps({'fragment': error_fragment})}\n\n"

    return Stream(generate_sse(), media_type="text/event-stream")


@get("/health")
async def health() -> dict:
    """Health check endpoint"""
    return {"status": "ok", "framework": "litestar", "frontend": "datastar"}


# Litestar app - much simpler configuration than FastAPI!
app = Litestar(
    route_handlers=[index, chat, health],
    template_config=TemplateConfig(
        directory=Path(__file__).parent / "templates",
        engine=JinjaTemplateEngine,
    ),
    debug=True,
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8011,
        reload=True,
        log_level="info"
    )
