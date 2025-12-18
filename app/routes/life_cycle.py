from fastapi import APIRouter, HTTPException
from app.schemas.life_cycle import LifeCycleSurveyRequest
from app.schemas.life_cycle_response import LifeCyclePlanResponse
from app.services.life_cycle_service import LifeCycleService
from app.services.gemini_service import (
    GeminiService,
    GeminiServiceError,
    GeminiServiceTimeout,
    GeminiServiceUnavailable,
)
from app.repositories.life_cycle_repo import LifeCycleRepo

gemini_service = GeminiService()
repo = LifeCycleRepo()
life_cycle_service = LifeCycleService(gemini=gemini_service, repo=repo)

router = APIRouter(prefix="/ai", tags=["life-cycle"])


@router.post("/cheongyak-plan", response_model=LifeCyclePlanResponse)
def generate_life_cycle_plan(req: LifeCycleSurveyRequest):
    try:
        # ✅ Pydantic v2
        return life_cycle_service.generate_plan(user_data=req.model_dump())

    # ✅ Gemini 타임아웃 → 504
    except GeminiServiceTimeout as e:
        raise HTTPException(status_code=504, detail=str(e))

    # ✅ Gemini 과부하/일시 장애(503/429) → 503
    except GeminiServiceUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))

    # ✅ Gemini 기타 업스트림 오류 → 502
    except GeminiServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # ✅ LLM 결과(JSON 깨짐/스키마 불일치) → 502
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # ✅ 진짜 우리 서버 버그만 500
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/health")
def test_connection():
    return {"status": "OK", "message": "AI server OK."}