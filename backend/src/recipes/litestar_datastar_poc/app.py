"""
Litestar + Datastar POC

This demonstrates how Litestar and Datastar can simplify the stack:
- Litestar: More intuitive routing, built-in DI, less boilerplate
- Datastar: Hypermedia-driven reactivity without React/Vue/etc.
- Zero custom JavaScript: Everything is declarative
"""

import asyncio
import json
import os
from pathlib import Path
from typing import AsyncGenerator

from litestar import Litestar, get, post
from litestar.response import Stream
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.datastructures import State
from litestar.status_codes import HTTP_200_OK
from openai import AsyncOpenAI


async def get_openai_client(state: State) -> AsyncOpenAI:
    """Get OpenAI client from app state (dependency injection)"""
    endpoints = json.loads(os.getenv("COOKBOOK_ENDPOINTS", "[]"))
    if not endpoints:
        # Fallback for testing
        return AsyncOpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

    endpoint = endpoints[0]
    return AsyncOpenAI(base_url=endpoint["baseUrl"], api_key=endpoint["apiKey"])


@get("/")
async def index() -> dict:
    """Serve the main page with Datastar"""
    template_path = Path(__file__).parent / "templates" / "index.html"
    return {"content": template_path.read_text()}


@post("/chat")
async def chat(data: dict, state: State) -> Stream:
    """
    Handle chat messages and stream responses via Datastar SSE signals

    Litestar automatically:
    - Parses JSON body to dict
    - Validates required fields
    - Handles errors gracefully

    Datastar expects SSE events in this format:
    event: datastar-merge-signals
    data: {"response": "text here"}
    """
    message = data.get("message", "")
    if not message:
        # Send empty response signal
        async def empty():
            yield f'event: datastar-merge-signals\ndata: {{"response": "", "loading": false}}\n\n'
        return Stream(empty(), media_type="text/event-stream")

    async def generate_datastar_signals() -> AsyncGenerator[str, None]:
        """Generate Datastar-compatible SSE signals"""
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

                    # Send Datastar signal to update the store
                    signal_data = {
                        "response": full_response,
                        "loading": True
                    }
                    yield f"event: datastar-merge-signals\n"
                    yield f"data: {json.dumps(signal_data)}\n\n"

                    await asyncio.sleep(0.01)  # Smooth streaming

            # Send final signal with loading=false
            final_signal = {
                "response": full_response,
                "loading": False,
                "message": ""  # Clear the input
            }
            yield f"event: datastar-merge-signals\n"
            yield f"data: {json.dumps(final_signal)}\n\n"

        except Exception as e:
            error_signal = {
                "response": f"Error: {str(e)}",
                "loading": False
            }
            yield f"event: datastar-merge-signals\n"
            yield f"data: {json.dumps(error_signal)}\n\n"

    return Stream(
        generate_datastar_signals(),
        media_type="text/event-stream",
        status_code=HTTP_200_OK,
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@get("/health")
async def health() -> dict:
    """Health check endpoint"""
    return {
        "status": "ok",
        "framework": "litestar",
        "frontend": "datastar",
        "javascript_lines": 0
    }


# Litestar app - much simpler configuration than FastAPI!
app = Litestar(
    route_handlers=[index, chat, health],
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
