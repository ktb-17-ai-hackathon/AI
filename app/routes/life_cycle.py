from fastapi import APIRouter, HTTPException
from app.schemas.life_cycle import LifeCycleSurveyRequest
from app.schemas.life_cycle_response import LifeCyclePlanResponse
from app.services.life_cycle_service import LifeCycleService
from app.services.gemini_service import GeminiService
from app.repositories.life_cycle_repo import LifeCycleRepo

gemini_service = GeminiService()
repo = LifeCycleRepo()
life_cycle_service = LifeCycleService(
    gemini=gemini_service,
    repo=repo
)

router = APIRouter(prefix="/ai", tags=["life-cycle"])

@router.post(
    "/cheongyak-plan",
    response_model=LifeCyclePlanResponse
)
def generate_life_cycle_plan(req: LifeCycleSurveyRequest):
    try:
        return life_cycle_service.generate_plan(
            user_data=req.model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def test_connection():
    return {"status": "OK", "message": "AI server OK."}