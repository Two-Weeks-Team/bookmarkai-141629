import os
import json
import re
import httpx
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Helper to pull JSON out of markdown code blocks or raw text
# ---------------------------------------------------------------------------
def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

# ---------------------------------------------------------------------------
# Core inference caller (async)
# ---------------------------------------------------------------------------
_INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
_API_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")

async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    payload = {
        "model": _MODEL,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(_INFERENCE_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # Expected response shape: {"choices": [{"message": {"content": "..."}}]}
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_str = _extract_json(content)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Return raw text as note if JSON parsing fails
                return {"note": "Failed to parse AI response as JSON", "raw": content}
    except Exception as e:
        # Any error results in a graceful fallback dict
        return {"note": f"AI service temporarily unavailable: {str(e)}"}

# ---------------------------------------------------------------------------
# Public helpers used by routes
# ---------------------------------------------------------------------------
async def generate_summary(url: str, detail_level: str = "one_sentence") -> Dict[str, Any]:
    # Build a prompt that asks the model to return JSON with a "summary" field (and optional detailed)
    if detail_level == "expanded":
        instruction = (
            "Provide a concise 1‑sentence summary and then an expanded 3‑5 sentence version."
        )
    else:
        instruction = "Provide a concise 1‑sentence summary."
    prompt = (
        f"Summarize the content at the following URL. Return a JSON object with keys "
        f"'summary' (string) and, if expanded, 'detailed_summary' (string).\nURL: {url}\n{instruction}"
    )
    messages = [{"role": "user", "content": prompt}]
    return await _call_inference(messages, max_tokens=512)

async def suggest_tags(text: str) -> Dict[str, Any]:
    # Prompt to produce a JSON list of tags under the key "tags"
    prompt = (
        "Given the following text, generate a list of hierarchical tags that describe the main topics. "
        "Return a JSON object with a single key 'tags' containing an array of strings.\n\n"
        f"Text:\n{text}"
    )
    messages = [{"role": "user", "content": prompt}]
    return await _call_inference(messages, max_tokens=512)
