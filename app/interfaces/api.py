from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.models import AgentModel
from app.agents.manager import registrar_agente, executar_agente
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# === MODELOS === #

class AgentCreateRequest(BaseModel):
    name: str
    instruction: str
    temperature: float = 0.7
    top_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0

class AgentMessageRequest(BaseModel):
    agent_name: str
    message: str
    user_id: str = "anon"

# === ENDPOINTS === #

@router.get("/agents")
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentModel))
    agents = result.scalars().all()
    return [
        {
            "id": str(agent.id),
            "name": agent.name,
            "instruction": agent.instruction,
            "temperature": agent.temperature,
            "top_p": agent.top_p,
            "presence_penalty": agent.presence_penalty,
            "frequency_penalty": agent.frequency_penalty,
            "created_at": agent.created_at
        }
        for agent in agents
    ]

@router.post("/create-agent")
async def create_agent(data: AgentCreateRequest, db: AsyncSession = Depends(get_db)):
    agent = AgentModel(
        name=data.name,
        instruction=data.instruction,
        temperature=data.temperature,
        top_p=data.top_p,
        presence_penalty=data.presence_penalty,
        frequency_penalty=data.frequency_penalty
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    registrar_agente(agent)
    return {"id": agent.id, "message": "Agente criado com sucesso."}
class RegisterAgentRequest(BaseModel):
    name: str

@router.delete("/delete-agent", summary="Remove um agente do banco")
async def delete_agent(name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentModel).where(AgentModel.name == name))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado.")

    await db.delete(agent)
    await db.commit()

    return {"message": f"Agente '{name}' removido com sucesso."}

@router.post("/register-agent")
async def register_agent(payload: RegisterAgentRequest, db: AsyncSession = Depends(get_db)):
    from app.agents.manager import registrar_agente
    from sqlalchemy import select

    result = await db.execute(select(AgentModel).where(AgentModel.name == payload.name))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado no banco.")

    registrar_agente(agent)
    return {
        "message": f"Agente '{payload.name}' registrado com sucesso.",
        "agent_name": payload.name,
        "available_now": True
    }

@router.post("/message")
async def talk_to_agent(payload: AgentMessageRequest):
    context = {
        "user_id": payload.user_id,
        "user_message": payload.message
    }
    response = await executar_agente(str(payload.agent_name), context)
    return {"response": response}

@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow()}


