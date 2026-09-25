from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .ai import (
    generate_nutrition_tip_with_flash,
    generate_workout_gemini,
    update_workout_plan,
)
from .config import get_settings
from .crud import (
    delete_user,
    get_all_users,
    get_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from .database import get_db
from .schemas import (
    FeedbackBody,
    FeedbackRequest,
    PlanResponse,
    UserInput,
)


settings = get_settings()

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
        },
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user_input = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        user_input = user_input.normalized()

    except Exception as exc:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "app_name": settings.app_name,
                "error": str(exc),
            },
            status_code=400,
        )

    user = save_user(
        db,
        user_input,
    )

    workout = generate_workout_gemini(
        username=user.username,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )

    nutrition_tip = generate_nutrition_tip_with_flash(
        goal=user.goal,
    )

    plan = save_plan(
        db=db,
        user_id=user.user_id,
        original_plan=workout,
        nutrition_tip=nutrition_tip,
    )

    return templates.TemplateResponse(
    request=request,
    name="workout.html",
    context={
        "app_name": settings.app_name,
        "user": user,
        "plan": plan,
    },
)


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    plan = get_plan(
        db,
        user_id,
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Workout plan not found.",
        )

    feedback_body = FeedbackBody(
        feedback=feedback
    )

    updated_workout = update_workout_plan(
        original_plan=plan.original_plan,
        feedback=feedback_body.feedback,
        username=user.username,
        goal=user.goal,
        intensity=user.intensity,
    )

    nutrition_tip = generate_nutrition_tip_with_flash(
        goal=user.goal,
    )
    updated_plan = update_plan(
        db=db,
        plan=plan,
        updated_plan=updated_workout,
        feedback=feedback_body.feedback,
        nutrition_tip=nutrition_tip,
    )

    return templates.TemplateResponse(
        request=request,
        name="workout.html",
        context={
            "app_name": settings.app_name,
            "user": user,
            "plan": updated_plan,
            "message": "Your feedback has been applied.",
        },
    )

@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):
    if not settings.admin_enabled:
        raise HTTPException(
            status_code=403,
            detail="Admin access is disabled.",
        )

    users = get_all_users(db)

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "app_name": settings.app_name,
            "users": users,
        },
    )

@router.post(
    "/admin/delete/{user_id}",
)
def admin_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
):
    if not settings.admin_enabled:
        raise HTTPException(
            status_code=403,
            detail="Admin access is disabled.",
        )

    deleted = delete_user(
        db,
        user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return RedirectResponse(
        url="/view-all-users",
        status_code=303,
    )


@router.post(
    "/api/workouts",
    response_model=PlanResponse,
)
def api_generate_workout(
    data: UserInput,
    db: Session = Depends(get_db),
):
    data = data.normalized()

    user = save_user(
        db,
        data,
    )

    workout = generate_workout_gemini(
        username=user.username,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )

    nutrition_tip = generate_nutrition_tip_with_flash(
        goal=user.goal,
    )

    plan = save_plan(
        db=db,
        user_id=user.user_id,
        original_plan=workout,
        nutrition_tip=nutrition_tip,
    )

    return PlanResponse(
        user=user,
        original_plan=plan.original_plan,
        updated_plan=plan.updated_plan,
        nutrition_tip=plan.nutrition_tip,
        feedback=plan.feedback,
    )


@router.get(
    "/api/users/{user_id}",
    response_model=PlanResponse,
)
def api_get_user_plan(
    user_id: str,
    db: Session = Depends(get_db),
):
    user = get_user(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    plan = get_plan(
        db,
        user_id,
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Workout plan not found.",
        )

    return PlanResponse(
        user=user,
        original_plan=plan.original_plan,
        updated_plan=plan.updated_plan,
        nutrition_tip=plan.nutrition_tip,
        feedback=plan.feedback,
    )


@router.post(
    "/api/workouts/{user_id}/feedback",
    response_model=PlanResponse,
)
def api_submit_feedback(
    user_id: str,
    data: FeedbackRequest,
    db: Session = Depends(get_db),
):
    if data.user_id != user_id:
        raise HTTPException(
            status_code=400,
            detail="User ID mismatch.",
        )

    user = get_user(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    plan = get_plan(
        db,
        user_id,
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Workout plan not found.",
        )

    updated_workout = update_workout_plan(
        original_plan=plan.original_plan,
        feedback=data.feedback,
        username=user.username,
        goal=user.goal,
        intensity=user.intensity,
    )

    nutrition_tip = generate_nutrition_tip_with_flash(
        goal=user.goal,
    )

    updated_plan = update_plan(
        db=db,
        plan=plan,
        updated_plan=updated_workout,
        feedback=data.feedback,
        nutrition_tip=nutrition_tip,
    )

    return PlanResponse(
        user=user,
        original_plan=updated_plan.original_plan,
        updated_plan=updated_plan.updated_plan,
        nutrition_tip=updated_plan.nutrition_tip,
        feedback=updated_plan.feedback,
    )