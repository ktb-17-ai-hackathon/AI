from pydantic import BaseModel, Field
from typing import List, Literal, Optional

MarryStatus = Literal["single", "married", "divorced_or_widowed"]
DebtType = Literal["housing", "student", "credit", "mixed", "none"]
DebtInterestRateBand = Literal["LT_2", "BETWEEN_2_4", "BETWEEN_4_6", "GT_6", "UNKNOWN"]
TargetSubscriptionType = Literal["public", "private", "both"]
PriorityCriteria = Literal["transport", "commute", "school", "commercial", "price", "park", "view", "other"]

class LifeCycleSurveyRequest(BaseModel):
    # survey PK (옵션)
    surveyId: Optional[int] = Field(default=None, description="백엔드 설문 PK")

    # 1. 기본 정보
    age: int
    marryStatus: MarryStatus
    fMarryStatus: Optional[bool] = None  # 미혼일 때 결혼 계획 여부(없으면 null)

    # 2. 가족 & 자녀 계획
    childCount: int
    fChildCount: Optional[int] = None
    isDoubleIncome: Optional[bool] = None
    fIsDoubleIncome: Optional[bool] = None
    willContinueDoubleIncome: Optional[bool] = None

    # 3. 현재 집 / 부모
    currentDistrict: str
    isHouseholder: bool
    hasOwnedHouse: bool
    unhousedStartYear: Optional[int] = None
    isSupportingParents: bool
    fIsSupportingParents: Optional[bool] = None

    # 4. 돈 흐름 (소득/자산/부채)
    jobTitle: str
    jobDistrict: str
    annualIncome: int
    annualSideIncome: Optional[int] = 0
    monthlySavingAmount: int
    currentFinancialAssets: int
    additionalAssets: Optional[int] = 0
    targetSavingRate: Optional[int] = None  # %

    hasDebt: bool
    debtType: DebtType
    debtPrincipal: Optional[int] = None
    debtInterestRateBand: DebtInterestRateBand = "UNKNOWN"
    debtPrincipalPaid: Optional[int] = 0
    monthlyDebtPayment: Optional[int] = 0

    # 5. 청약 준비 상태
    hasSubscriptionAccount: bool
    subscriptionStartDate: Optional[str] = None       # "YYYY-MM-DD"
    fSubscriptionStartDate: Optional[str] = None      # "YYYY-MM-DD"
    monthlySubscriptionAmount: Optional[int] = 0
    totalSubscriptionBalance: Optional[int] = 0

    # 6. 살고 싶은 집/선호
    targetSubscriptionType: TargetSubscriptionType
    preferredRegion: str
    priorityCriteria: List[PriorityCriteria] = Field(default_factory=list)
    preferredHousingSize: str