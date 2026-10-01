"""Local-only browser fixture; operates exclusively on generated e2e accounts."""

import json
import re
import sys

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import build_engine
from app.models import AuthSession, User, VipCode


def main():
    payload = json.load(sys.stdin)
    account = payload["account"]
    if not re.fullmatch(r"e2e_[0-9a-f]{16}", account):
        raise SystemExit("Invalid fixture identity")
    engine = build_engine(connect_timeout=30, statement_timeout_ms=30000)
    try:
        with Session(engine) as db, db.begin():
            user = db.scalar(select(User).where(User.account == account))
            if user is None:
                return
            if payload["action"] == "promote":
                user.role = "admin"
            elif payload["action"] == "code":
                code_digest = payload["digest"]
                if not re.fullmatch(r"[0-9a-f]{64}", code_digest):
                    raise SystemExit("Invalid fixture digest")
                db.add(VipCode(digest=code_digest))
            elif payload["action"] == "cleanup":
                user.vip_code_id = None
                db.flush()
                db.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
                db.execute(delete(VipCode).where(VipCode.used_by == user.id))
                if payload.get("digest"):
                    db.execute(
                        delete(VipCode).where(VipCode.digest == payload["digest"])
                    )
                db.delete(user)
            else:
                raise SystemExit("Invalid fixture action")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
