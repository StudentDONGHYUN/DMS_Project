import cv2
import threading
import time
import os
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class MultiVideoCalibrationManager:
    """다중 비디오 캘리브레이션 관리"""

    def __init__(self, user_id: str):
        self.is_same_driver = True
        self.shared_calibration_data = None

    def set_driver_continuity(self, is_same: bool):
        self.is_same_driver = is_same
        logger.info(f"운전자 연속성 설정됨: {'동일 운전자' if is_same else '다른 운전자'}")

    def should_skip_calibration(self) -> bool:
        return self.is_same_driver and self.shared_calibration_data is not None

    def save_calibration_data(self, data: Dict):
        if self.is_same_driver:
            self.shared_calibration_data = data.copy()

    def get_shared_calibration_data(self) -> Optional[Dict]:
        return self.shared_calibration_data

class VideoInputManager:
    """비동기 입력 관리자"""

    def __init__(self, input_source):
        self.input_source = input_source
        self.cap = None
        self.is_video_mode = isinstance(input_source, (str, list, tuple))
        self.video_playlist = []
        self.current_video_index = -1
        self.playback_speed = 1.0
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        self.stopped = True
        self.video_changed_flag = False

    def initialize(self) -> bool:
        try:
            if self.is_video_mode:
                self.video_playlist = self.input_source if isinstance(self.input_source, list) else [self.input_source]
                if not self.video_playlist:
                    return False
                self.current_video_index = 0
                self.cap = cv2.VideoCapture(self.video_playlist[0])
            else:
                self.cap = cv2.VideoCapture(int(self.input_source))
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if not self.cap or not self.cap.isOpened():
                logger.error(f"입력 소스 열기 실패: {self.input_source}")
                return False
            self.stopped = False
            self.capture_thread = threading.Thread(target=self._reader_thread, daemon=True)
            self.capture_thread.start()
            logger.info("✅ 입력 소스 초기화 및 스레드 시작")
            return True
        except Exception as e:
            logger.error(f"VideoInputManager 초기화 실패: {e}", exc_info=True)
            return False

    def _reader_thread(self):
        while not self.stopped:
            if not self.cap or not self.cap.isOpened():
                self.stopped = True
                break
            ret, frame = self.cap.read()
            if not ret:
                if self.is_video_mode and self._try_next_video():
                    continue
                else:
                    self.stopped = True
                    break
            if not self.is_video_mode:
                frame = cv2.flip(frame, 1)
            with self.frame_lock:
                self.current_frame = frame
            if self.is_video_mode:
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                sleep_duration = 1.0 / (fps * self.playback_speed) if fps > 0 and self.playback_speed > 0 else 1 / 30
                time.sleep(sleep_duration)

    def _try_next_video(self):
        if self.current_video_index >= len(self.video_playlist) - 1:
            return False
        self.current_video_index += 1
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.video_playlist[self.current_video_index])
        if self.cap.isOpened():
            logger.info(f"다음 비디오 로드: {os.path.basename(self.video_playlist[self.current_video_index])}")
            self.video_changed_flag = True
            return True
        return False

    def get_frame(self):
        with self.frame_lock:
            return self.current_frame

    def has_video_changed(self):
        if self.video_changed_flag:
            self.video_changed_flag = False
            return True
        return False

    def set_playback_speed(self, speed: float):
        self.playback_speed = max(0.1, speed)

    def get_playback_info(self):
        info = {"mode": "video" if self.is_video_mode else "webcam"}
        if self.is_video_mode and self.video_playlist:
            info.update({
                "current_file": os.path.basename(self.video_playlist[self.current_video_index]),
                "total_videos": len(self.video_playlist),
                "current_video": self.current_video_index + 1,
            })
        return info

    def is_running(self):
        return not self.stopped

    def release(self):
        self.stopped = True
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1)
        if self.cap:
            self.cap.release()
        logger.info("VideoInputManager 리소스 해제 완료.")
