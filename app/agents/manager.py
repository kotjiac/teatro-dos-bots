from mcp_agent.core.fastagent import FastAgent
from app.core.models import AgentModel
from app.core.vector_store import buscar_memoria, adicionar_memoria
from typing import Dict
from app.config.config import LLM_MODEL
import sys

# Armazena os agentes carregados dinamicamente
registry: Dict[str, FastAgent] = {}

def criar_fastagent(agent: AgentModel) -> FastAgent:
    sys.argv = ["main.py", "--agent", agent.name, "--model", LLM_MODEL]

    fastagent = FastAgent(name=agent.name)

    @fastagent.agent(
        instruction=agent.instruction
    )

    async def handler(context: dict):
        context["__llm_config__"] = {
            "temperature": agent.temperature,
            "top_p": agent.top_p,
            "presence_penalty": agent.presence_penalty,
            "frequency_penalty": agent.frequency_penalty
        }

        mensagem = context.get("user_message", "")
        memoria = context.get("memoria", "")

        entrada_final = f"""Você é um agente que já teve interações com este usuário.
    Aqui estão os registros anteriores de conversa:

    {memoria}

    Agora o usuário disse:
    {mensagem}

    Responda levando em conta o histórico acima.
    """
        return entrada_final

    return fastagent

def registrar_agente(agent: AgentModel):
    if agent.name not in registry:
        agent_instance = criar_fastagent(agent)
        registry[agent.name] = agent_instance

def obter_agente(agent_name: str) -> FastAgent | None:
    return registry.get(agent_name)

async def executar_agente(agent_name: str, context: dict) -> str:
    agent = obter_agente(agent_name)
    if not agent:
        return f"Agente com id {agent_name} não encontrado."

    user_input = context.get("user_message", "")
    user_id = context.get("user_id", "anon")

    # Passo 1: buscar memórias
    memorias = buscar_memoria(agent_name, user_input)

    contexto_expandido = {
        **context,
        "memoria": "\n".join(memorias)
    }

    async with agent.run() as session:
        response = await session(contexto_expandido)

    # Passo 2: armazenar nova memória
    #adicionar_memoria(agent_name, user_input, user_id)
    adicionar_memoria(agent_name, user_input, {
        "user_id": user_id,
        "content": user_input
    })

    return response