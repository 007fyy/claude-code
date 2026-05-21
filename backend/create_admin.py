"""
创建或提升管理员账号。
用法：
  python backend/create_admin.py                        # 使用默认账号
  python backend/create_admin.py admin@qq.com Admin123  # 指定邮箱和密码
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models.user import User
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

email    = sys.argv[1] if len(sys.argv) > 1 else "admin@qq.com"
password = sys.argv[2] if len(sys.argv) > 2 else "Admin123456"

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.role = "admin"
        db.commit()
        print(f"[OK] 已将 {email} 提升为管理员")
    else:
        user = User(
            email=email,
            password_hash=pwd_ctx.hash(password),
            nickname="管理员",
            role="admin",
        )
        db.add(user)
        db.commit()
        print(f"[OK] 管理员账号已创建")
        print(f"     邮箱：{email}")
        print(f"     密码：{password}")
finally:
    db.close()
