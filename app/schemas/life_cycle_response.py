from pydantic import BaseModel
from typing import List, Literal

ConfidenceLevel = Literal["HIGH", "MEDIUM", "LOW"]
RecommendedHorizon = Literal["SHORT_3", "MID_5", "LONG_10"]

class Summary(BaseModel):
    title: str
    body: str

class Diagnosis(BaseModel):
    canBuyWithCheongyak: bool
    confidenceLevel: ConfidenceLevel
    reasons: List[str]

class SavingProjection(BaseModel):
    year: int
    amount: int

class ChartData(BaseModel):
    savingProjectionByYear: List[SavingProjection]

class TimeHorizonStrategy(BaseModel):
    now: str
    threeYears: str
    fiveYears: str

class PlanMeta(BaseModel):
    recommendedHorizon: RecommendedHorizon
    reason: str

class LifeCyclePlanResponse(BaseModel):
    summary: Summary
    diagnosis: Diagnosis
    timeHorizonStrategy: TimeHorizonStrategy
    chartData: ChartData
    planMeta: PlanMeta