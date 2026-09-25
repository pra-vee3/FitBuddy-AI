from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Plan, User
from .schemas import UserInput


def save_user(
    db: Session,
    data: UserInput,
) -> User:

    user = db.scalar(
        select(User).where(
            User.user_id == data.user_id
        )
    )

    if user:
        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity

    else:
        user = User(
            **data.model_dump()
        )

        db.add(user)

    db.commit()

    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user_id: str,
    original_plan: str,
    nutrition_tip: str,
) -> Plan:

    plan = Plan(
        user_id=user_id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip,
    )

    db.add(plan)

    db.commit()

    db.refresh(plan)

    return plan


def get_user(
    db: Session,
    user_id: str,
):

    return db.scalar(
        select(User).where(
            User.user_id == user_id
        )
    )


def get_plan(
    db: Session,
    user_id: str,
):

    return db.scalar(
        select(Plan)
        .where(Plan.user_id == user_id)
        .order_by(Plan.id.desc())
    )


def update_plan(
    db: Session,
    plan: Plan,
    updated_plan: str,
    feedback: str,
    nutrition_tip: str,
):

    plan.updated_plan = updated_plan
    plan.feedback = feedback
    plan.nutrition_tip = nutrition_tip

    plan.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()

    db.refresh(plan)

    return plan


def get_all_users(
    db: Session,
):

    return list(
        db.scalars(
            select(User)
            .order_by(
                User.created_at.desc()
            )
        ).all()
    )


def delete_user(
    db: Session,
    user_id: str,
) -> bool:

    user = get_user(
        db,
        user_id,
    )

    if not user:
        return False

    db.query(Plan).filter(
        Plan.user_id == user_id
    ).delete()

    db.delete(user)

    db.commit()

    return True