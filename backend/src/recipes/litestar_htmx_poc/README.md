# Litestar + HTMX + Hyperscript POC

> **The classic hypermedia approach.** Battle-tested, widely adopted, minimal scripting.

A proof-of-concept demonstrating the mature hypermedia stack for AI-powered web applications.

## What This Demonstrates

This POC shows how **Litestar** (Python backend) + **HTMX** (hypermedia AJAX) + **Hyperscript** (tiny scripting) creates a simple, powerful stack:

1. **HTMX for hypermedia**: More mature than Datastar, widely adopted
2. **Hyperscript for scripting**: Tiny bits of readable client-side logic
3. **HTML fragments**: Server sends HTML, not JSON
4. **SSE streaming**: Built-in with `hx-ext="sse"`
5. **Progressive enhancement**: Works without JavaScript (degrades gracefully)
6. **Battle-tested**: Production-ready, great documentation

## HTMX vs Datastar: Which to Choose?

We now have two hypermedia POCs in this repo. Here's how they compare:

### HTMX Approach (This POC)

**Strengths:**
- ✅ More mature (2020 vs 2023)
- ✅ Larger community and ecosystem
- ✅ Better documentation and examples
- ✅ More extensions available
- ✅ Battle-tested in production
- ✅ Progressive enhancement built-in
- ✅ Works with any backend framework

**Trade-offs:**
- ⚠️ Hyperscript needed for client-side state/logic
- ⚠️ More attributes to learn (`hx-target`, `hx-swap`, etc.)
- ⚠️ SSE requires extension (`hx-ext="sse"`)

**Best for:**
- Production applications
- Teams new to hypermedia
- Projects needing progressive enhancement
- When community support matters

### Datastar Approach (../litestar_datastar_poc)

**Strengths:**
- ✅ Newer, modern design
- ✅ Built-in client-side state (signals)
- ✅ Zero custom JavaScript possible
- ✅ SSE streaming native
- ✅ Cleaner syntax for some use cases
- ✅ Smaller API surface

**Trade-offs:**
- ⚠️ Newer = smaller community
- ⚠️ Fewer examples and resources
- ⚠️ Less production usage
- ⚠️ Evolving API (less stable)

**Best for:**
- Greenfield projects
- When you want built-in state management
- Simpler apps with less complex interactions
- Experimenting with cutting-edge hypermedia

## Stack Overview

```
Backend:
- Litestar with simple decorators (113 lines)
- Type hints for validation
- SSE streaming with HTML fragments

Frontend:
- HTMX from CDN (hypermedia AJAX)
- Hyperscript from CDN (minimal scripting)
- Single HTML file (240 lines)
- ~10 lines of hyperscript for behaviors
```

## Key Concepts

### 1. HTMX Attributes

HTMX uses declarative attributes to enable AJAX:

```html
<button
    hx-post="/chat"          <!-- POST to this endpoint -->
    hx-target="#response"    <!-- Put response here -->
    hx-swap="innerHTML"      <!-- How to swap content -->
>
    Send
</button>
```

### 2. Server-Sent Events with HTMX

```html
<button
    hx-ext="sse"            <!-- Enable SSE extension -->
    sse-connect="/chat"      <!-- Connect to SSE endpoint -->
    sse-swap="message"       <!-- Listen for 'message' events -->
    hx-target="#response"
>
```

### 3. Hyperscript for Client Logic

Instead of vanilla JavaScript:

```javascript
// Vanilla JS (verbose)
document.addEventListener('htmx:afterRequest', function(e) {
    document.getElementById('message-input').value = '';
    document.getElementById('message-input').disabled = false;
});
```

Use hyperscript (readable):

```html
<button _="on htmx:afterRequest
           set #message-input.value to ''
           set #message-input.disabled to false">
```

### 4. Server Returns HTML

Backend sends HTML fragments, not JSON:

```python
# Python backend
html_fragment = f'<div class="response">{content}</div>'
yield f"data: {html_fragment}\n\n"
```

HTMX automatically swaps this into the target element.

## Comparison with React

### React Approach

```tsx
// Multiple files, components, hooks, state management
import { useState, useEffect } from 'react';

function Chat() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const res = await fetch('/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });

    const reader = res.body.getReader();
    // ... 30+ more lines of streaming logic

    setLoading(false);
    setMessage('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={message}
        onChange={e => setMessage(e.target.value)}
        disabled={loading}
      />
      <button disabled={loading}>Send</button>
      <div>{response}</div>
    </form>
  );
}
```

### HTMX + Hyperscript Approach

```html
<!-- Single HTML file -->
<form hx-ext="sse">
  <input name="message" id="msg" />
  <button
    hx-post="/chat"
    sse-connect="/chat"
    sse-swap="message"
    hx-target="#response"
    _="on htmx:afterRequest set #msg.value to ''"
  >
    Send
  </button>
  <div id="response"></div>
</form>
```

Much simpler, no build step, no framework.

## File Structure Comparison

### FastAPI + React (Current)
```
backend/src/recipes/multiturn_chat.py      # 150+ lines
frontend/src/
  ├── components/
  │   ├── Chat.tsx
  │   ├── ChatForm.tsx
  │   ├── ChatMessage.tsx
  │   └── StreamingResponse.tsx
  ├── hooks/
  │   ├── useChat.ts
  │   └── useStreaming.ts
  └── types/chat.ts
```

### Litestar + HTMX (This POC)
```
litestar_htmx_poc/
  ├── app.py           # 113 lines
  └── templates/
      └── index.html   # 240 lines (includes styles)
```

## Running the POC

### Prerequisites

1. Set up environment variable:
   ```bash
   export COOKBOOK_ENDPOINTS='[
     {
       "id": "localhost",
       "baseUrl": "http://localhost:8000/v1",
       "apiKey": "EMPTY"
     }
   ]'
   ```

2. Have a model server running (vLLM, Ollama, etc.)

### Start the POC

```bash
# From the backend directory
cd /home/user/max-agentic-cookbook/backend

# Install dependencies (already done if you ran Datastar POC)
uv sync

# Run the HTMX app
python src/recipes/litestar_htmx_poc/app.py
```

The POC will be available at: **http://localhost:8012**

### What to Try

1. **Open the UI**: Visit http://localhost:8012
2. **Ask questions**: See streaming responses via SSE
3. **View source**: See how clean the HTMX attributes are
4. **Compare**: Open the Datastar POC (port 8011) side-by-side
5. **Inspect network**: Watch HTML fragments streaming in

## Why HTMX + Hyperscript?

### For DevRel Examples

**Pros:**
- More developers know HTMX
- Better onboarding materials
- Easier to find help/examples
- More "production-ready" feel
- Progressive enhancement story

**Cons:**
- Slightly more verbose than Datastar
- Need hyperscript for client-side logic
- More concepts to learn (extensions, etc.)

### For Production Apps

HTMX is the safer choice:
- Used by Basecamp, GitHub, and others
- Active development and maintenance
- Stable API, unlikely to break
- Great performance characteristics
- Works with any backend

## HTMX vs Datastar: Side-by-Side

| Feature | HTMX | Datastar |
|---------|------|----------|
| **Maturity** | 4 years, stable | 1 year, evolving |
| **Community** | Large, active | Small, growing |
| **Docs** | Excellent | Good |
| **Client State** | Via hyperscript | Built-in (signals) |
| **SSE Support** | Via extension | Native |
| **Attributes** | Many (`hx-*`) | Fewer (`data-*`) |
| **Learning Curve** | Moderate | Gentle |
| **Production Use** | Extensive | Limited |
| **Progressive Enhancement** | Yes | Partial |

## When to Use What

**Use HTMX when:**
- Building production applications
- Team is new to hypermedia
- You want battle-tested tech
- Progressive enhancement matters
- You need extensive examples

**Use Datastar when:**
- Building experimental/greenfield apps
- You want built-in state management
- Simpler syntax appeals to you
- You like cutting-edge tech
- App is simple/medium complexity

**Use React when:**
- Building complex SPAs
- Need offline-first capabilities
- Heavy client-side logic
- Large existing React ecosystem
- Team already knows React well

## Learn More

- **HTMX**: https://htmx.org
- **Hyperscript**: https://hyperscript.org
- **Litestar**: https://litestar.dev
- **HTMX Examples**: https://htmx.org/examples/

## Both POCs Together

This repo now has **both** approaches:

```
backend/src/recipes/
├── litestar_datastar_poc/    # Modern, minimal
└── litestar_htmx_poc/        # Classic, mature
```

Try both! See which feels better for your use case. Both are vastly simpler than FastAPI + React.

## Questions?

These POCs demonstrate that you don't need heavy frameworks for AI web apps. Whether you choose HTMX or Datastar, you get:

- ✅ Simpler code
- ✅ Faster development
- ✅ Easier debugging
- ✅ Better performance
- ✅ No build step
- ✅ Less to learn

The hypermedia approach is worth considering for DevRel examples!
