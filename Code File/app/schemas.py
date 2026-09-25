from pydantic import BaseModel, ConfigDict, Field


class UserInput(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=120,
    )

    user_id: str = Field(
        min_length=1,
        max_length=100,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        le=500,
    )

    goal: str = Field(
        min_length=2,
        max_length=50,
    )

    intensity: str = Field(
        min_length=2,
        max_length=20,
    )

    def normalized(self):
        return self.model_copy(
            update={
                "username": self.username.strip(),
                "user_id": self.user_id.strip(),
                "goal": self.goal.strip().lower(),
                "intensity": self.intensity.strip().lower(),
            }
        )


class FeedbackRequest(BaseModel):
    user_id: str = Field(
        min_length=1,
        max_length=100,
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )


class FeedbackBody(BaseModel):
    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    user_id: str
    username: str
    age: int
    weight: float
    goal: str
    intensity: str


class PlanResponse(BaseModel):
    user: UserResponse

    original_plan: str

    updated_plan: str | None

    nutrition_tip: str

    feedback: str | None