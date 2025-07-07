import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from utils.logging import setup_logging_system
setup_logging_system()
from app import DMSApp
from core.definitions import CameraPosition
import logging
logger = logging.getLogger(__name__)

GUI_AVAILABLE = True

class DMS_GUI_Setup:
    def __init__(self, root):
        self.root = root
        self.root.title(" Enhanced DMS v18 - Research Integrated")
        self.root.geometry("500x420")
        self.config = None
        self.video_files = []
        self.is_same_driver = True
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("TRadiobutton", font=("Helvetica", 10))
        style.configure("TCheckbutton", font=("Helvetica", 10))
        style.configure("TMenubutton", font=("Helvetica", 10))
        self.source_type = tk.StringVar(value="webcam")
        self.webcam_id = tk.StringVar(value="0")
        self.user_id = tk.StringVar(value="default")
        self.enable_calibration = tk.BooleanVar(value=True)
        self.camera_position_var = tk.StringVar(value=str(CameraPosition.REARVIEW_MIRROR))
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill="both", expand=True)
        title_label = ttk.Label(main_frame, text=" Enhanced Driver Monitoring System v18", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=(0, 10))
        subtitle_label = ttk.Label(main_frame, text="연구 결과 통합: 향상된 EAR • 감정 인식 • 예측적 안전 • 운전자 식별", font=("Helvetica", 9))
        subtitle_label.pack(pady=(0, 15))
        source_frame = ttk.LabelFrame(main_frame, text="  입력 소스 선택 ", padding="10")
        source_frame.pack(fill="x", pady=5)
        ttk.Radiobutton(source_frame, text="웹캠", variable=self.source_type, value="webcam", command=self.toggle_source_widgets).pack(side="left", padx=5)
        self.webcam_id_entry = ttk.Entry(source_frame, textvariable=self.webcam_id, width=5)
        self.webcam_id_entry.pack(side="left")
        ttk.Radiobutton(source_frame, text="비디오 파일", variable=self.source_type, value="video", command=self.toggle_source_widgets).pack(side="left", padx=(20, 5))
        self.video_button = ttk.Button(source_frame, text="파일 선택...", command=self.browse_video, state="disabled")
        self.video_button.pack(side="left")
        self.video_label = ttk.Label(main_frame, text="선택된 파일 없음", wraplength=450, justify="left")
        self.video_label.pack(fill="x", pady=(0, 10))
        user_frame = ttk.LabelFrame(main_frame, text="  사용자 설정 ", padding="10")
        user_frame.pack(fill="x", pady=5)
        ttk.Label(user_frame, text="사용자 ID:").pack(side="left", padx=(0, 5))
        ttk.Entry(user_frame, textvariable=self.user_id).pack(side="left", expand=True, fill="x")
        adv_frame = ttk.LabelFrame(main_frame, text=" ⚙️ 고급 설정 ", padding="10")
        adv_frame.pack(fill="x", pady=5)
        ttk.Checkbutton(adv_frame, text="개인화 캘리브레이션 수행", variable=self.enable_calibration).pack(anchor="w")
        pos_frame = ttk.Frame(adv_frame)
        pos_frame.pack(fill="x", pady=(5, 0))
        ttk.Label(pos_frame, text="카메라 위치:").pack(side="left", padx=(0, 5))
        positions = [str(pos) for pos in CameraPosition]
        ttk.OptionMenu(pos_frame, self.camera_position_var, self.camera_position_var.get(), *positions).pack(side="left", expand=True, fill="x")
        features_frame = ttk.LabelFrame(main_frame, text=" ✨ 새로운 기능 ", padding="10")
        features_frame.pack(fill="x", pady=5)
        features_text = ("• 향상된 EAR 기반 졸음 감지 (개인화 임계값)\n" "• 52개 블렌드셰이프 감정 인식\n" "• 주의산만 객체 실시간 감지\n" "• 30초 전 위험 예측 시스템\n" "• 운전자 신원 자동 확인")
        ttk.Label(features_frame, text=features_text, font=("Helvetica", 8)).pack(anchor="w")
        start_button = ttk.Button(main_frame, text=" Enhanced DMS 시작", command=self.start_app, style="Accent.TButton")
        start_button.pack(fill="x", pady=(20, 0), ipady=8)

    def toggle_source_widgets(self):
        if self.source_type.get() == "webcam":
            self.webcam_id_entry.config(state="normal")
            self.video_button.config(state="disabled")
        else:
            self.webcam_id_entry.config(state="disabled")
            self.video_button.config(state="normal")

    def browse_video(self):
        files = filedialog.askopenfilenames(title="비디오 파일을 선택하세요 (다중 선택 가능)", filetypes=(("비디오 파일", "*.mp4 *.avi *.mov *.mkv *.wmv"), ("모든 파일", "*.* 발전")))
        if files:
            self.video_files = list(files)
            if len(self.video_files) > 1:
                self.video_label.config(text=f"{len(self.video_files)}개 파일 선택됨: {os.path.basename(self.video_files[0])} 등")
                self.is_same_driver = messagebox.askyesno("운전자 확인", f"{len(self.video_files)}개의 비디오를 선택했습니다.\n모두 같은 운전자의 영상입니까?\n\n('예' 선택 시, 개인화 설정을 공유합니다.)")
            else:
                self.video_label.config(text=f"선택됨: {os.path.basename(self.video_files[0])}")
        else:
            self.video_files = []
            self.video_label.config(text="선택된 파일 없음")

    def start_app(self):
        input_source = None
        if self.source_type.get() == "webcam":
            cam_id_str = self.webcam_id.get()
            if cam_id_str.isdigit():
                input_source = int(cam_id_str)
            else:
                messagebox.showerror("입력 오류", "웹캠 번호는 숫자여야 합니다.")
                return
        else:
            if not self.video_files:
                messagebox.showerror("입력 오류", "비디오 파일을 선택해주세요.")
                return
            input_source = self.video_files if len(self.video_files) > 1 else self.video_files[0]
        user_id = self.user_id.get().strip() or "default"
        selected_pos_str = self.camera_position_var.get()
        camera_position = next((pos for pos in CameraPosition if str(pos) == selected_pos_str), CameraPosition.REARVIEW_MIRROR)
        self.config = {
            "input_source": input_source,
            "user_id": user_id,
            "camera_position": camera_position,
            "enable_calibration": self.enable_calibration.get(),
            "is_same_driver": self.is_same_driver,
        }
        self.root.destroy()

def get_user_input_terminal():
    print("\n" + "=" * 70)
    print(" Enhanced DMS v18 - Research Integrated (터미널 모드)")
    print("=" * 70)
    input_source, is_same_driver = None, True
    while input_source is None:
        choice = input("\n 입력 소스 선택 (1: 웹캠, 2: 비디오 파일): ").strip()
        if choice == "1":
            cam_id = input(" 웹캠 번호 입력 (기본값 0): ").strip()
            input_source = int(cam_id) if cam_id.isdigit() else 0
        elif choice == "2":
            path = input(" 비디오 파일 경로 입력 (여러 파일은 쉼표로 구분): ").strip()
            paths = [p.strip() for p in path.split(",")]
            valid_paths = [p for p in paths if os.path.exists(p)]
            if not valid_paths:
                print("❌ 유효한 파일을 찾을 수 없습니다.")
                continue
            input_source = valid_paths if len(valid_paths) > 1 else valid_paths[0]
            if len(valid_paths) > 1:
                same_driver_choice = input("같은 운전자입니까? (y/n, 기본값 y): ").strip().lower()
                is_same_driver = same_driver_choice != "n"
    user_id = input("\n 사용자 ID 입력 (기본값 default): ").strip() or "default"
    calib_choice = input("\n 개인화 캘리브레이션 수행? (y/n, 기본값 y): ").strip().lower()
    enable_calibration = calib_choice != "n"
    print("\n 카메라 위치 선택:")
    positions = list(CameraPosition)
    for i, pos in enumerate(positions, 1):
        print(f"{i}. {pos.value}")
    pos_choice = input(f"선택 (1-{len(positions)}, 기본값 1): ").strip()
    camera_position = positions[int(pos_choice) - 1] if pos_choice.isdigit() and 0 < int(pos_choice) <= len(positions) else positions[0]
    return input_source, user_id, camera_position, enable_calibration, is_same_driver

def main():
    config = None
    try:
        if GUI_AVAILABLE:
            root = tk.Tk()
            try:
                root.tk.call("source", "azure.tcl")
                root.tk.call("set_theme", "light")
            except tk.TclError:
                pass
            gui_setup = DMS_GUI_Setup(root)
            root.mainloop()
            config = gui_setup.config
        else:
            input_source, user_id, camera_position, enable_calibration, is_same_driver = get_user_input_terminal()
            config = {
                "input_source": input_source,
                "user_id": user_id,
                "camera_position": camera_position,
                "enable_calibration": enable_calibration,
                "is_same_driver": is_same_driver,
            }
        if config:
            logger.info(f"설정 완료: {config}")
            print("\n" + "=" * 60 + f"\n DMS 시스템 시작... (사용자: {config['user_id']})\n" + "=" * 60)
            app = DMSApp(**config)
            app.run()
        else:
            print("\n 설정이 취소되어 프로그램을 종료합니다.")
    except (KeyboardInterrupt, EOFError):
        print("\n\n 프로그램을 종료합니다.")
    except Exception as e:
        logger.error(f"시스템 실행 실패: {e}", exc_info=True)
        if GUI_AVAILABLE:
            messagebox.showerror("치명적 오류", f"시스템 실행 중 심각한 오류가 발생했습니다.\n로그 파일을 확인해주세요.\n\n오류: {e}")
        else:
            print("\n❌ 시스템 실행 중 심각한 오류가 발생했습니다. 로그 파일을 확인해주세요.")

if __name__ == "__main__":
    model_files = ["models/face_landmarker.task", "models/pose_landmarker_full.task", "models/hand_landmarker.task", "models/efficientdet_lite0.tflite"]
    missing_files = [f for f in model_files if not os.path.exists(f)]
    if missing_files:
        error_msg = "다음 모델 파일이 없어 프로그램을 시작할 수 없습니다:\n" + "\n".join(missing_files)
        logger.critical(error_msg)
        if GUI_AVAILABLE:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("모델 파일 오류", error_msg)
        else:
            print(f"\n❌ ERROR: {error_msg}")
    else:
        main()