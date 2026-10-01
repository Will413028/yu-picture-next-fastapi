import argparse
import getpass

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import build_engine
from app.models import User, VipCode
from app.security import digest
from app.user_schemas import UserCreate
from app.users import create_user


def main() -> None:
    parser = argparse.ArgumentParser(
        description="本機管理員與會員代碼初始化；不輸出憑證"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    admin = commands.add_parser("bootstrap-admin")
    admin.add_argument("account")
    commands.add_parser("add-vip-code")
    args = parser.parse_args()
    engine = build_engine(connect_timeout=30, statement_timeout_ms=30000)
    try:
        with Session(engine) as db, db.begin():
            if args.command == "bootstrap-admin":
                db.execute(text("LOCK TABLE users IN SHARE ROW EXCLUSIVE MODE"))
                if db.scalar(
                    select(User).where(User.role == "admin", ~User.is_deleted)
                ):
                    raise SystemExit("已有管理員；請使用管理介面")
                password = getpass.getpass("初始密碼（隱藏輸入）：")
                confirmation = getpass.getpass("確認密碼（隱藏輸入）：")
                if password != confirmation:
                    raise SystemExit("兩次密碼不一致")
                payload = UserCreate(
                    account=args.account, password=password, role="admin"
                )
                create_user(db, payload, role="admin", name="管理員")
            else:
                code = getpass.getpass("會員兌換碼（隱藏輸入）：")
                if not 1 <= len(code) <= 128 or not code.strip():
                    raise SystemExit("代碼長度不符合要求")
                db.add(VipCode(digest=digest(code)))
                db.flush()
        print("已完成，未輸出密碼或兌換碼")
    except IntegrityError:
        raise SystemExit("帳號或代碼已存在") from None
    except SQLAlchemyError:
        raise SystemExit("資料庫操作失敗，請稍後重試") from None
    except (ValidationError, HTTPException):
        raise SystemExit("輸入不符合要求，請檢查帳號與密碼") from None
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
