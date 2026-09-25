from google import genai

from .config import get_settings


settings = get_settings()


def _client():
    if not settings.gemini_api_key:
        return None

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def _generate(
    model: str,
    prompt: str,
) -> str:

    client = _client()

    if client is None:
        raise RuntimeError(
            "Gemini API key is not configured."
        )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text.strip()


def _demo_workout(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    return f"""
FITBUDDY 7-DAY WORKOUT PLAN

User: {username}
Age: {age}
Weight: {weight:g} kg
Goal: {goal}
Intensity: {intensity}

DAY 1 — FULL BODY

Warm-up:
• 5–7 minutes brisk walking
• Shoulder circles
• Hip mobility

Workout:
• Squats — 3 × 10
• Push-ups — 3 × 8–12
• Dumbbell rows — 3 × 10
• Glute bridges — 3 × 12
• Plank — 3 × 30 seconds

Rest:
60–90 seconds between sets.

Cooldown:
5 minutes of easy movement and stretching.


DAY 2 — CARDIO

Warm-up:
5 minutes easy walking.

Workout:
• 25 minutes brisk walking or cycling
• Include 5 × 1-minute faster intervals

Cooldown:
5 minutes easy pace.


DAY 3 — LOWER BODY + CORE

Warm-up:
7 minutes.

Workout:
• Lunges — 3 × 10 per side
• Glute bridges — 3 × 12
• Calf raises — 3 × 15
• Dead bug — 3 × 10 per side
• Side plank — 3 × 20 seconds per side

Cooldown:
5–8 minutes gentle stretching.


DAY 4 — RECOVERY

• 20–30 minutes comfortable walking
• Gentle mobility
• Light stretching

Keep the effort low.


DAY 5 — UPPER BODY + CORE

Warm-up:
7 minutes.

Workout:
• Incline push-ups — 3 × 10
• Rows — 3 × 10
• Shoulder press — 3 × 10
• Bodyweight squats — 3 × 12
• Side plank — 3 × 20 seconds per side

Cooldown:
5 minutes.


DAY 6 — CARDIO + MOBILITY

Cardio:
30 minutes moderate-intensity walking,
cycling, swimming, or another comfortable activity.

Mobility:
10 minutes.


DAY 7 — REST

Full rest or a comfortable 15–20 minute walk.

Focus on:
• Sleep
• Hydration
• Recovery


PROGRESSION

Increase exercise volume gradually.

Keep approximately 2–3 repetitions in reserve
rather than training to complete exhaustion.


SAFETY

This is general fitness guidance rather than medical advice.

Stop exercising if you experience concerning symptoms
such as chest pain, severe dizziness, fainting, or unusual
shortness of breath, and seek appropriate medical attention.
"""


def generate_workout_gemini(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_workout(
            username=username,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a practical 7-day workout plan for this user:

Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}

Requirements:

1. Provide exactly Day 1 through Day 7.
2. Include a warm-up for workout days.
3. Include the main exercises.
4. Include sets/repetitions or duration.
5. Include rest guidance.
6. Include cooldown or recovery guidance.
7. Include at least one recovery/rest day.
8. Keep the language practical and easy to understand.
9. Do not diagnose medical conditions.
10. Do not provide medical treatment.
11. Do not recommend dangerous exercise practices.
12. Include a short safety note.

Return only the workout plan.
"""

    return _generate(
        model=settings.gemini_workout_model,
        prompt=prompt,
    )


def generate_nutrition_tip_with_flash(
    goal: str,
) -> str:

    if settings.demo_mode or not settings.gemini_api_key:

        tips = {
            "weight loss": (
                "Prioritize vegetables, protein-rich foods, "
                "whole grains, hydration, and consistent meal timing."
            ),
            "muscle gain": (
                "Include a protein source in regular meals, "
                "stay hydrated, and support training with balanced meals."
            ),
            "general wellness": (
                "Aim for balanced meals with vegetables, "
                "protein, whole grains, healthy fats, and enough water."
            ),
            "flexibility": (
                "Stay hydrated and include a variety of "
                "fruits, vegetables, protein, and whole foods."
            ),
        }

        return tips.get(
            goal.lower(),
            tips["general wellness"],
        )

    prompt = f"""
Give one concise nutrition and recovery tip for a fitness user
whose goal is: {goal}

Requirements:
- Maximum 80 words.
- Practical and easy to understand.
- Do not diagnose medical conditions.
- Do not prescribe medical diets.
- Do not recommend dangerous calorie restrictions.
- Do not recommend unnecessary supplements.

Return only the tip.
"""

    return _generate(
        model=settings.gemini_tip_model,
        prompt=prompt,
    )


def update_workout_plan(
    original_plan: str,
    feedback: str,
    username: str,
    goal: str,
    intensity: str,
) -> str:

    if settings.demo_mode or not settings.gemini_api_key:

        return f"""
FITBUDDY UPDATED 7-DAY WORKOUT PLAN

User: {username}
Goal: {goal}
Intensity: {intensity}

USER FEEDBACK:
{feedback}


UPDATED PLAN

The original plan has been adjusted based on the user's
feedback.

Keep the following structure:

DAY 1 — FULL BODY
Use a comfortable level of effort and adjust exercise
difficulty according to the feedback.

DAY 2 — CARDIO
Choose a comfortable cardio activity such as walking
or cycling.

DAY 3 — LOWER BODY + CORE
Use controlled movements and moderate volume.

DAY 4 — RECOVERY
Light walking, mobility, and stretching.

DAY 5 — UPPER BODY + CORE
Use manageable resistance and controlled repetitions.

DAY 6 — CARDIO + MOBILITY
Moderate cardio followed by mobility work.

DAY 7 — REST
Full rest or an easy walk.

FEEDBACK APPLIED:
{feedback}


SAFETY

This is general fitness guidance rather than medical advice.
Stop exercising if you experience concerning symptoms and
seek appropriate medical attention.
"""

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

The user originally received this workout plan:

--- ORIGINAL PLAN ---
{original_plan}
--- END ORIGINAL PLAN ---

The user provided this feedback:

--- FEEDBACK ---
{feedback}
--- END FEEDBACK ---

User:
Name: {username}
Goal: {goal}
Intensity: {intensity}

Create a complete revised 7-day workout plan.

Requirements:

1. Incorporate the user's feedback.
2. Preserve useful parts of the original plan when appropriate.
3. Provide exactly Day 1 through Day 7.
4. Include warm-up, main workout, sets/repetitions or duration,
   rest, and cooldown/recovery where appropriate.
5. Include at least one rest or recovery day.
6. Use practical, easy-to-understand language.
7. Do not diagnose medical conditions.
8. Do not provide medical treatment.
9. Do not recommend dangerous exercise practices.
10. Include a short safety note.

Return only the revised workout plan.
"""

    return _generate(
        model=settings.gemini_workout_model,
        prompt=prompt,
    )