import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routes import router

app = FastAPI(title="BookmarkAI Backend", version="0.1.0")
app.include_router(router, prefix="/api")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    html = """
    <html>
    <head>
        <title>BookmarkAI API</title>
        <style>
            body { background-color: #111; color: #eee; font-family: Arial, sans-serif; padding: 2rem; }
            a { color: #39f; }
            h1 { color: #39f; }
            pre { background: #222; padding: 1rem; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>BookmarkAI – AI‑organized bookmarks</h1>
        <p>FastAPI backend powering the BookmarkAI product.</p>
        <h2>Available Endpoints</h2>
        <pre>
GET  /health                           – health check
POST /api/bookmarks                    – create bookmark (AI summary & tags)
GET  /api/bookmarks/{id}               – retrieve a bookmark
GET  /api/bookmarks                    – list bookmarks (filters optional)
POST /api/ai/summarize                – raw summarization endpoint
POST /api/ai/tag                      – raw tag‑suggestion endpoint
POST /api/search                       – semantic search (future)
        </pre>
        <h2>Tech Stack</h2>
        <ul>
            <li>FastAPI 0.115.0</li>
            <li>SQLAlchemy 2.0.35 (synchronous)</li>
            <li>PostgreSQL (psycopg) – shared DB with prefix <code>bm_</code></li>
            <li>DigitalOcean Serverless Inference (model: openai-gpt-oss-120b)</li>
            <li>Python 3.12+</li>
        </ul>
        <p>Docs: <a href="/docs">Swagger UI</a> | <a href="/redoc">Redoc</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
