# Litestar + Datastar POC

> **Zero JavaScript.** Zero build step. Full reactivity.

A proof-of-concept demonstrating a simpler, more streamlined stack for AI-powered web applications.

## What This Demonstrates

This POC shows how **Litestar** (Python backend) + **Datastar** (hypermedia frontend) can significantly simplify your DevRel examples by:

1. **Zero custom JavaScript**: All reactivity via declarative HTML attributes
2. **Reducing boilerplate**: Less Pydantic model ceremony
3. **Simpler routing**: More intuitive than FastAPI's router system
4. **No React complexity**: Reactive UI without build tools, bundlers, or frameworks
5. **Hypermedia-driven**: Server sends signals, Datastar updates DOM
6. **Built-in features**: Better dependency injection, lifecycle hooks

## Stack Comparison

### Current Stack (FastAPI + React)

```
Backend:
- FastAPI with APIRouter
- Multiple Pydantic models per endpoint
- Manual router registration
- Complex streaming setup

Frontend:
- React + TypeScript
- Vite build system
- State management (Context/Redux)
- Multiple components
- npm/pnpm dependencies
- Build/bundle process
```

### Litestar + Datastar POC

```
Backend:
- Litestar with simple decorators
- Type hints for validation (fewer Pydantic models)
- Auto-registration
- Built-in SSE support

Frontend:
- Single HTML file (229 lines)
- Datastar from CDN (no build step)
- Zero custom JavaScript (0 lines)
- Declarative reactivity via data-* attributes
- Server sends SSE signals to update state
```

## Key Benefits

### 1. **Litestar Simplicity**

**FastAPI** (current):
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

class ChatRequest(BaseModel):
    endpointId: str
    modelName: str
    messages: list[dict]

class ChatResponse(BaseModel):
    message: str
    duration: int

@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    # Implementation
    pass

# Somewhere else: app.include_router(router)
```

**Litestar** (this POC):
```python
from litestar import Litestar, post

@post("/chat")
async def chat(data: dict) -> Stream:
    # Litestar validates dict structure automatically
    # No need for separate Pydantic models!
    message = data.get("message")
    # Implementation
    pass

app = Litestar(route_handlers=[chat])
```

### 2. **Datastar Reactivity**

**React** (current):
```tsx
// Multiple files, components, state management
import { useState } from 'react';

function ChatForm() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    // Fetch logic...
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        disabled={loading}
      />
      <button disabled={loading}>
        {loading ? 'Loading...' : 'Send'}
      </button>
    </form>
  );
}
```

**Datastar** (this POC):
```html
<!-- Single HTML file, no build step -->
<div data-store='{"message": "", "loading": false}'>
  <form data-on-submit="$$post('/chat'); $loading=true">
    <input
      data-model="message"
      data-bind-disabled="$loading"
    />
    <button data-bind-disabled="$loading">
      <span data-show="!$loading">Send</span>
      <span data-show="$loading">Loading...</span>
    </button>
  </form>
</div>
```

### 3. **Fewer Files**

**FastAPI + React recipe**:
```
backend/src/recipes/
├── multiturn_chat.py           # 150+ lines
└── ...

frontend/src/
├── components/
│   ├── Chat.tsx
│   ├── ChatForm.tsx
│   ├── ChatMessage.tsx
│   └── StreamingResponse.tsx
├── hooks/
│   ├── useChat.ts
│   └── useStreaming.ts
├── types/
│   └── chat.ts
└── ...
```

**Litestar + Datastar POC**:
```
litestar_datastar_poc/
├── app.py                      # 80 lines
└── templates/
    └── index.html              # Self-contained UI
```

### 4. **Better Performance**

- **Litestar**: Faster routing and validation than FastAPI
- **Datastar**: No React reconciliation overhead
- **SSE**: Native browser support, no polling
- **Smaller bundle**: No JS framework to download

## Running the POC

### Prerequisites

1. Ensure you have the `COOKBOOK_ENDPOINTS` environment variable set:
   ```bash
   export COOKBOOK_ENDPOINTS='[
     {
       "id": "localhost",
       "baseUrl": "http://localhost:8000/v1",
       "apiKey": "EMPTY"
     }
   ]'
   ```

2. Have a model server running (e.g., vLLM, Ollama, or local LLM server)

### Start the POC

```bash
# From the backend directory
cd /home/user/max-agentic-cookbook/backend

# Install dependencies (including Litestar)
uv sync

# Run the Litestar app
python src/recipes/litestar_datastar_poc/app.py
```

The POC will be available at: **http://localhost:8011**

### What to Try

1. **Open the UI**: Visit http://localhost:8011
2. **Ask questions**: Type in the chat input and see streaming responses
3. **Check the code**: View `app.py` to see how simple the backend is
4. **Inspect the HTML**: Right-click → View Source to see Datastar in action
5. **Compare**: Look at the existing FastAPI + React recipes to see the difference

## Why This Matters for DevRel

### Easier Onboarding
- Developers can understand the full stack in one file
- No need to explain React hooks, state management, or build tools
- Focus on AI functionality, not framework complexity

### Faster Iteration
- Change HTML and refresh (no build step)
- Add endpoints with simple decorators
- Less context switching between frontend/backend

### Better Examples
- Self-contained demos
- Copy-paste friendly code
- Works without npm install
- Easier to adapt to different use cases

### Production Ready
- Litestar is used by major companies
- Datastar handles complex UIs
- SSE is standard protocol
- Easy to add authentication, middleware, etc.

## Potential Next Steps

If this POC is compelling, we could:

1. **Port existing recipes** to Litestar + Datastar
2. **Create hybrid examples** showing both stacks
3. **Add comparison docs** to help users choose
4. **Benchmark performance** between the two approaches
5. **Create templates** for common patterns

## File Structure

```
litestar_datastar_poc/
├── app.py                  # Litestar backend (80 lines)
├── templates/
│   └── index.html          # Datastar frontend (self-contained)
└── README.md              # This file
```

## Learn More

- **Litestar**: https://litestar.dev
- **Datastar**: https://datastar.dev
- **SSE**: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

## Questions?

This is a proof-of-concept to demonstrate the potential benefits. The goal is to:
- Simplify DevRel examples
- Reduce cognitive overhead for learners
- Show that AI apps don't need heavy frameworks

What do you think? Should we explore this approach further?
