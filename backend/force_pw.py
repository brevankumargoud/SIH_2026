from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
u = db.query(User).filter_by(username="dev_user").first()
u.password_hash = get_password_hash("dev_password_only")
db.commit()
print("Password reset!")
