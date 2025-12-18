from typing import Any, Dict, Optional
from datetime import datetime

class LifeCycleRepo:
    """
    지금은 DB 없음 → 나중에 Mongo/MySQL/Redis 등으로 교체 가능
    현재는 요청/응답을 저장할 '자리'만 제공
    """
    def save_record(
        self,
        task: str,
        user_data: Dict[str, Any],
        question: Optional[str],
        result: str
    ) -> None:
        # TODO: DB 저장 구현
        # 지금은 그냥 콘솔 로그 정도만
        print("[LifeCycleRecord]", {
            "ts": datetime.utcnow().isoformat(),
            "task": task,
            "question": question,
            "user_data_keys": list(user_data.keys()),
            "result_preview": result[:120]
        })