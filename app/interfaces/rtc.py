from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.agents.manager import executar_agente
from app.config.config import OPENAI_API_KEY
import uuid
from openai import OpenAI
import httpx
from typing import Optional

http_client = httpx.Client(timeout=120)
openai_client = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)

router = APIRouter()

class RTCTextRequest(BaseModel):
    agent_name: str
    message: str
    user_id: str = "anon"
    voice: Optional[str] = "nova"
    voice_instructions: Optional[str] = None  # Novo campo

@router.post("/rtc/text", summary="Texto para voz com agente")
async def rtc_text(payload: RTCTextRequest):
    context = {
        "user_id": payload.user_id,
        "user_message": payload.message
    }

    resposta_texto = await executar_agente(payload.agent_name, context)

    speech_path = f"/tmp/{uuid.uuid4()}.mp3"

    with openai_client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=payload.voice,
        input=resposta_texto,
        response_format="mp3",
        **({"instructions": payload.voice_instructions} if payload.voice_instructions else {})
    ) as response:
        response.stream_to_file(speech_path)

    return FileResponse(speech_path, media_type="audio/mpeg", filename="resposta.mp3")


@router.post("/rtc/audio", summary="Áudio para voz com agente")
async def rtc_audio(
    file: UploadFile = File(...),
    agent_name: str = File(...),
    user_id: str = File("anon"),
    voice: str = File("nova"),
    voice_instructions: Optional[str] = File(None)
):
    audio_data = await file.read()
    input_path = f"/tmp/{uuid.uuid4()}.wav"
    with open(input_path, "wb") as f:
        f.write(audio_data)

    with open(input_path, "rb") as f:
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )

    texto_usuario = transcript.text

    context = {
        "user_id": user_id,
        "user_message": texto_usuario
    }

    resposta_texto = await executar_agente(agent_name, context)

    speech_path = f"/tmp/{uuid.uuid4()}.mp3"

    with openai_client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=voice,
        input=resposta_texto,
        response_format="mp3",
        **({"instructions": voice_instructions} if voice_instructions else {})
    ) as response:
        response.stream_to_file(speech_path)

    return FileResponse(speech_path, media_type="audio/mpeg", filename="resposta.mp3")