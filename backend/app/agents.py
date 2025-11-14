from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from . import database, models, schemas
from typing import List, Optional
from .core.crew_stub import CrewAgent

router = APIRouter(tags=['agents'])

# in-memory agent runtime instances (per process)
runtime_agents = {}

def get_user_from_auth(authorization: Optional[str], db: Session):
    from .utils import decode_access_token
    if not authorization:
        return None
    token = authorization.split(' ',1)[1] if authorization.lower().startswith('bearer ') else authorization
    email = decode_access_token(token)
    if not email:
        return None
    return db.query(models.User).filter(models.User.email == email).first()

@router.post('/create', response_model=schemas.AgentOut)
def create_agent(config: schemas.AgentCreate, authorization: Optional[str] = Header(None), db: Session = Depends(database.get_db)):
    user = get_user_from_auth(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')

    agent = models.Agent(
        name=config.name, role=config.role, goal=config.goal,
        model_name=config.model_name, temperature=config.temperature, max_tokens=config.max_tokens,
        owner_id=user.id
    )
    db.add(agent); db.commit(); db.refresh(agent)

    # create runtime instance
    runtime_agents[agent.id] = CrewAgent(agent.name, role=agent.role, goal=agent.goal, model=agent.model_name, temperature=agent.temperature, max_tokens=agent.max_tokens)
    return agent

@router.get('/list', response_model=List[schemas.AgentOut])
def list_agents(authorization: Optional[str] = Header(None), db: Session = Depends(database.get_db)):
    user = get_user_from_auth(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')
    return db.query(models.Agent).filter(models.Agent.owner_id == user.id).all()

@router.delete('/{agent_id}')
def delete_agent(agent_id: int, authorization: Optional[str] = Header(None), db: Session = Depends(database.get_db)):
    user = get_user_from_auth(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id, models.Agent.owner_id == user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail='Agent not found')
    # remove runtime instance if exists
    runtime_agents.pop(agent.id, None)
    db.delete(agent); db.commit()
    return {'message':'deleted'}
