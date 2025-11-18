from fastapi import APIRouter, Depends, HTTPException, Body, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from . import database, models, schemas
from .agents import runtime_agents
from typing import List
from .core.crew_stub import CrewAgent
import json

router = APIRouter(tags=['chat'])

def get_user_from_auth(authorization: str, db: Session):
    from .utils import decode_access_token
    if not authorization:
        return None
    token = authorization.split(' ',1)[1] if authorization.lower().startswith('bearer ') else authorization
    email = decode_access_token(token)
    if not email:
        return None
    return db.query(models.User).filter(models.User.email == email).first()

@router.post('/{agent_id}/send', response_model=dict)
def send_message(agent_id: int, payload: schemas.ChatMessageCreate, authorization: str = Header(None), db: Session = Depends(database.get_db)):
    user = get_user_from_auth(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id, models.Agent.owner_id == user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail='Agent not found')

    # ensure runtime instance
    runtime = runtime_agents.get(agent.id)
    if not runtime:
        runtime = CrewAgent(
            agent.name,
            role=agent.role,
            goal=agent.goal,
            model=agent.model_name,
            temperature=agent.temperature or 0.7,
            max_tokens=agent.max_tokens or 1024,
            top_p=agent.top_p,
            top_k=agent.top_k,
            api_key=agent.api_key,
            provider=agent.provider
        )
        runtime_agents[agent.id] = runtime
    else:
        # Update runtime instance with latest agent settings
        runtime.api_key = agent.api_key
        runtime.provider = agent.provider
        runtime.temperature = agent.temperature or 0.7
        runtime.max_tokens = agent.max_tokens or 1024
        runtime.top_p = agent.top_p
        runtime.top_k = agent.top_k
        runtime.model = agent.model_name
        runtime.role = agent.role
        runtime.goal = agent.goal

    api_key = (payload.api_key or agent.api_key or '').strip()
    if not api_key:
        raise HTTPException(status_code=400, detail='No API key configured for this agent. Add one when creating the agent or provide api_key with this request.')

    # save user message
    user_msg = models.ChatMessage(agent_id=agent.id, sender='user', message=payload.message)
    db.add(user_msg); db.commit(); db.refresh(user_msg)

    # get response from agent
    try:
        response_text = runtime.think(payload.message, api_key)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    bot_msg = models.ChatMessage(agent_id=agent.id, sender='agent', message=response_text)
    db.add(bot_msg); db.commit(); db.refresh(bot_msg)

    return {'response': response_text, 'user_message_id': user_msg.id, 'bot_message_id': bot_msg.id}

@router.post('/{agent_id}/send-stream')
def send_message_stream(agent_id: int, payload: schemas.ChatMessageCreate, authorization: str = Header(None), db: Session = Depends(database.get_db)):
    user = get_user_from_auth(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id, models.Agent.owner_id == user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail='Agent not found')

    # ensure runtime instance
    runtime = runtime_agents.get(agent.id)
    if not runtime:
        runtime = CrewAgent(
            agent.name,
            role=agent.role,
            goal=agent.goal,
            model=agent.model_name,
            temperature=agent.temperature or 0.7,
            max_tokens=agent.max_tokens or 1024,
            top_p=agent.top_p,
            top_k=agent.top_k,
            api_key=agent.api_key,
            provider=agent.provider
        )
        runtime_agents[agent.id] = runtime
    else:
        # Update runtime instance with latest agent settings
        runtime.api_key = agent.api_key
        runtime.provider = agent.provider
        runtime.temperature = agent.temperature or 0.7
        runtime.max_tokens = agent.max_tokens or 1024
        runtime.top_p = agent.top_p
        runtime.top_k = agent.top_k
        runtime.model = agent.model_name
        runtime.role = agent.role
        runtime.goal = agent.goal

    api_key = (payload.api_key or agent.api_key or '').strip()
    if not api_key:
        raise HTTPException(status_code=400, detail='No API key configured for this agent. Add one when creating the agent or provide api_key with this request.')

    # save user message
    user_msg = models.ChatMessage(agent_id=agent.id, sender='user', message=payload.message)
    db.add(user_msg); db.commit(); db.refresh(user_msg)

    def generate():
        try:
            full_response = ''
            # Send initial message with user message ID
            yield f"data: {json.dumps({'type': 'start', 'user_message_id': user_msg.id})}\n\n"
            
            # Stream response from agent
            for chunk in runtime.think_stream(payload.message, api_key):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            # Save complete response to database
            bot_msg = models.ChatMessage(agent_id=agent.id, sender='agent', message=full_response)
            db.add(bot_msg); db.commit(); db.refresh(bot_msg)
            
            # Send final message with bot message ID
            yield f"data: {json.dumps({'type': 'done', 'bot_message_id': bot_msg.id, 'full_response': full_response})}\n\n"
        except RuntimeError as exc:
            error_data = json.dumps({'type': 'error', 'message': str(exc)})
            yield f"data: {error_data}\n\n"
        except Exception as exc:
            error_data = json.dumps({'type': 'error', 'message': f'Unexpected error: {str(exc)}'})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get('/{agent_id}/history', response_model=List[schemas.ChatMessageOut])
def history(agent_id: int, authorization: str = Header(None), db: Session = Depends(database.get_db)):
    user = get_user_from_auth(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id, models.Agent.owner_id == user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail='Agent not found')
    msgs = db.query(models.ChatMessage).filter(models.ChatMessage.agent_id == agent.id).order_by(models.ChatMessage.created_at.asc()).all()
    return msgs
