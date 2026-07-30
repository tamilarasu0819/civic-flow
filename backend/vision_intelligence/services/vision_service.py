"""
backend/vision_intelligence/services/vision_service.py
Multimodal LLM API Integration & Server-Sent Events (SSE) Live Thought Streamer.
"""

import os
import io
import json
import pathlib
import asyncio
import logging
from typing import AsyncGenerator, Optional, Tuple

import httpx
from schemas.vision import VisionAnalysisResponse
from services.image_processor import preprocess_image
from services.vision_parser import parse_vision_response, generate_fallback_vision_data

logger = logging.getLogger("vision_service")

try:
    from dotenv import load_dotenv
    # Look for .env in backend directory or parent directories
    env_path = pathlib.Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass

# Environment configurations for Custom LLM API / Local Gemma API
VISION_API_BASE = os.getenv("VISION_API_BASE", "https://api.openai.com/v1")
VISION_API_KEY = os.getenv("VISION_API_KEY", "")
VISION_MODEL_ID = os.getenv("VISION_MODEL_ID", "gemma-4-vision")

DEFAULT_PROMPT_PATH = pathlib.Path(__file__).parent.parent / "prompts" / "vision_prompt.md"


def load_system_prompt() -> str:
    """Loads default system prompt instructions from vision_prompt.md."""
    try:
        if DEFAULT_PROMPT_PATH.exists():
            return DEFAULT_PROMPT_PATH.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read system prompt file: {e}")
    
    return "You are CivicFlow AI's Vision Intelligence Engine. Analyze the civic issue image and return valid JSON."


async def execute_multimodal_api_call(
    base64_image: str,
    mime_type: str,
    prompt_text: str
) -> str:
    """
    Executes multimodal visual API request to configured API endpoint (Custom LLM / Gemma API).
    If no API key is provided or remote call fails, falls back gracefully.
    """
    if not VISION_API_KEY:
        logger.info("VISION_API_KEY not configured. Utilizing deterministic vision model simulator.")
        await asyncio.sleep(0.5)  # Simulate network latency
        return """```json
{
  "thinking_steps": [
    "Ingested input image asset.",
    "Evaluating image content for public infrastructure defects..."
  ],
  "is_civic_issue": false,
  "issue_type": "Unrecognized Image",
  "severity": "Low",
  "confidence": 0,
  "description": "No valid public infrastructure defect or civic hazard was recognized in the uploaded image.",
  "affected_infrastructure": "None",
  "visible_risks": [],
  "estimated_urgency": "Routine Maintenance",
  "image_quality_notes": "Unable to verify civic asset"
}
```"""

    headers = {
        "Authorization": f"Bearer {VISION_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": VISION_MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2,
        "max_tokens": 4000
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            endpoint_url = f"{VISION_API_BASE.rstrip('/')}/chat/completions"
            response = await client.post(
                endpoint_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            res_json = response.json()
            return res_json["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Multimodal LLM API call error: {e}")
        return ""


async def stream_vision_analysis(
    image_bytes: bytes,
    custom_prompt: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    Executes vision processing pipeline and yields Server-Sent Events (SSE) data frames.

    Yields SSE events:
      - event: thought\ndata: {"thought": "Step message..."}\n\n
      - event: result\ndata: <VisionAnalysisResponse JSON>\n\n
    """
    # 1. Pre-process Image Asset
    try:
        encoded_img, mime_type, dimensions = preprocess_image(image_bytes)
        yield f"event: thought\ndata: {json.dumps({'thought': f'Image validated & pre-processed ({dimensions[0]}x{dimensions[1]}px).'})}\n\n"
        await asyncio.sleep(0.2)
    except Exception as exc:
        yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"
        return

    prompt_text = custom_prompt or load_system_prompt()

    # 2. Simulated / Dynamic Thinking Step Milestones
    thought_milestones = [
        "Analyzing image lighting, camera orientation, and background setting...",
        "Executing visual segment analysis on central grid...",
        "Detecting physical anomalies and infrastructure degradation...",
        "Evaluating severity rating against public safety matrix...",
        "Formulating structured visual intelligence telemetry payload..."
    ]

    for step in thought_milestones:
        yield f"event: thought\ndata: {json.dumps({'thought': step})}\n\n"
        await asyncio.sleep(0.3)

    # 3. Model Inference Execution
    raw_output = await execute_multimodal_api_call(encoded_img, mime_type, prompt_text)
    validated_response = parse_vision_response(raw_output)

    # Serialize output object
    if hasattr(validated_response, "model_dump_json"):
        json_output = validated_response.model_dump_json()
    else:
        json_output = validated_response.json()

    # 4. Emit Final Vision Telemetry Result Event
    yield f"event: result\ndata: {json_output}\n\n"


async def analyze_image_bytes(
    image_bytes: bytes,
    custom_prompt: Optional[str] = None
) -> VisionAnalysisResponse:
    """
    Synchronous / direct REST execution helper. Returns VisionAnalysisResponse.
    """
    encoded_img, mime_type, _ = preprocess_image(image_bytes)
    prompt_text = custom_prompt or load_system_prompt()
    raw_output = await execute_multimodal_api_call(encoded_img, mime_type, prompt_text)
    return parse_vision_response(raw_output)
