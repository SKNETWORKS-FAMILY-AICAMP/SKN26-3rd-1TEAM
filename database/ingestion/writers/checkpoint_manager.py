"""
인제션 작업의 안정성을 위한 체크포인트 관리 모듈입니다.
대량 데이터 적재 중 장애 발생 시, 마지막으로 성공한 지점을 기록하고
다시 실행했을 때 중단된 지점부터 재개할 수 있도록 상태 정보를 저장하고 로드합니다.
"""

import json
import os


class CheckpointManager:
    """적재 진행 상황을 기록하고 중단 지점부터 재개할 수 있게 돕는 매니저"""

    def __init__(self, checkpoint_file: str = "checkpoint.json"):
        self.checkpoint_file = checkpoint_file

    def load_checkpoint(self) -> int:
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "r") as f:
                return json.load(f).get("last_index", 0)
        return 0

    def save_checkpoint(self, index: int):
        with open(self.checkpoint_file, "w") as f:
            json.dump({"last_index": index}, f)

    def clear_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
