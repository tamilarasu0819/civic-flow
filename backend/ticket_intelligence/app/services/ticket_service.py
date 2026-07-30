"""
backend/app/services/ticket_service.py
Service handling prompt assembly, LLM execution, and ticket payload construction.
"""

import os
import uuid
import json
import httpx
import pathlib
import logging
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any

from app.schemas.ticket import (
    VisionInputPayload,
    TicketGenerationRequest,
    TicketResponsePayload,
    DepartmentMappingResult,
    SSEStageUpdateData,
    SSEThoughtData,
    vision_response_to_input_payload
)
from app.services.department_mapper import DepartmentMapper

logger = logging.getLogger("civicflow.ticket_service")

# Load environment configurations for Ticket Intelligence LLM Engine
try:
    from dotenv import load_dotenv
    env_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass

TICKET_API_BASE = os.getenv("TICKET_API_BASE", os.getenv("VISION_API_BASE", "https://generativelanguage.googleapis.com/v1beta/openai/"))
TICKET_API_KEY = os.getenv("TICKET_API_KEY", os.getenv("VISION_API_KEY", ""))
TICKET_MODEL_ID = os.getenv("TICKET_MODEL_ID", os.getenv("VISION_MODEL_ID", "gemini-2.5-flash"))


class TicketService:
    def __init__(self, department_mapper: DepartmentMapper, llm_client=None):
        self.department_mapper = department_mapper
        self.llm_client = llm_client

    async def generate_ticket_from_vision(self, vision_input: Any, override_department: Any = None) -> TicketResponsePayload:
        """Helper to generate a ticket directly from a Vision Intelligence output or dict."""
        vision_payload = vision_response_to_input_payload(vision_input)
        req = TicketGenerationRequest(vision_data=vision_payload, override_department=override_department)
        return await self.generate_ticket(req)

    async def generate_ticket(self, request: TicketGenerationRequest) -> TicketResponsePayload:
        """Direct REST handler for creating a formal complaint ticket."""
        vision_data = vision_response_to_input_payload(request.vision_data)

        # 1. Map Department & Priority
        mapping_result = self.department_mapper.map_department(vision_data)
        target_department = request.override_department or mapping_result.department
        assigned_priority = mapping_result.priority

        # 2. Build Prompt & Invoke LLM
        prompt_str = self._build_ticket_prompt(vision_data, target_department.value, assigned_priority.value)
        llm_json_output = await self._call_llm_ticket_generator(prompt_str, vision_data, target_department.value, assigned_priority.value)

        # 3. Construct Final Ticket Payload
        ticket_id = f"TCK-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        
        return TicketResponsePayload(
            ticket_id=ticket_id,
            created_at=datetime.now(timezone.utc),
            department=target_department,
            priority=assigned_priority,
            complaint_title=llm_json_output.get("complaint_title", f"Formal Notice: {vision_data.type} Hazard"),
            executive_summary=llm_json_output.get("executive_summary", vision_data.description),
            formal_complaint_body=llm_json_output.get("formal_complaint_body", ""),
            evidence_summary=llm_json_output.get("evidence_summary", []),
            actionable_recommendations=llm_json_output.get("actionable_recommendations", []),
            statutory_references=llm_json_output.get("statutory_references", []),
            vision_summary=vision_data
        )

    def _build_ticket_prompt(self, vision_data: VisionInputPayload, dept_name: str, priority: str) -> str:
        return f"""
        Execute Formal Complaint Generation for:
        Issue Type: {vision_data.type}
        Description: {vision_data.description}
        Severity: {vision_data.severity.value if hasattr(vision_data.severity, 'value') else str(vision_data.severity)}
        Department: {dept_name}
        Priority: {priority}
        Affected Area: {vision_data.affected_area}
        Confidence Score: {vision_data.confidence}%
        Risks: {', '.join(vision_data.possible_risks) if vision_data.possible_risks else 'Public Safety Risk'}
        """

    async def _call_llm_ticket_generator(self, prompt: str, vision_data: VisionInputPayload, dept_name: str, priority: str) -> Dict[str, Any]:
        """Invokes underlying LLM service (Gemini AI / Vertex AI / Custom Endpoint)."""
        if TICKET_API_KEY:
            try:
                system_prompt = (
                    "You are CivicFlow's Agentic AI Ticket Intelligence Engine. "
                    "Your task is to generate a formal, authoritative, and comprehensive municipal complaint memo and ticket payload "
                    "based on visual evidence telemetry from civic infrastructure inspections. "
                    "You MUST respond ONLY with a single valid raw JSON object matching this schema:\n"
                    "{\n"
                    '  "complaint_title": "string (Urgent formal title with issue type and location)",\n'
                    '  "executive_summary": "string (Clear executive summary of issue, severity, and required action)",\n'
                    '  "formal_complaint_body": "string (Detailed legal/bureaucratic notice to department chief with risk analysis and compliance requirements)",\n'
                    '  "evidence_summary": ["string point 1", "string point 2"],\n'
                    '  "actionable_recommendations": ["string recommendation 1", "string recommendation 2"],\n'
                    '  "statutory_references": ["string ordinance 1", "string ordinance 2"]\n'
                    "}"
                )
                
                headers = {
                    "Authorization": f"Bearer {TICKET_API_KEY}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": TICKET_MODEL_ID,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"}
                }

                async with httpx.AsyncClient(timeout=15.0) as client:
                    url = f"{TICKET_API_BASE.rstrip('/')}/chat/completions"
                    res = await client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        raw_content = res.json()["choices"][0]["message"]["content"]
                        if "```" in raw_content:
                            raw_content = raw_content.split("```")[1]
                            if raw_content.startswith("json"):
                                raw_content = raw_content[4:]
                            raw_content = raw_content.strip()
                        ai_json = json.loads(raw_content)
                        logger.info("Successfully generated AI ticket via Gemini Model!")
                        return ai_json
                    else:
                        logger.warning(f"LLM API call returned status {res.status_code}: {res.text}")
            except Exception as e:
                logger.error(f"Error calling LLM ticket generator API: {e}. Falling back to default bureaucrat generator.")

        # High-fidelity realistic municipal bureaucrat fallback generator
        issue_title = vision_data.type
        body_intro = f"TO THE CHIEF MUNICIPAL OFFICER / EXECUTIVE ENGINEER, {dept_name.upper()}:\n\n"
        body_notice = f"Official notice is hereby served regarding a verified public infrastructure defect identified as '{issue_title}' located in the public domain ({vision_data.affected_area}). Visual evidence confirms {vision_data.description.lower()}.\n\n"
        body_impact = f"The observed situation presents an elevated risk rating of {priority} severity. Primary public hazards include {', '.join(vision_data.possible_risks) if vision_data.possible_risks else 'public safety impairment'}. Continued inaction risks progressive structural degradation and severe statutory non-compliance under municipal codes.\n\n"
        body_action = f"Immediate deployment of departmental field units is requested to execute containment, structural repair, and restore standard operating conditions."

        return {
            "complaint_title": f"URGENT: Formal Notice of {issue_title} on {vision_data.affected_area}",
            "executive_summary": f"A verified civic issue ({issue_title}) has been identified on {vision_data.affected_area}. Immediate departmental action by {dept_name} is required to mitigate active hazards and restore public safety.",
            "formal_complaint_body": body_intro + body_notice + body_impact + body_action,
            "evidence_summary": [
                f"Visual confirmation of {vision_data.type} with estimated severity score of {vision_data.severity.value if hasattr(vision_data.severity, 'value') else str(vision_data.severity)}.",
                f"Identified hazard vectors: {', '.join(vision_data.possible_risks) if vision_data.possible_risks else 'General public risk'}.",
                f"Affected zone: {vision_data.affected_area} (Confidence score: {vision_data.confidence}%)."
            ],
            "actionable_recommendations": [
                "Dispatch emergency field inspection team within target SLA timeframe.",
                "Erect safety barriers and hazard warnings around affected zone.",
                "Initiate corrective engineering remediation and issue completion report."
            ],
            "statutory_references": [
                "Municipal Corporation Infrastructure & Safety Maintenance Act (Section 104).",
                "Public Nuisance & Hazard Mitigation Ordinance."
            ]
        }

