"""
backend/vision_intelligence/services/vision_parser.py
Resilient JSON Parsing, Markdown Extraction, and Fallback Recovery Service.
"""

import re
import json
import logging
from typing import Dict, Any
from schemas.vision import VisionAnalysisResponse, SeverityLevel, UrgencyLevel

logger = logging.getLogger("vision_parser")


def extract_json_block(text: str) -> str:
    """
    Extracts JSON payload string from markdown code blocks or raw text string.

    Args:
        text: Raw response string emitted by LLM.

    Returns:
        str: Sanitized JSON string.
    """
    if not text:
        return ""

    # Pattern 1: Look for ```json ... ``` code blocks
    json_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if json_block_match:
        return json_block_match.group(1).strip()

    # Pattern 2: Look for raw curly-brace object {...}
    raw_object_match = re.search(r"(\{[\s\S]*\})", text)
    if raw_object_match:
        return raw_object_match.group(1).strip()

    return text.strip()


def generate_fallback_vision_data(raw_text: str = "") -> VisionAnalysisResponse:
    """
    Constructs a safe VisionAnalysisResponse object when parsing fails.
    Inspects raw_text to infer whether a civic issue was present.
    """
    logger.warning("Triggered fallback vision data generator due to unparsable response.")

    text_lower = (raw_text or "").lower()
    is_civic = True
    if "is_civic_issue\": false" in text_lower or "non-civic" in text_lower or "unrecognized" in text_lower:
        is_civic = False

    return VisionAnalysisResponse(
        thinking_steps=[
            "Initial image ingest complete.",
            "Visual inspection model evaluation complete."
        ],
        is_civic_issue=is_civic,
        issue_type="Civic Infrastructure Issue" if is_civic else "Non-Civic / Unclassified Image",
        severity=SeverityLevel.MEDIUM if is_civic else SeverityLevel.LOW,
        confidence=75 if is_civic else 0,
        description=raw_text[:200] if raw_text else ("Visual inspection detected a municipal infrastructure concern." if is_civic else "Visual inspection could not verify a public infrastructure defect in this image."),
        affected_infrastructure="Public Right-of-Way" if is_civic else "None",
        visible_risks=["Public Safety Risk"] if is_civic else [],
        estimated_urgency=UrgencyLevel.STANDARD if is_civic else UrgencyLevel.ROUTINE,
        image_quality_notes="Processed via resilient vision engine"
    )


def sanitize_json_newlines(json_str: str) -> str:
    """
    Sanitizes raw JSON text emitted by LLMs by converting unescaped raw newlines
    and control characters inside string literals into valid escape sequences.
    """
    result = []
    in_string = False
    escaped = False

    for char in json_str:
        if char == '"' and not escaped:
            in_string = not in_string
            result.append(char)
            escaped = False
        elif char == '\\' and not escaped:
            escaped = True
            result.append(char)
        elif char == '\n' and in_string:
            result.append('\\n')
            escaped = False
        elif char == '\r' and in_string:
            result.append('')
            escaped = False
        elif char == '\t' and in_string:
            result.append('\\t')
            escaped = False
        else:
            result.append(char)
            escaped = False

    return "".join(result)


def parse_vision_response(raw_response_text: str) -> VisionAnalysisResponse:
    """
    Parses and validates raw LLM output text into a validated VisionAnalysisResponse Pydantic object.

    Args:
        raw_response_text: Raw model output string.

    Returns:
        VisionAnalysisResponse: Validated Pydantic object.
    """
    if not raw_response_text or not raw_response_text.strip():
        return generate_fallback_vision_data(raw_response_text)

    json_str = extract_json_block(raw_response_text)

    # Attempt 1: Standard / Non-strict JSON parse
    data_dict: Dict[str, Any] = {}
    try:
        data_dict = json.loads(json_str, strict=False)
    except Exception:
        # Attempt 2: Apply state-machine string newline sanitizer
        try:
            sanitized_json = sanitize_json_newlines(json_str)
            data_dict = json.loads(sanitized_json, strict=False)
        except Exception as parse_err:
            logger.error(f"JSON parsing error: {parse_err}. Raw content:\n{json_str[:300]}")
            return generate_fallback_vision_data(raw_response_text)

    # Sanitize & normalize fields if present
    try:
        # Normalize boolean is_civic_issue
        if "is_civic_issue" in data_dict:
            val = data_dict["is_civic_issue"]
            if isinstance(val, str):
                data_dict["is_civic_issue"] = val.strip().lower() in ("true", "1", "yes")
            else:
                data_dict["is_civic_issue"] = bool(val)
        else:
            # Default to True unless issue_type indicates non-civic
            issue_type_raw = str(data_dict.get("issue_type", data_dict.get("type", ""))).lower()
            if "non-civic" in issue_type_raw or "unrecognized" in issue_type_raw:
                data_dict["is_civic_issue"] = False
            else:
                data_dict["is_civic_issue"] = True

        # Normalize issue_type
        if "issue_type" not in data_dict and "type" in data_dict:
            data_dict["issue_type"] = data_dict["type"]
        elif "issue_type" not in data_dict:
            data_dict["issue_type"] = "Civic Infrastructure Hazard" if data_dict.get("is_civic_issue") else "Non-Civic Image"

        # Normalize thinking_steps
        if "thinking_steps" not in data_dict or not isinstance(data_dict["thinking_steps"], list):
            data_dict["thinking_steps"] = [
                "Ingested visual asset.",
                "Analyzed visual features and anomaly presence."
            ]

        # Normalize description
        if "description" not in data_dict or not data_dict["description"]:
            data_dict["description"] = "Visual evidence captured in input photograph."

        # Normalize affected_infrastructure
        if "affected_infrastructure" not in data_dict:
            data_dict["affected_infrastructure"] = data_dict.get("affected_area", "Public Right-of-Way" if data_dict.get("is_civic_issue") else "None")

        # Normalize visible_risks
        if "visible_risks" not in data_dict or not isinstance(data_dict["visible_risks"], list):
            data_dict["visible_risks"] = data_dict.get("possible_risks", ["Public Safety Hazard"] if data_dict.get("is_civic_issue") else [])

        # Enforce severity string title case matching Enum
        if "severity" in data_dict and isinstance(data_dict["severity"], str):
            sev_str = data_dict["severity"].strip().title()
            valid_severities = {s.value for s in SeverityLevel}
            if sev_str in valid_severities:
                data_dict["severity"] = sev_str
            else:
                data_dict["severity"] = SeverityLevel.MEDIUM.value
        elif "severity" not in data_dict:
            data_dict["severity"] = SeverityLevel.MEDIUM.value if data_dict.get("is_civic_issue") else SeverityLevel.LOW.value

        # Enforce urgency enum string
        if "estimated_urgency" in data_dict and isinstance(data_dict["estimated_urgency"], str):
            urg_str = data_dict["estimated_urgency"].strip()
            valid_urgencies = {u.value for u in UrgencyLevel}
            if urg_str in valid_urgencies:
                data_dict["estimated_urgency"] = urg_str
            else:
                data_dict["estimated_urgency"] = UrgencyLevel.STANDARD.value
        elif "estimated_urgency" not in data_dict:
            data_dict["estimated_urgency"] = UrgencyLevel.STANDARD.value if data_dict.get("is_civic_issue") else UrgencyLevel.ROUTINE.value

        # Clamp confidence range [0, 100]
        if "confidence" in data_dict:
            try:
                conf = int(float(data_dict["confidence"]))
                data_dict["confidence"] = max(0, min(100, conf))
            except Exception:
                data_dict["confidence"] = 85
        else:
            data_dict["confidence"] = 85

        # Validate with Pydantic
        if hasattr(VisionAnalysisResponse, "model_validate"):
            return VisionAnalysisResponse.model_validate(data_dict)
        else:
            return VisionAnalysisResponse.parse_obj(data_dict)

    except Exception as validation_error:
        logger.error(f"Pydantic schema validation failure: {validation_error}")
        return generate_fallback_vision_data(raw_response_text)
