"""
backend/ticket_intelligence/app/services/document_customizer.py
Service for processing user-requested ticket/document customizations via Groq API.
"""

import os
import json
import logging
import pathlib
import httpx
from typing import Dict, Any, List

logger = logging.getLogger("civicflow.services.document_customizer")

try:
    from dotenv import load_dotenv
    env_path = pathlib.Path(__file__).parent.parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
GROQ_MODEL_ID = os.getenv("GROQ_MODEL_ID", "llama-3.3-70b-versatile")


SYSTEM_PROMPT = """You are CivicFlow AI's Municipal Document Customization Engine powered by Groq.
Your task is to modify a municipal complaint ticket based strictly on the user's customization request.

Given:
1. Current Ticket Data (JSON)
2. User's Edit Instruction (e.g., "change location to Jubilee Hills Road No. 36", "update department to Water Supply & Sewerage", "set severity to Critical")

You MUST:
1. Apply the user's requested changes accurately to the ticket fields.
2. Update related fields logically (e.g., if location changes, update location/affectedArea; if department changes, update department name; if severity changes, update severity/priority).
3. If formal_complaint_body or executive_summary refer to old location/department/severity, revise those sentences accordingly so the report is fully coherent and professional.
4. Keep unmodified fields intact.
5. Return a strictly valid JSON object with the following schema:

```json
{
  "updated_ticket": {
    "id": "string",
    "ticketId": "string",
    "title": "string",
    "description": "string",
    "category": "string",
    "department": "string",
    "severity": "string (Critical | High | Medium | Low)",
    "location": "string",
    "evidence": ["string"],
    "dateGenerated": "string",
    "formal_complaint_body": "string",
    "executive_summary": "string",
    "actionable_recommendations": ["string"],
    "statutory_references": ["string"]
  },
  "summary_of_changes": "A clear, 1-2 sentence summary of what specific fields were changed.",
  "changed_fields": ["array of modified field names, e.g. location, department, title, severity, formal_complaint_body"]
}
```
"""


class DocumentCustomizer:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", GROQ_API_KEY)
        self.api_base = os.getenv("GROQ_API_BASE", GROQ_API_BASE).rstrip('/')
        self.model_id = os.getenv("GROQ_MODEL_ID", GROQ_MODEL_ID)

    async def customize_ticket(
        self,
        current_ticket: Dict[str, Any],
        user_instruction: str
    ) -> Dict[str, Any]:
        """
        Calls Groq API to update ticket JSON according to user_instruction.
        Returns dict containing updated_ticket, summary_of_changes, changed_fields.
        """
        if not self.api_key:
            logger.warning("GROQ_API_KEY not configured.")
            return self._fallback_customization(current_ticket, user_instruction)

        prompt_payload = f"""Current Ticket Data:
{json.dumps(current_ticket, indent=2)}

User Customization Request:
"{user_instruction}"

Respond ONLY with valid raw JSON matching the required schema. No conversational text outside JSON.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_payload}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                res_data = response.json()
                content = res_data["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                if "updated_ticket" in parsed:
                    # Ensure ID remains consistent
                    parsed["updated_ticket"]["id"] = current_ticket.get("id") or current_ticket.get("ticketId")
                    parsed["updated_ticket"]["ticketId"] = current_ticket.get("ticketId") or current_ticket.get("id")
                    return parsed
                else:
                    return self._fallback_customization(current_ticket, user_instruction)

        except Exception as e:
            logger.error(f"Groq API document customization error: {e}")
            return self._fallback_customization(current_ticket, user_instruction)

    def _fallback_customization(
        self,
        current_ticket: Dict[str, Any],
        user_instruction: str
    ) -> Dict[str, Any]:
        """Fallback in case Groq API call fails or is unreachable."""
        ticket_copy = dict(current_ticket)
        instruction_lower = user_instruction.lower()
        changed = []

        if "location" in instruction_lower:
            parts = user_instruction.split("location to")
            new_loc = parts[-1].strip() if len(parts) > 1 else user_instruction
            ticket_copy["location"] = new_loc
            changed.append("location")

        summary = f"Updated document according to request: '{user_instruction}'"
        return {
            "updated_ticket": ticket_copy,
            "summary_of_changes": summary,
            "changed_fields": changed if changed else ["description"]
        }
