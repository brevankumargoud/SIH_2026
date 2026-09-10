import os
import re

path = "app/api/endpoints/conversations.py"
with open(path, "r") as f:
    content = f.read()

imports = """from app.api.deps import get_current_user, require_workspace_access
from app.models.user import User
from fastapi import HTTPException
"""
content = content.replace("from app.services.chat_service import ChatService\n", "from app.services.chat_service import ChatService\n" + imports)

# replace function signatures
content = content.replace("def create_conversation(request: ConversationCreate, db: Session = Depends(get_db)):",
"""def create_conversation(request: ConversationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_workspace_access(request.workspace_id, db, current_user)""")

content = content.replace("def list_conversations(workspace_id: uuid.UUID, db: Session = Depends(get_db)):",
"""def list_conversations(workspace_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_workspace_access(workspace_id, db, current_user)""")

content = content.replace("def get_conversation(conversation_id: uuid.UUID, db: Session = Depends(get_db)):",
"""def get_conversation(conversation_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ChatService(db)
    conv = svc.get_conversation(conversation_id)
    if not conv: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(conv.workspace_id, db, current_user)
    return conv""")
content = re.sub(r'def get_conversation.*?return conv', 
"""def get_conversation(conversation_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ChatService(db)
    conv = svc.get_conversation(conversation_id)
    if not conv: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(conv.workspace_id, db, current_user)
    return conv""", content, flags=re.DOTALL)


content = content.replace("def get_messages(conversation_id: uuid.UUID, limit: int = 50, db: Session = Depends(get_db)):",
"""def get_messages(conversation_id: uuid.UUID, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ChatService(db)
    conv = svc.get_conversation(conversation_id)
    if not conv: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(conv.workspace_id, db, current_user)""")

content = content.replace("def send_message(conversation_id: uuid.UUID, request: ChatRequest, db: Session = Depends(get_db)):",
"""def send_message(conversation_id: uuid.UUID, request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ChatService(db)
    conv = svc.get_conversation(conversation_id)
    if not conv: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(conv.workspace_id, db, current_user)""")

with open(path, "w") as f:
    f.write(content)
