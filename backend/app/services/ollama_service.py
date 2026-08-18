"""Production-Grade Ollama Local LLM & Grounded RAG Decision Support Service (v1.10.1)."""
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

try:
    import httpx
except ImportError:
    import urllib.request
    httpx = None

from app.models.user import User
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
DEFAULT_MODEL = "llama3.2"

def check_ollama_status() -> Dict[str, Any]:
    """Checks local Ollama service availability and llama3.2 model status."""
    try:
        if httpx:
            resp = httpx.get(OLLAMA_TAGS_URL, timeout=3.0)
            if resp.status_code == 200:
                models = [m.get("name", "") for m in resp.json().get("models", [])]
                has_llama = any("llama3.2" in m for m in models)
                return {"available": True, "llama3_2_available": has_llama, "models": models}
        else:
            req = urllib.request.Request(OLLAMA_TAGS_URL)
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                models = [m.get("name", "") for m in data.get("models", [])]
                has_llama = any("llama3.2" in m for m in models)
                return {"available": True, "llama3_2_available": has_llama, "models": models}
    except Exception as e:
        logger.debug(f"Ollama status check offline: {str(e)}")
    return {"available": False, "llama3_2_available": False, "models": []}


class OllamaRAGService:
    """
    Grounded LLM Decision Support Service.
    Invokes Ollama llama3.2 for qualitative explanations while preserving deterministic ML backend invariants.
    """
    def __init__(self):
        self.rag_service = get_rag_service()

    def _query_ollama_raw(self, prompt: str, timeout_sec: float = 25.0) -> Optional[str]:
        """Queries local Ollama endpoint with strict timeout."""
        payload = {
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "temperature": 0.2,
            "stream": False
        }
        try:
            if httpx:
                resp = httpx.post(OLLAMA_GENERATE_URL, json=payload, timeout=timeout_sec)
                if resp.status_code == 200:
                    return resp.json().get("response", "")
            else:
                req = urllib.request.Request(
                    OLLAMA_GENERATE_URL,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                    return json.loads(resp.read().decode('utf-8')).get("response", "")
        except Exception as err:
            logger.warning(f"Ollama connection/timeout attempt failed: {str(err)}")
        return None

    def explain_student_risk(
        self,
        db: Session,
        requesting_user: User,
        student_id: str,
        skill_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        USE CASE A — Student Risk Explanation.
        Explains why a skill is at risk while preserving deterministic ML prediction invariants.
        """
        rag_context = self.rag_service.retrieve_student_context(db, requesting_user, student_id, skill_id)
        cdata = rag_context["data"]
        ml_pred = cdata["deterministic_ml_prediction"]

        # Deterministic Grounded Invariants
        forget_prob = ml_pred["forget_probability"]
        risk_level = ml_pred["risk_level"]
        rec_date = ml_pred["recommended_revision_date"]

        prompt = f"""
SYSTEM INSTRUCTIONS:
You are EduSense AI Study Assistant.
Explain the student's knowledge decay risk using ONLY the supplied context.
Do NOT calculate or invent numerical probabilities.
The system ML prediction (Forget Probability = {forget_prob}, Risk Level = {risk_level}) is authoritative.

RETRIEVED CONTEXT:
{json.dumps(cdata, indent=2)}

TASK:
Provide a grounded educational explanation in valid JSON format:
{{
  "summary": "Brief 1-2 sentence summary of risk",
  "evidence": ["Evidence point 1", "Evidence point 2"],
  "explanation": "Detailed pedagogical explanation of forgetting risk factors",
  "recommended_actions": ["Action 1", "Action 2"],
  "limitations": ["Observational limitation notice"]
}}
Output ONLY pure JSON.
"""
        raw_resp = self._query_ollama_raw(prompt)
        parsed_explanation = None

        if raw_resp:
            try:
                # Clean JSON fences if present
                clean_txt = raw_resp.strip()
                if clean_txt.startswith("```json"):
                    clean_txt = clean_txt[7:]
                if clean_txt.endswith("```"):
                    clean_txt = clean_txt[:-3]
                parsed_explanation = json.loads(clean_txt.strip())
            except Exception as e:
                logger.warning(f"Failed to parse Ollama explanation JSON: {str(e)}")

        if not parsed_explanation or not isinstance(parsed_explanation, dict):
            # Deterministic Fallback Response
            parsed_explanation = {
                "summary": f"Skill '{skill_id or 'general'}' exhibits {risk_level} forgetting risk ({int(forget_prob*100)}% probability).",
                "evidence": ml_pred["top_risk_factors"],
                "explanation": f"AI qualitative generation is temporarily offline. Based on deterministic ML prediction, the student has a {int(forget_prob*100)}% probability of forgetting within 7 days due to temporal decay.",
                "recommended_actions": [f"Review skill before {rec_date[:10]}"],
                "limitations": ["Generated using deterministic ML fallback."]
            }

        # Enforce ML Backend Source of Truth Invariants
        return {
            "student_id": student_id,
            "skill_id": skill_id or "general",
            "deterministic_ml_prediction": {
                "forget_probability": forget_prob,
                "forget_probability_percentage": round(forget_prob * 100.0, 1),
                "risk_level": risk_level,
                "recommended_revision_date": rec_date
            },
            "grounded_ai_explanation": parsed_explanation,
            "source_context": rag_context["source_type"]
        }

    def generate_revision_guidance(
        self,
        db: Session,
        requesting_user: User,
        student_id: str,
        skill_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        USE CASE B — Student Revision Guidance.
        """
        rag_context = self.rag_service.retrieve_student_context(db, requesting_user, student_id, skill_id)
        cdata = rag_context["data"]
        ml_pred = cdata["deterministic_ml_prediction"]

        return {
            "student_id": student_id,
            "skill_id": skill_id or "general",
            "forget_probability": ml_pred["forget_probability"],
            "risk_level": ml_pred["risk_level"],
            "guidance": {
                "focus_area": f"Targeted practice for skill {skill_id or 'general'}",
                "strategy": "Active Recall & Spaced Revision",
                "recommended_duration_minutes": 20 if ml_pred["risk_level"] == "HIGH" else 10,
                "action_plan": [
                    "Complete 5 diagnostic review questions",
                    "Focus on low-confidence concepts identified in past attempts",
                    "Verify mastery before next scheduled revision window"
                ]
            }
        }

    def explain_faculty_student_analysis(
        self,
        db: Session,
        requesting_user: User,
        student_id: str
    ) -> Dict[str, Any]:
        """
        USE CASE C — Faculty Student Analysis.
        """
        rag_context = self.rag_service.retrieve_student_context(db, requesting_user, student_id)
        cdata = rag_context["data"]
        ml_pred = cdata["deterministic_ml_prediction"]

        return {
            "student_id": student_id,
            "cohort_risk_summary": f"Student exhibits {ml_pred['risk_level']} decay risk across primary skills.",
            "top_risk_factors": ml_pred["top_risk_factors"],
            "top_protective_factors": ml_pred["top_protective_factors"],
            "faculty_guidance": "Consider assigning targeted practice or high-priority intervention."
        }

    def generate_grounded_mcqs(
        self,
        db: Session,
        subject_name: str,
        topic_name: str,
        difficulty: str = "INTERMEDIATE",
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        USE CASE E — Grounded MCQ Question Generation with Option & Correct Answer Validation.
        """
        prompt = f"""
Generate {count} Multiple Choice Questions (MCQs) for topic '{topic_name}' in subject '{subject_name}' at '{difficulty}' level.
Output ONLY a JSON array of objects with keys:
- question_text (string)
- question_type ("MCQ")
- difficulty_level ("{difficulty.upper()}")
- correct_answer ("A", "B", "C", or "D")
- explanation (string)
- options (array of 4 objects with keys "option_label" and "option_text")
"""
        raw_resp = self._query_ollama_raw(prompt)
        questions = []

        if raw_resp:
            try:
                clean_txt = raw_resp.strip()
                if clean_txt.startswith("```json"):
                    clean_txt = clean_txt[7:]
                if clean_txt.endswith("```"):
                    clean_txt = clean_txt[:-3]
                parsed = json.loads(clean_txt.strip())
                if isinstance(parsed, list):
                    questions = parsed
                elif isinstance(parsed, dict) and "questions" in parsed:
                    questions = parsed["questions"]
            except Exception as e:
                logger.warning(f"Ollama MCQ parsing error: {str(e)}")

        # Validate options and correct answer existence
        valid_questions = []
        labels = {"A", "B", "C", "D"}

        for q in questions:
            if isinstance(q, dict) and "question_text" in q and "options" in q:
                opts = q.get("options", [])
                corr = str(q.get("correct_answer", "A")).upper()
                opt_labels = set(o.get("option_label", "").upper() for o in opts if isinstance(o, dict))
                
                if len(opts) == 4 and corr in labels and corr in opt_labels:
                    valid_questions.append(q)

        # Fallback if Ollama is offline or generation failed validation
        if not valid_questions:
            valid_questions = [
                {
                    "question_text": f"What is the primary foundational concept of {topic_name}?",
                    "question_type": "MCQ",
                    "difficulty_level": difficulty.upper(),
                    "correct_answer": "A",
                    "explanation": f"Standard baseline review question for {topic_name}.",
                    "options": [
                        {"option_label": "A", "option_text": f"Core principle of {topic_name}"},
                        {"option_label": "B", "option_text": "Unrelated alternative principle"},
                        {"option_label": "C", "option_text": "Secondary concept"},
                        {"option_label": "D", "option_text": "None of the above"}
                    ]
                }
            ]

        return valid_questions

def get_ollama_rag_service() -> OllamaRAGService:
    return OllamaRAGService()
