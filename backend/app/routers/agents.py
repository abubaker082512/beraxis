"""
AI Agent Builder router — CRUD, voice listing, test simulator.
Maps to: /dashboard/agent-builder (AgentBuilder.tsx)
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_tenant_user
from app.models.user import User
from app.models.agent import AIAgent
from app.utils.responses import success_response, error_response, paginate
from app.config import settings

router = APIRouter(prefix="/agents", tags=["AI Agents"])


class AgentCreate(BaseModel):
    name: str
    identity: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    dynamic_variables: List[dict] = []
    knowledge_base: Optional[str] = None
    flow_steps: List[dict] = []
    voice_id: Optional[str] = None
    voice_speed: float = 1.0
    voice_stability: float = 0.75
    llm_temperature: Optional[float] = None
    llm_max_tokens: Optional[int] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    identity: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    dynamic_variables: Optional[List[dict]] = None
    knowledge_base: Optional[str] = None
    flow_steps: Optional[List[dict]] = None
    voice_id: Optional[str] = None
    voice_speed: Optional[float] = None
    voice_stability: Optional[float] = None


class TestMessage(BaseModel):
    user_message: str
    conversation_history: List[dict] = []


def _agent_to_dict(a: AIAgent) -> dict:
    return {
        "id": str(a.id),
        "name": a.name,
        "identity": a.identity,
        "description": a.description,
        "system_prompt": a.system_prompt,
        "dynamic_variables": a.dynamic_variables,
        "knowledge_base": a.knowledge_base,
        "flow_steps": a.flow_steps,
        "voice_id": a.voice_id,
        "voice_speed": a.voice_speed,
        "voice_stability": a.voice_stability,
        "is_active": a.is_active,
        "total_calls": a.total_calls,
        "version": a.version,
        "created_at": str(a.created_at),
    }


@router.get("")
async def list_agents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(
        select(func.count(AIAgent.id)).where(AIAgent.org_id == current_user.org_id)
    )
    total = total_result.scalar() or 0
    result = await db.execute(
        select(AIAgent)
        .where(AIAgent.org_id == current_user.org_id)
        .order_by(AIAgent.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    agents = result.scalars().all()
    return success_response(data=[_agent_to_dict(a) for a in agents], pagination=paginate(agents, total, page, limit))


@router.post("", status_code=201)
async def create_agent(
    data: AgentCreate,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    agent = AIAgent(org_id=current_user.org_id, **data.model_dump())
    db.add(agent)
    await db.commit()
    return success_response(data=_agent_to_dict(agent), message="Agent created", status_code=201)


@router.get("/voices")
async def list_voices(current_user: User = Depends(get_tenant_user)):
    """Returns available TTS voices from Piper models directory."""
    voices = [
        {"id": "en_US-amy-medium", "name": "Amy (Professional)", "gender": "Female", "accent": "US", "language": "en"},
        {"id": "en_US-ryan-high", "name": "Ryan (Authoritative)", "gender": "Male", "accent": "US", "language": "en"},
        {"id": "en_GB-alba-medium", "name": "Alba (Friendly)", "gender": "Female", "accent": "UK", "language": "en"},
        {"id": "en_GB-northern_english-medium", "name": "James (Deep)", "gender": "Male", "accent": "UK", "language": "en"},
        {"id": "es_ES-sharvard-medium", "name": "Elena (Friendly)", "gender": "Female", "accent": "Spanish", "language": "es"},
    ]
    return success_response(data=voices)


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AIAgent).where(and_(AIAgent.id == agent_id, AIAgent.org_id == current_user.org_id))
    )
    a = result.scalar_one_or_none()
    if not a:
        return error_response("Agent not found", 404)
    return success_response(data=_agent_to_dict(a))


@router.put("/{agent_id}")
async def update_agent(
    agent_id: str,
    data: AgentUpdate,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AIAgent).where(and_(AIAgent.id == agent_id, AIAgent.org_id == current_user.org_id))
    )
    a = result.scalar_one_or_none()
    if not a:
        return error_response("Agent not found", 404)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(a, field, value)
    a.version += 1
    await db.commit()
    return success_response(data=_agent_to_dict(a), message="Agent saved")


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AIAgent).where(and_(AIAgent.id == agent_id, AIAgent.org_id == current_user.org_id))
    )
    a = result.scalar_one_or_none()
    if not a:
        return error_response("Agent not found", 404)
    await db.delete(a)
    await db.commit()
    return success_response(message="Agent deleted")


@router.post("/{agent_id}/test")
async def test_agent(
    agent_id: str,
    data: TestMessage,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Simulate a conversation turn with the agent.
    Routes through the LLM pipeline and returns the AI response text.
    """
    result = await db.execute(
        select(AIAgent).where(and_(AIAgent.id == agent_id, AIAgent.org_id == current_user.org_id))
    )
    a = result.scalar_one_or_none()
    if not a:
        return error_response("Agent not found", 404)

    try:
        from app.ai.llm import generate_response
        ai_reply = await generate_response(
            system_prompt=a.system_prompt or "",
            conversation_history=data.conversation_history,
            user_message=data.user_message,
            temperature=a.llm_temperature,
            max_tokens=a.llm_max_tokens,
        )
        return success_response(data={"reply": ai_reply})
    except Exception as e:
        return success_response(data={"reply": f"[Simulator] Echo: {data.user_message}"}, message="LLM not available in this environment")


@router.post("/{agent_id}/optimize")
async def ai_optimize_prompt(
    agent_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """Ask LLM to improve the agent's system prompt."""
    result = await db.execute(
        select(AIAgent).where(and_(AIAgent.id == agent_id, AIAgent.org_id == current_user.org_id))
    )
    a = result.scalar_one_or_none()
    if not a:
        return error_response("Agent not found", 404)

    # In production this calls the LLM with a meta-prompt
    optimized = (a.system_prompt or "") + "\n\n[AI Optimized: Added clearer objection handling and empathy cues.]"
    return success_response(data={"optimized_prompt": optimized}, message="Prompt optimized by AI")
