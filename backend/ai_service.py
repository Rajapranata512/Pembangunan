"""
ai_service.py — Abstraksi LLM provider (provider-agnostic).
Saat ini mendukung Google Gemini. Dirancang untuk mudah ditambah OpenAI/Claude.
"""
import os
import json
import re
import time
import traceback
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Data Classes
# ──────────────────────────────────────────────
@dataclass
class InsightResult:
    insight_text: str
    key_strengths: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list)
    best_for: list[str] = field(default_factory=list)
    model_version: str = "gemini-2.5-flash"
    success: bool = True
    error: Optional[str] = None


@dataclass
class SentimentResult:
    overall_sentiment: str = "netral"
    confidence_score: float = 0.5
    summary: str = ""
    highlights: list[dict] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


# ──────────────────────────────────────────────
# AI Service Class
# ──────────────────────────────────────────────
class AIService:
    """Provider-agnostic AI service. Currently uses Google Gemini."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self._client = None
        self._model_name = "gemini-2.5-flash"
        self._available = False
        self._init_client()

    def _init_client(self):
        """Initialize the Gemini client."""
        if not self.api_key or self.api_key == "your_api_key_here":
            print("[AI] WARNING: GEMINI_API_KEY not set. AI features will use fallback mode.")
            return

        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self._available = True
            print(f"[AI] OK: Gemini client initialized (model: {self._model_name})")
        except ImportError:
            print("[AI] WARNING: google-genai not installed. Run: pip install google-genai")
        except Exception as e:
            print(f"[AI] WARNING: Failed to init Gemini: {e}")

    @property
    def is_available(self) -> bool:
        return self._available

    def _call_gemini(self, prompt: str, system_prompt: str = "", max_tokens: int = 4096, **kwargs) -> str:
        """Call Gemini API with retry logic."""
        if not self._available:
            raise RuntimeError("AI service not available")

        from google.genai import types

        config_dict = {
            "system_instruction": system_prompt if system_prompt else None,
            "max_output_tokens": max_tokens,
            "temperature": 0.7,
        }
        
        # Extract kwargs that should go into config
        kwargs_copy = kwargs.copy()
        if "response_mime_type" in kwargs_copy:
            config_dict["response_mime_type"] = kwargs_copy.pop("response_mime_type")

        config = types.GenerateContentConfig(**config_dict)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=config,
                )
                if response.text:
                    return response.text
                return ""
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait = (attempt + 1) * 5
                    print(f"[AI] Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)

        raise RuntimeError("Max retries exceeded")

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def generate_region_insight(self, region_data: dict, system_prompt: str = "", user_prompt: str = "") -> InsightResult:
        """Generate AI insight for a region using all its data."""
        from prompts import INSIGHT_SYSTEM_PROMPT, INSIGHT_USER_TEMPLATE

        sys_prompt = system_prompt or INSIGHT_SYSTEM_PROMPT

        # Format the user prompt with region data
        try:
            formatted_prompt = user_prompt or INSIGHT_USER_TEMPLATE.format(**region_data)
        except KeyError as e:
            return InsightResult(
                insight_text="",
                success=False,
                error=f"Missing data field: {e}",
            )

        try:
            response_text = self._call_gemini(formatted_prompt, sys_prompt, max_tokens=2048)

            # Parse the response — extract narrative and JSON
            insight_text = response_text
            strengths = []
            risks = []
            best_for = []

            # Try to extract JSON block from response
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*(?:```)?', response_text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    strengths = parsed.get("key_strengths", [])
                    risks = parsed.get("key_risks", [])
                    best_for = parsed.get("best_for", [])
                    # Remove JSON block from insight text
                    insight_text = response_text[:json_match.start()].strip()
                except json.JSONDecodeError:
                    pass
            else:
                # Try finding the first { and last }
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                    try:
                        parsed = json.loads(response_text[start_idx:end_idx+1])
                        strengths = parsed.get("key_strengths", [])
                        risks = parsed.get("key_risks", [])
                        best_for = parsed.get("best_for", [])
                        insight_text = response_text[:start_idx].strip()
                    except json.JSONDecodeError:
                        pass

            return InsightResult(
                insight_text=insight_text,
                key_strengths=strengths[:5],
                key_risks=risks[:5],
                best_for=best_for[:5],
                model_version=self._model_name,
            )

        except Exception as e:
            traceback.print_exc()
            return InsightResult(
                insight_text="",
                success=False,
                error=str(e),
            )

    def chat(self, message: str, system_prompt: str = "", context: str = "") -> str:
        """Handle a chatbot message and return AI response."""
        from prompts import CHATBOT_SYSTEM_PROMPT

        sys_prompt = system_prompt or CHATBOT_SYSTEM_PROMPT
        full_prompt = f"{context}\n\nPertanyaan user: {message}" if context else message

        try:
            response = self._call_gemini(full_prompt, sys_prompt, max_tokens=1024)
            return response.strip()
        except Exception as e:
            traceback.print_exc()
            return f"Maaf, saya mengalami kendala teknis. Silakan coba lagi nanti. (Error: {str(e)[:100]})"

    def analyze_sentiment(self, headlines: list[str], region_name: str = "", province: str = "") -> SentimentResult:
        """Analyze sentiment of news headlines about a region."""
        from prompts import SENTIMENT_SYSTEM_PROMPT, SENTIMENT_USER_TEMPLATE

        if not headlines:
            return SentimentResult(
                summary="Tidak ada headline berita yang ditemukan untuk wilayah ini.",
                success=True,
            )

        headlines_text = "\n".join(f"- {h}" for h in headlines[:15])
        prompt = SENTIMENT_USER_TEMPLATE.format(
            region_name=region_name,
            province=province,
            headlines=headlines_text,
        )

        try:
            # Force JSON response format
            response = self._call_gemini(
                prompt, 
                SENTIMENT_SYSTEM_PROMPT, 
                max_tokens=2048,
                response_mime_type="application/json"
            )

            # Extract JSON from response
            try:
                parsed = json.loads(response.strip())
            except json.JSONDecodeError:
                # Fallback extraction if model still wraps in markdown
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        parsed = None
                else:
                    parsed = None

            if not parsed:
                return SentimentResult(
                    summary=f"AI merespons tetapi format tidak dapat diparse. Raw: {response[:200]}",
                    success=False,
                )

            return SentimentResult(
                overall_sentiment=parsed.get("overall_sentiment", "netral"),
                confidence_score=float(parsed.get("confidence_score", 0.5)),
                summary=parsed.get("summary", ""),
                highlights=parsed.get("highlights", [])[:5],
            )

        except Exception as e:
            traceback.print_exc()
            return SentimentResult(
                summary=f"Gagal menganalisis sentimen: {str(e)[:100]}",
                success=False,
                error=str(e),
            )

    def generate_pdf_narrative(self, region_data: dict) -> str:
        """Generate a formal executive summary for PDF report."""
        from prompts import PDF_NARRATIVE_PROMPT

        prompt = PDF_NARRATIVE_PROMPT.format(
            region_data=json.dumps(region_data, indent=2, ensure_ascii=False, default=str),
            business_score=region_data.get("business_score", "N/A"),
            property_score=region_data.get("property_score", "N/A"),
            growth_score=region_data.get("growth_score", "N/A"),
            risk_score=region_data.get("risk_score", "N/A"),
            final_score=region_data.get("final_score", "N/A"),
        )

        try:
            return self._call_gemini(prompt, max_tokens=1024).strip()
        except Exception:
            return (
                f"{region_data.get('name', 'Wilayah ini')} merupakan {region_data.get('region_type', 'wilayah')} "
                f"di Provinsi {region_data.get('province', '-')} dengan skor final "
                f"{region_data.get('final_score', 'N/A')}/100. "
                "Analisis AI sedang tidak tersedia, silakan coba lagi nanti."
            )


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create the singleton AIService instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
