"""
OpenAI/ChatGPT Audit Client

Sends audit requests to ChatGPT API and parses responses.

Usage:
    from multi_agent.automation.openai_client import ChatGPTAuditor

    auditor = ChatGPTAuditor()
    result = await auditor.audit_spec(spec_content, "spec-review")
"""

import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None


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


class ChatGPTAuditor:
    """ChatGPT API client for spec and code audits."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o",
        max_tokens: int = 4000,
        prompts_dir: Path | None = None,
    ):
        """
        Initialize ChatGPT auditor.

        Args:
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
            model: Model to use. Defaults to gpt-4o.
            max_tokens: Maximum response tokens.
            prompts_dir: Directory containing prompt files.
        """
        if AsyncOpenAI is None:
            raise ImportError("openai package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY env var.")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens

        if prompts_dir:
            self.prompts_dir = Path(prompts_dir)
        else:
            self.prompts_dir = Path(__file__).parent.parent / "prompts" / "chatgpt"

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
        Send spec to ChatGPT for audit.

        Args:
            spec_content: The spec content to audit.
            prompt_type: Type of audit (spec-review, code-audit, security-check).
            context: Additional context to include.

        Returns:
            AuditResult with findings.
        """
        request_id = f"AUDIT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        try:
            system_prompt = self._load_prompt(prompt_type)

            user_message = f"## Audit Request\n\n{spec_content}"
            if context:
                user_message = f"## Context\n\n{context}\n\n{user_message}"

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for consistency
            )

            raw_response = response.choices[0].message.content or ""

            return self._parse_response(
                request_id=request_id,
                audit_type=prompt_type,
                raw_response=raw_response,
            )

        except Exception as e:
            return AuditResult(
                request_id=request_id,
                audit_type=prompt_type,
                agent="chatgpt",
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
        """Parse ChatGPT response into structured result."""
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

        # Extract issues from markdown tables or lists
        # Look for patterns like "| C-001 |" or "1. **Issue Title**"
        issue_patterns = [
            # Table format: | ID | Title | Location | ...
            r"\|\s*([CHML]-\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)",
            # List format: 1. **Title** or 1. [Title]
            r"(\d+)\.\s*\*\*([^*]+)\*\*[:\s]*([^\n]+)?",
        ]

        for pattern in issue_patterns:
            matches = re.findall(pattern, raw_response)
            for match in matches:
                if len(match) >= 2:
                    issue_id = str(match[0])
                    title = match[1].strip()
                    location = match[2].strip() if len(match) > 2 else ""

                    # Determine severity from ID prefix
                    severity = "MEDIUM"
                    if issue_id.startswith("C") or "critical" in title.lower():
                        severity = "CRITICAL"
                    elif issue_id.startswith("H") or "high" in title.lower():
                        severity = "HIGH"
                    elif issue_id.startswith("L") or "low" in title.lower():
                        severity = "LOW"

                    issues.append(
                        AuditIssue(
                            id=issue_id,
                            severity=severity,
                            title=title,
                            location=location,
                            description="",  # Would need more parsing
                            recommendation="",
                        )
                    )

        return AuditResult(
            request_id=request_id,
            audit_type=audit_type,
            agent="chatgpt",
            timestamp=datetime.now(),
            assessment=assessment,
            risk_level=risk_level,
            issues=issues,
            raw_response=raw_response,
        )

    async def close(self):
        """Close the client (for cleanup)."""
        await self.client.close()
