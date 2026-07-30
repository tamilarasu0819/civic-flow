"""
backend/vision_intelligence/routes/vision_router.py
FastAPI Router for Vision Intelligence Pipeline & SSE Streaming.
"""

import base64
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse

from schemas.vision import VisionAnalysisResponse, VisionAnalysisRequest
from services.image_processor import ImagePreprocessingError
from services.vision_service import analyze_image_bytes, stream_vision_analysis

router = APIRouter(prefix="/api/v1/vision", tags=["Vision Intelligence"])


@router.post(
    "/analyze",
    response_model=VisionAnalysisResponse,
    summary="Analyze Civic Image Asset (Synchronous REST)",
    description="Accepts an uploaded image file or Base64 string payload and returns structured visual intelligence telemetry."
)
async def analyze_image(
    file: Optional[UploadFile] = File(None, description="Image file asset (JPEG, PNG, WEBP, HEIC)"),
    image_base64: Optional[str] = Form(None, description="Optional Base64 string payload"),
    custom_prompt: Optional[str] = Form(None, description="Optional custom system prompt override")
):
    image_bytes: Optional[bytes] = None

    if file:
        image_bytes = await file.read()
    elif image_base64:
        try:
            # Strip data URI header if present (e.g. data:image/jpeg;base64,...)
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Base64 encoded payload: {str(e)}"
            )

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing image payload. Please provide an uploaded file or Base64 string."
        )

    try:
        response = await analyze_image_bytes(image_bytes, custom_prompt=custom_prompt)
        return response
    except ImagePreprocessingError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vision intelligence processing failure: {str(exc)}"
        )


@router.post(
    "/analyze-stream",
    summary="Analyze Civic Image Asset (Live SSE Thought Stream)",
    description="Streams real-time AI thought reasoning traces and final visual telemetry payload over Server-Sent Events (SSE)."
)
async def analyze_image_stream(
    file: Optional[UploadFile] = File(None, description="Image file asset (JPEG, PNG, WEBP, HEIC)"),
    image_base64: Optional[str] = Form(None, description="Optional Base64 string payload"),
    custom_prompt: Optional[str] = Form(None, description="Optional custom system prompt override")
):
    image_bytes: Optional[bytes] = None

    if file:
        image_bytes = await file.read()
    elif image_base64:
        try:
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Base64 encoded payload: {str(e)}"
            )

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing image payload. Please provide an uploaded file or Base64 string."
        )

    return StreamingResponse(
        stream_vision_analysis(image_bytes, custom_prompt=custom_prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
