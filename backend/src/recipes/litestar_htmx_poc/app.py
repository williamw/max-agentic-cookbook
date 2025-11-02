"""
Litestar + HTMX + Hyperscript POC

This demonstrates the classic hypermedia approach:
- Litestar: Simple Python backend
- HTMX: Hypermedia-driven AJAX and SSE
- Hyperscript: Tiny bits of readable client-side scripting

HTMX is more mature and widely adopted than Datastar.
Hyperscript provides minimal scripting in a declarative style.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import AsyncGenerator

from litestar import Litestar, get, post
from litestar.response import Stream, Response
from litestar.datastructures import State
from litestar.status_codes import HTTP_200_OK
from openai import AsyncOpenAI


async def get_openai_client(state: State) -> AsyncOpenAI:
    """Get OpenAI client from app state"""
    endpoints = json.loads(os.getenv("COOKBOOK_ENDPOINTS", "[]"))
    if not endpoints:
        return AsyncOpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

    endpoint = endpoints[0]
    return AsyncOpenAI(base_url=endpoint["baseUrl"], api_key=endpoint["apiKey"])


@get("/")
async def index() -> Response:
    """Serve the main page with HTMX"""
    template_path = Path(__file__).parent / "templates" / "index.html"
    return Response(
        content=template_path.read_text(),
        media_type="text/html",
        status_code=HTTP_200_OK
    )


@post("/chat")
async def chat(data: dict, state: State) -> Stream:
    """
    Stream chat responses as SSE for HTMX

    HTMX expects SSE events with HTML fragments.
    We use the standard SSE format with 'message' events.
    """
    message = data.get("message", "")
    if not message:
        async def empty():
            yield "data: <div></div>\n\n"
        return Stream(empty(), media_type="text/event-stream")

    async def generate_sse() -> AsyncGenerator[str, None]:
        """Generate SSE events with HTML fragments for HTMX"""
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

                    # Send HTML fragment for HTMX to swap in
                    # Escape HTML entities to prevent XSS
                    safe_content = (
                        full_response
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace('"', "&quot;")
                        .replace("'", "&#39;")
                    )
                    html_fragment = f'<div class="response">{safe_content}</div>'

                    yield f"data: {html_fragment}\n\n"
                    await asyncio.sleep(0.01)

        except Exception as e:
            error_html = f'<div class="error">Error: {str(e)}</div>'
            yield f"data: {error_html}\n\n"

    return Stream(
        generate_sse(),
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
        "frontend": "htmx + hyperscript",
        "custom_js_lines": 0
    }


# Litestar app
app = Litestar(
    route_handlers=[index, chat, health],
    debug=True,
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8012,
        reload=True,
        log_level="info"
    )
