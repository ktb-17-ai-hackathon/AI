from pydantic import BaseModel, Field
from typing import List, Literal, Optional

MarryStatus = Literal["single", "married", "divorced_or_widowed"]
DebtType = Literal["housing", "student", "credit", "mixed", "none"]
DebtInterestRateBand = Literal["LT_2", "BETWEEN_2_4", "BETWEEN_4_6", "GT_6", "UNKNOWN"]
TargetSubscriptionType = Literal["public", "private", "both"]
PriorityCriteria = Literal[
    "transport", "commute", "school", "commercial", "price", "park", "view", "other"
]

class LifeCycleSurveyRequest(BaseModel):
    # survey PK
    surveyId: Optional[int] = Field(default=None, description="백엔드 설문 PK")

    # 1. 기본 정보
    age: Optional[int] = None
    marryStatus: Optional[MarryStatus] = None
    fMarryStatus: Optional[bool] = None

    # 2. 가족 & 자녀 계획
    childCount: Optional[int] = None
    fChildCount: Optional[int] = None
    isDoubleIncome: Optional[bool] = None
    fIsDoubleIncome: Optional[bool] = None
    willContinueDoubleIncome: Optional[bool] = None

    # 3. 현재 집 / 부모
    currentDistrict: Optional[str] = None
    isHouseholder: Optional[bool] = None
    hasOwnedHouse: Optional[bool] = None
    unhousedStartYear: Optional[int] = None
    isSupportingParents: Optional[bool] = None
    fIsSupportingParents: Optional[bool] = None

    # 4. 돈 흐름 (소득/자산/부채)
    jobTitle: Optional[str] = None
    jobDistrict: Optional[str] = None
    annualIncome: Optional[int] = None
    annualSideIncome: Optional[int] = None
    monthlySavingAmount: Optional[int] = None
    currentFinancialAssets: Optional[int] = None
    additionalAssets: Optional[int] = None
    targetSavingRate: Optional[int] = None  # %

    hasDebt: Optional[bool] = None
    debtType: Optional[DebtType] = None
    debtPrincipal: Optional[int] = None
    debtInterestRateBand: Optional[DebtInterestRateBand] = None
    debtPrincipalPaid: Optional[int] = None
    monthlyDebtPayment: Optional[int] = None

    # 5. 청약 준비 상태
    hasSubscriptionAccount: Optional[bool] = None
    subscriptionStartDate: Optional[str] = None       # "YYYY-MM-DD"
    fSubscriptionStartDate: Optional[str] = None      # "YYYY-MM-DD"
    monthlySubscriptionAmount: Optional[int] = None
    totalSubscriptionBalance: Optional[int] = None

    # 6. 살고 싶은 집/선호
    targetSubscriptionType: Optional[TargetSubscriptionType] = None
    preferredRegion: Optional[str] = None
    priorityCriteria: Optional[List[PriorityCriteria]] = None
    preferredHousingSize: Optional[str] = None
