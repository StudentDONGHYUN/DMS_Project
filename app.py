# app.py

import cv2
import time
import asyncio
from pathlib import Path
from datetime import datetime
import logging

# core 모듈
from core.definitions import CameraPosition
from core.state_manager import EnhancedStateManager

# analysis 모듈
from analysis.engine import EnhancedAnalysisEngine

# systems 모듈
from systems.mediapipe_manager import EnhancedMediaPipeManager
from systems.performance import PerformanceOptimizer

# io_handler 모듈
# 여기서 MultiVideoCalibrationManager를 함께 import 해야 합니다.
from io_handler.video_input import VideoInputManager, MultiVideoCalibrationManager

# utils 모듈
logger = logging.getLogger(__name__)


class DMSApp:
    """향상된 메인 애플리케이션"""

    def __init__(
        self,
        input_source=0,
        user_id: str = "default",
        camera_position: CameraPosition = CameraPosition.REARVIEW_MIRROR,
        enable_calibration: bool = True,
        is_same_driver: bool = True,
    ):
        self.input_source = input_source
        self.user_id = user_id
        self.camera_position = camera_position
        self.enable_calibration = enable_calibration
        self.is_same_driver = is_same_driver
        self.running = False
        self.paused = False
        self.current_processed_frame = None

        self.performance_monitor = PerformanceOptimizer()
        
        # MultiVideoCalibrationManager 클래스는 video_input.py에서 가져옵니다.
        self.calibration_manager = MultiVideoCalibrationManager(user_id)
        if isinstance(input_source, (list, tuple)) and len(input_source) > 1:
            self.calibration_manager.set_driver_continuity(self.is_same_driver)

    def initialize(self) -> bool:
        """향상된 초기화"""
        try:
            self.state_manager = EnhancedStateManager()
            self.analysis_engine = EnhancedAnalysisEngine(
                self.state_manager,
                self.user_id,
                self.camera_position,
                self.calibration_manager,
                self.enable_calibration,
            )
            self.mediapipe_manager = EnhancedMediaPipeManager(self.analysis_engine)
            self.video_input_manager = VideoInputManager(self.input_source)

            if not self.video_input_manager.initialize():
                raise RuntimeError("입력 소스 초기화 실패")

            logger.info("🚀 고도화된 DMS 시스템 v18 (연구 결과 통합) 초기화 완료")
            logger.info(
                "📊 새로운 기능: 향상된 EAR, 감정 인식, 예측적 안전, 운전자 식별"
            )
            return True

        except Exception as e:
            logger.error(f"초기화 실패: {e}", exc_info=True)
            return False

    async def main_async_loop(self):
        last_displayed_frame = None
        try:
            while self.running:
                queue_processed_this_loop = False

                if not self.video_input_manager.is_running() and not self.analysis_engine.processed_data_queue:
                    logger.info("모든 비디오 재생 완료 또는 입력 종료")
                    break

                if self.paused:
                    if last_displayed_frame is not None:
                        cv2.imshow("Enhanced DMS v18", last_displayed_frame)
                    if not self._handle_keyboard_input(cv2.waitKey(30)):
                        break
                    continue

                if self.video_input_manager.is_running():
                    original_frame = self.video_input_manager.get_frame()
                    if original_frame is not None:
                        self.mediapipe_manager.run_tasks(original_frame.copy())
                        if last_displayed_frame is None:
                            last_displayed_frame = original_frame

                if self.analysis_engine.processed_data_queue and not queue_processed_this_loop:
                    analysis_start_time = time.time()
                    frame, results = self.analysis_engine.processed_data_queue.popleft()
                    playback_info = self.video_input_manager.get_playback_info()
                    health = self.mediapipe_manager.get_system_health()
                    perf_stats = {
                        "fps": self.mediapipe_manager.current_fps,
                        "system_health": health.get("overall_health", 1.0),
                        "performance_status": health.get("performance_status", {}),
                    }
                    annotated_frame = await self.analysis_engine.process_and_annotate_frame(
                        frame, results, perf_stats, playback_info
                    )
                    last_displayed_frame = annotated_frame
                    self.current_processed_frame = annotated_frame
                    actual_processing_time = (time.time() - analysis_start_time) * 1000
                    self.performance_monitor.log_performance(actual_processing_time, perf_stats["fps"])
                    queue_processed_this_loop = True

                if last_displayed_frame is not None:
                    cv2.imshow(
                        "Enhanced DMS v18 - Research Integrated", last_displayed_frame
                    )

                if not self._handle_keyboard_input(cv2.waitKey(1)):
                    break
        except KeyboardInterrupt:
            logger.info("사용자 중단")
        except Exception as e:
            logger.error(f"실행 중 오류 발생: {e}", exc_info=True)
        finally:
            self.performance_monitor.save_session_summary()
            self._cleanup()

    def run(self):
        """비동기 루프를 시작하고 실행하는 동기 진입점 함수."""
        if not self.initialize():
            return
        self.running = True
        logger.info(
            "🎯 DMS v18 시스템 시작. 'q'를 눌러 종료, 스페이스바로 일시정지, 's'로 스크린샷 저장"
        )
        asyncio.run(self.main_async_loop())

    def _handle_keyboard_input(self, key: int) -> bool:
        """향상된 키보드 입력 처리"""
        key &= 0xFF

        if key == ord("q") or key == 27:
            return False
        elif key == ord(" "):
            self.paused = not self.paused
            logger.info(f"{'일시정지' if self.paused else '재생 재개'}")
        elif key == ord("s") and self.current_processed_frame is not None:
            filename = f"captures/enhanced_dms_v18_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            Path("captures").mkdir(exist_ok=True)
            cv2.imwrite(filename, self.current_processed_frame)
            logger.info(f"프레임 저장됨: {filename}")
        elif key == ord("r"):
            self.performance_monitor = PerformanceOptimizer()
            logger.info("성능 통계 리셋됨")
        elif key == ord("i"):
            metrics = self.analysis_engine.get_latest_metrics()
            logger.info(
                f"현재 상태 - 피로도: {metrics.fatigue_risk_score:.2f}, "
                f"주의산만: {metrics.distraction_risk_score:.2f}, "
                f"감정: {metrics.emotion_state.value}, "
                f"예측 위험: {metrics.predictive_risk_score:.2f}"
            )
        return True

    def _cleanup(self):
        """향상된 정리"""
        logger.info("Enhanced DMS v18 시스템 정리 중...")
        self.running = False

        if hasattr(self, "mediapipe_manager"):
            self.mediapipe_manager.close()
        if hasattr(self, "analysis_engine"):
            self.analysis_engine.personalization.save_profile()
            if hasattr(self.analysis_engine, "driver_identifier"):
                self.analysis_engine.driver_identifier._save_driver_profiles()
        if hasattr(self, "video_input_manager"):
            self.video_input_manager.release()

        cv2.destroyAllWindows()

        if hasattr(self, "performance_monitor"):
            final_status = self.performance_monitor.get_optimization_status()
            logger.info(
                f"최종 성능 요약 - 평균 FPS: {final_status.get('avg_fps', 0):.1f}, "
                f"성능 점수: {final_status.get('performance_score', 0):.1%}"
            )

        logger.info("Enhanced DMS v18 시스템 정리 완료")