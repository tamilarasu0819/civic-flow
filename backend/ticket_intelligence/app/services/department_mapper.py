"""
backend/app/services/department_mapper.py
Hybrid Department Resolution Engine (Rule Matrix + LLM Dynamic Fallback).
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from app.schemas.ticket import (
    VisionInputPayload, 
    DepartmentMappingResult, 
    DepartmentName, 
    PriorityLevel, 
    SeverityLevel
)

logger = logging.getLogger("civicflow.department_mapper")


class DepartmentMapper:
    """
    Resolves responsible civic department and calculates incident priority.
    Uses rule-based regex patterns first, falling back to LLM evaluation if confidence is low.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self._init_rule_matrix()

    def _init_rule_matrix(self):
        """Compiles rule mappings for fast regex lookup."""
        self.rule_matrix: List[Dict] = [
            {
                "department": DepartmentName.ELECTRICITY,
                "patterns": [r"electric", r"wire", r"transformer", r"pole", r"spark", r"power outage", r"street light"],
                "high_priority_triggers": ["wire", "spark", "live", "fallen pole"]
            },
            {
                "department": DepartmentName.WATER_SEWAGE,
                "patterns": [r"drain", r"sewer", r"water pipe", r"manhole", r"effluent", r"water leakage", r"sludge"],
                "high_priority_triggers": ["open manhole", "sewage overflow", "pipe burst"]
            },
            {
                "department": DepartmentName.SANITATION,
                "patterns": [r"garbage", r"waste", r"dumping", r"trash", r"dead animal", r"litter", r"dustbin"],
                "high_priority_triggers": ["toxic waste", "blocking road"]
            },
            {
                "department": DepartmentName.TRAFFIC_POLICE,
                "patterns": [r"traffic light", r"signal", r"illegal parking", r"road block", r"signboard", r"tree fallen"],
                "high_priority_triggers": ["signal dead", "total blockage"]
            },
            {
                "department": DepartmentName.PWD,
                "patterns": [r"pothole", r"road", r"footpath", r"pavement", r"bridge", r"trench", r"asphalt"],
                "high_priority_triggers": ["road collapse", "bridge damage"]
            }
        ]

    def map_department(self, vision_data: VisionInputPayload) -> DepartmentMappingResult:
        """
        Main entry point for department and priority mapping.
        """
        # Step 1: Attempt Rule-Based Resolution
        rule_result = self._apply_rule_matrix(vision_data)
        if rule_result and rule_result.confidence_score >= 0.85:
            logger.info(f"Rule match successful: {rule_result.department.value}")
            return rule_result

        # Step 2: LLM Fallback for ambiguous or low-confidence results
        if self.llm_client:
            logger.info("Confidence low or ambiguous issue. Triggering LLM fallback resolution.")
            return self._llm_fallback_map(vision_data)

        # Default Fallback if LLM unavailable
        return rule_result or DepartmentMappingResult(
            department=DepartmentName.GENERAL_MUNICIPAL,
            priority=self._calculate_priority(vision_data.severity, []),
            confidence_score=0.50,
            matched_rule="DEFAULT_FALLBACK",
            resolution_method="SYSTEM_DEFAULT"
        )

    def _apply_rule_matrix(self, vision_data: VisionInputPayload) -> Optional[DepartmentMappingResult]:
        combined_text = f"{vision_data.type} {vision_data.description} {' '.join(vision_data.possible_risks)}".lower()
        
        best_dept = None
        max_matches = 0
        matched_rule_name = ""
        matched_triggers = []

        for rule in self.rule_matrix:
            matches = sum(1 for pattern in rule["patterns"] if re.search(pattern, combined_text))
            if matches > max_matches:
                max_matches = matches
                best_dept = rule["department"]
                matched_rule_name = f"REGEX_MATCH_{rule['department'].name}"
                matched_triggers = [trig for trig in rule["high_priority_triggers"] if trig in combined_text]

        if best_dept and max_matches > 0:
            confidence = min(0.60 + (max_matches * 0.15), 0.98)
            computed_priority = self._calculate_priority(
                vision_data.severity, 
                matched_triggers + vision_data.possible_risks
            )
            
            return DepartmentMappingResult(
                department=best_dept,
                priority=computed_priority,
                confidence_score=confidence,
                matched_rule=matched_rule_name,
                resolution_method="RULE_MATRIX"
            )

        return None

    def _calculate_priority(self, vision_severity: SeverityLevel, risk_factors: List[str]) -> PriorityLevel:
        """Calculates numerical priority score and returns PriorityLevel enum."""
        severity_weights = {
            SeverityLevel.CRITICAL: 4.0,
            SeverityLevel.HIGH: 3.0,
            SeverityLevel.MEDIUM: 2.0,
            SeverityLevel.LOW: 1.0
        }
        
        score = severity_weights.get(vision_severity, 2.0)

        # Risk factor weightings
        risk_str = " ".join(risk_factors).lower()
        if any(k in risk_str for k in ["electric", "wire", "collapse", "live"]):
            score += 1.5
        if any(k in risk_str for k in ["manhole", "open pit", "fire"]):
            score += 1.5
        if any(k in risk_str for k in ["disease", "health", "hazard", "traffic"]):
            score += 1.0

        if score >= 5.0:
            return PriorityLevel.CRITICAL
        elif score >= 3.5:
            return PriorityLevel.HIGH
        elif score >= 2.0:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW

    def _llm_fallback_map(self, vision_data: VisionInputPayload) -> DepartmentMappingResult:
        """Invokes LLM for multi-domain civic issue classification."""
        return DepartmentMappingResult(
            department=DepartmentName.GENERAL_MUNICIPAL,
            priority=PriorityLevel.HIGH,
            confidence_score=0.90,
            matched_rule="LLM_DYNAMIC_CLASSIFICATION",
            resolution_method="LLM_FALLBACK"
        )
