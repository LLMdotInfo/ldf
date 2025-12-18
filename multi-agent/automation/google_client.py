"""
Google/Gemini Audit Client

Sends audit requests to Gemini API and parses responses.

Usage:
    from multi_agent.automation.google_client import GeminiAuditor

    auditor = GeminiAuditor()
    result = await auditor.audit_spec(spec_content, "gap-analysis")
"""

import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    genai = None


@dataclass
class AuditIssue:
    """Single issue found during audit."""

    id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    location: str
    description: str
    recommendation: str


@dataclass
class AuditResult:
    """Result of an audit request."""

    request_id: str
    audit_type: str
    agent: str
    timestamp: datetime
    assessment: str  # APPROVE, NEEDS_REVISION, REJECT
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    issues: list[AuditIssue] = field(default_factory=list)
    raw_response: str = ""
    error: str | None = None


class GeminiAuditor:
    """Google Gemini API client for spec and code audits."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-pro",
        max_tokens: int = 4000,
        prompts_dir: Path | None = None,
    ):
        """
        Initialize Gemini auditor.

        Args:
            api_key: Google AI API key. Defaults to GOOGLE_AI_API_KEY env var.
            model: Model to use. Defaults to gemini-pro.
            max_tokens: Maximum response tokens.
            prompts_dir: Directory containing prompt files.
        """
        if genai is None:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )

        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google AI API key not provided. Set GOOGLE_AI_API_KEY env var."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.max_tokens = max_tokens

        if prompts_dir:
            self.prompts_dir = Path(prompts_dir)
        else:
            self.prompts_dir = Path(__file__).parent.parent / "prompts" / "gemini"

    def _load_prompt(self, prompt_type: str) -> str:
        """Load prompt file content."""
        prompt_file = self.prompts_dir / f"{prompt_type}.md"
        if not prompt_file.exists():
            raise ValueError(f"Prompt file not found: {prompt_file}")
        return prompt_file.read_text()

    async def audit_spec(
        self,
        spec_content: str,
        prompt_type: str,
        context: str | None = None,
    ) -> AuditResult:
        """
        Send spec to Gemini for audit.

        Args:
            spec_content: The spec content to audit.
            prompt_type: Type of audit (gap-analysis, edge-cases, architecture).
            context: Additional context to include.

        Returns:
            AuditResult with findings.
        """
        request_id = f"AUDIT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        try:
            system_prompt = self._load_prompt(prompt_type)

            full_prompt = f"{system_prompt}\n\n---\n\n## Audit Request\n\n{spec_content}"
            if context:
                full_prompt = f"{system_prompt}\n\n## Context\n\n{context}\n\n---\n\n## Audit Request\n\n{spec_content}"

            # Gemini uses generate_content_async for async
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=0.3,
                ),
            )

            raw_response = response.text or ""

            return self._parse_response(
                request_id=request_id,
                audit_type=prompt_type,
                raw_response=raw_response,
            )

        except Exception as e:
            return AuditResult(
                request_id=request_id,
                audit_type=prompt_type,
                agent="gemini",
                timestamp=datetime.now(),
                assessment="ERROR",
                risk_level="UNKNOWN",
                raw_response="",
                error=str(e),
            )

    def _parse_response(
        self,
        request_id: str,
        audit_type: str,
        raw_response: str,
    ) -> AuditResult:
        """Parse Gemini response into structured result."""
        issues = []

        # Extract assessment
        assessment = "NEEDS_REVISION"
        if "APPROVE" in raw_response.upper() and "NEEDS_REVISION" not in raw_response.upper():
            assessment = "APPROVE"
        elif "REJECT" in raw_response.upper():
            assessment = "REJECT"

        # Extract risk level
        risk_level = "MEDIUM"
        risk_match = re.search(r"Risk Level[:\s]*(CRITICAL|HIGH|MEDIUM|LOW)", raw_response, re.IGNORECASE)
        if risk_match:
            risk_level = risk_match.group(1).upper()

        # Extract issues from markdown tables
        # Gap analysis format: | G-001 | ...
        # Edge cases format: | BC-001 |, | TC-001 |, | ST-001 |, | DC-001 |, | UB-001 |, | IC-001 |
        issue_patterns = [
            # Table format with various ID prefixes
            r"\|\s*([GBTSDUI][C]?-\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)",
            # Generic table format
            r"\|\s*(\w+-\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)",
        ]

        for pattern in issue_patterns:
            matches = re.findall(pattern, raw_response)
            for match in matches:
                if len(match) >= 2:
                    issue_id = str(match[0]).strip()
                    title = match[1].strip()
                    location = match[2].strip() if len(match) > 2 else ""

                    # Skip header rows
                    if title.lower() in ["gap id", "id", "title", "user type", "scenario", "input/condition"]:
                        continue

                    # Determine severity based on context or ID
                    severity = "MEDIUM"
                    if "critical" in title.lower() or "high risk" in title.lower():
                        severity = "HIGH"
                    elif "low" in title.lower():
                        severity = "LOW"

                    issues.append(
                        AuditIssue(
                            id=issue_id,
                            severity=severity,
                            title=title,
                            location=location,
                            description="",
                            recommendation="",
                        )
                    )

        return AuditResult(
            request_id=request_id,
            audit_type=audit_type,
            agent="gemini",
            timestamp=datetime.now(),
            assessment=assessment,
            risk_level=risk_level,
            issues=issues,
            raw_response=raw_response,
        )

    async def close(self):
        """Close the client (for cleanup)."""
        # Gemini client doesn't need explicit cleanup
        pass
