import time
from collections import deque
import logging
from core.definitions import DriverState, AnalysisEvent

logger = logging.getLogger(__name__)

class EnhancedStateManager:
    """향상된 상태 관리자"""

    def __init__(self):
        self.current_state = DriverState.SAFE
        self.state_start_time = time.time()
        self.state_history = deque(maxlen=100)

    def handle_event(self, event: AnalysisEvent):
        new_state = self._determine_enhanced_new_state(event)
        if new_state != self.current_state:
            self.state_history.append(
                {
                    "timestamp": time.time(),
                    "from_state": self.current_state,
                    "to_state": new_state,
                    "trigger_event": event,
                }
            )
            logger.info(
                f"상태 전환: {self.current_state.value} -> {new_state.value} (이벤트: {event.value})"
            )
            self.current_state = new_state
            self.state_start_time = time.time()

    def _determine_enhanced_new_state(self, event: AnalysisEvent) -> DriverState:
        current_duration = time.time() - self.state_start_time
        immediate_transitions = {
            AnalysisEvent.PHONE_USAGE_CONFIRMED: DriverState.PHONE_USAGE,
            AnalysisEvent.MICROSLEEP_PREDICTED: DriverState.MICROSLEEP,
            AnalysisEvent.EMOTION_STRESS_DETECTED: DriverState.EMOTIONAL_STRESS,
            AnalysisEvent.PREDICTIVE_RISK_HIGH: DriverState.PREDICTIVE_WARNING,
        }
        if event in immediate_transitions:
            return immediate_transitions[event]
        if event == AnalysisEvent.FATIGUE_ACCUMULATION:
            if self.current_state == DriverState.FATIGUE_LOW:
                return DriverState.FATIGUE_HIGH
            else:
                return DriverState.FATIGUE_LOW
        if event == AnalysisEvent.ATTENTION_DECLINE:
            if self.current_state == DriverState.DISTRACTION_NORMAL:
                return DriverState.DISTRACTION_DANGER
            else:
                return DriverState.DISTRACTION_NORMAL
        if event == AnalysisEvent.DISTRACTION_OBJECT_DETECTED:
            if self.current_state in [DriverState.FATIGUE_HIGH, DriverState.EMOTIONAL_STRESS]:
                return DriverState.MULTIPLE_RISK
            else:
                return DriverState.DISTRACTION_DANGER
        if event == AnalysisEvent.NORMAL_BEHAVIOR:
            if current_duration > 5.0:
                return DriverState.SAFE
        return self.current_state

    def get_current_state(self) -> DriverState:
        return self.current_state

    def get_state_duration(self) -> float:
        return time.time() - self.state_start_time

    def get_state_statistics(self) -> dict:
        if not self.state_history:
            return {}
        state_counts = {}
        for entry in self.state_history:
            state = entry["to_state"]
            state_counts[state] = state_counts.get(state, 0) + 1
        return {
            "state_counts": state_counts,
            "current_duration": self.get_state_duration(),
            "total_transitions": len(self.state_history),
        }
