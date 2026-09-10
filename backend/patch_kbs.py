import os
import re

kb_path = "app/api/endpoints/knowledge_bases.py"
with open(kb_path, "r") as f:
    content = f.read()

# Add require_workspace_access
content = content.replace("def create_knowledge_base(request: KnowledgeBaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):",
"""def create_knowledge_base(request: KnowledgeBaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_workspace_access(request.workspace_id, db, current_user)""")

content = content.replace("def list_knowledge_bases(workspace_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):",
"""def list_knowledge_bases(workspace_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_workspace_access(workspace_id, db, current_user)""")

content = content.replace("def get_knowledge_base(kb_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):",
"""def get_knowledge_base(kb_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kb = db.get(KnowledgeBase, kb_id)
    if not kb: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(kb.workspace_id, db, current_user)""")

content = content.replace("def delete_knowledge_base(kb_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):",
"""def delete_knowledge_base(kb_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kb = db.get(KnowledgeBase, kb_id)
    if not kb: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(kb.workspace_id, db, current_user)""")

# Remove duplicate kb = db.get(KnowledgeBase, kb_id) check in get and delete
content = re.sub(r'def get_knowledge_base.*?require_workspace_access\(kb\.workspace_id, db, current_user\)\n    kb = db\.get\(KnowledgeBase, kb_id\)\n    if not kb:\n        raise HTTPException\(status_code=404, detail="Not found"\)',
                 """def get_knowledge_base(kb_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kb = db.get(KnowledgeBase, kb_id)
    if not kb: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(kb.workspace_id, db, current_user)""", content, flags=re.DOTALL)

with open(kb_path, "w") as f:
    f.write(content)
print("Updated knowledge_bases.py")
