"""LLM-calling wrapper.

Two backends, selected at runtime:

1. ``hermes``  — when running inside the Hermes desktop app the agent itself can
   simply invoke this module's ``llm_complete`` from its own context. The
   ``hermes`` backend just records the call (no nested LLM in the demo) and
   returns a deterministic mock so the tool still runs end-to-end.

2. ``openai``  — when the ``OPENAI_API_KEY`` env var is set, calls go to the
   OpenAI Chat Completions API at ``gpt-4o-mini`` (cheap + fast, fine for tool
   use). Any OpenAI-compatible endpoint can be selected via ``OPENAI_BASE_URL``.

3. ``mock``    — deterministic stub for tests and offline runs. Returns the
   prompt's last user message verbatim, prefixed with ``"[mock] "``.

The CLI lets the caller pick a backend with ``--backend {mock,openai,hermes}``.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

BACKEND = os.environ.get("MRNA_AI_LLM_BACKEND", "auto").lower()


def _detect_backend() -> str:
    if BACKEND in {"mock", "openai", "hermes"}:
        return BACKEND
    # auto
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "mock"


def llm_complete(
    prompt: str,
    *,
    system: str = "",
    json_mode: bool = False,
    temperature: float = 0.2,
    max_tokens: int = 800,
    backend: str | None = None,
) -> str:
    """Return a single LLM completion for ``prompt``.

    Backend selection: explicit ``backend`` arg > ``MRNA_AI_LLM_BACKEND`` env
    > auto-detect.
    """
    backend = backend or _detect_backend()

    if backend == "mock":
        # Deterministic offline stub: extract a structured guess from the prompt.
        return _mock_complete(prompt, system=system, json_mode=json_mode)

    if backend == "openai":
        return _openai_complete(
            prompt,
            system=system,
            json_mode=json_mode,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if backend == "hermes":
        # Inside the Hermes app, the assistant already IS the LLM. We surface
        # a clear error so the operator knows to switch backends.
        raise RuntimeError(
            "backend='hermes' is reserved for the assistant's own context. "
            "Use backend='openai' with OPENAI_API_KEY, or backend='mock' for "
            "offline runs."
        )

    raise ValueError(f"unknown backend: {backend!r}")


# ---------- mock backend ----------------------------------------------------


def _mock_complete(prompt: str, *, system: str = "", json_mode: bool = False) -> str:
    """Deterministic stub. Parses the prompt for obvious structured fields."""
    text = prompt.lower()
    if json_mode or "return json" in text or "json object" in text:
        # Heuristic: extract the first peptide or HLA mentioned.
        import re

        hla = re.search(r"hla[-_][a-z0-9*:.]+", prompt, re.I)
        pep = re.search(r"peptide\s*[:=]\s*([A-Z]{8,11})", prompt)
        var = re.search(r"variant\s*[:=]\s*([A-Z]\d+[A-Z])", prompt)
        if pep and hla:
            guess = {
                "peptide": pep.group(1),
                "hla": hla.group(0),
                "binding_affinity_nM": 250.0 if "A*02" in hla.group(0) else 800.0,
                "binder": True if "A*02" in hla.group(0) else False,
                "immunogenicity_score": 0.55,
                "rationale": "[mock] HLA-A*02:01 favors hydrophobic anchors at P2/P9.",
            }
            return json.dumps(guess)
        if var:
            return json.dumps(
                {
                    "variant": var.group(1),
                    "immunogenic": True,
                    "rationale": "[mock] missense variant in known tumor-suppressor locus.",
                }
            )
        # Generic structured answer for trial matching
        return json.dumps(
            {
                "eligible": True,
                "score": 0.7,
                "reasons": ["[mock] biomarker matches inclusion criterion"],
            }
        )
    return "[mock] " + prompt.strip().splitlines()[-1][:200]


# ---------- openai backend --------------------------------------------------


def _openai_complete(
    prompt: str,
    *,
    system: str,
    json_mode: bool,
    temperature: float,
    max_tokens: int,
) -> str:
    api_key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    body: dict[str, Any] = {
        "model": model,
        "messages": ([{"role": "system", "content": system}] if system else [])
        + [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenAI HTTP {e.code}: {e.read().decode()[:500]}") from e

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"unexpected OpenAI response: {data}") from e


def llm_json(prompt: str, **kwargs: Any) -> dict[str, Any]:
    """Convenience: call ``llm_complete`` with json_mode=True and parse."""
    raw = llm_complete(prompt, json_mode=True, **kwargs)
    # Strip code fences if any
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"LLM did not return valid JSON: {raw[:300]!r}") from e
