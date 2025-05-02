from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from app.interfaces import api
from app.interfaces import rtc
from app.core.vector_store import inicializar_colecao
from app.config.config import DEBUG

# Inicializa a coleção Qdrant ao iniciar o app
inicializar_colecao()

# Cria a aplicação FastAPI
app = FastAPI(title="Teatro dos Bots", version="0.1.0", debug=DEBUG)

mcp = FastApiMCP(
    app,
    # Optional parameters
    name="Teatro dos bots MCP Server",
    description="Teatro dos bots MCP Server",
    describe_all_responses=True,
    describe_full_response_schema=True
)

# Registra os endpoints
app.include_router(api.router)
app.include_router(rtc.router)

# Mount the MCP server directly to your FastAPI app
mcp.mount()

mcp.setup_server()