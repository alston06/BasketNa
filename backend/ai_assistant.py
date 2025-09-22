from copilotkit.fastapi import CopilotKitRouter
from fastapi import APIRouter, Request
from pydantic import BaseModel
from pydantic_ai.agent import PydanticAIAgent


# Define the input schema for chat messages
class ChatMessage(BaseModel):
    message: str
    product_id: str | None = None
    product_name: str | None = None
    context: dict | None = None

# Set up the router
router = APIRouter()

# Initialize Pydantic AI agent (basic config, customize as needed)
ai_agent = PydanticAIAgent()

# CopilotKit router for chat
copilot_router = CopilotKitRouter(agent=ai_agent)

@router.post("/ai/chat")
async def ai_chat(msg: ChatMessage, request: Request):
    # Optionally enrich context with product info, web search, etc.
    # For now, just pass message and context to the agent
    response = await ai_agent.chat(
        msg.message,
        context=msg.context or {"product_id": msg.product_id, "product_name": msg.product_name}
    )
    return {"response": response}

# Mount CopilotKit router for streaming/chat features
router.include_router(copilot_router, prefix="/ai/copilotkit")
