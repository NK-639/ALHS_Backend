"""Shaker 서비스"""
import numpy as np
from typing import Tuple

from app.config import get_logger

logger = get_logger(__name__)

# 쉐이커 상수
ORBITAL_RADIUS_MM = 5.0
CENTER_X = 150.0
CENTER_Y = 150.0
CENTER_Z = 10.0

# Vial 좌표 상수
VIAL_COORDINATES = {
    "vial_1": {"x": 100, "y": 150, "z": 0},
    "vial_2": {"x": 150, "y": 100, "z": 0},
}
DEFAULT_FEEDRATE = 3000

# 3D 모드 고정 파라미터
FIXED_ORBITAL_RADIUS_3D = 10.0
FIXED_AMPLITUDE_Z_3D = 5.0

# Klipper Z축 최대 속도
MAX_Z_FEEDRATE_MM_MIN = 900.0


class ShakerService:
    """Shaker G-code 생성 서비스"""

    @staticmethod
    def generate_orbital_gcode(rpm: int, time_sec: float, center_x: float = None, center_y: float = None) -> str:
        """ORBITAL 모드 G-code 시퀀스 생성

        - center_x, center_y: vial 좌표 (없으면 기본값 사용)
        """
        amplitude_mm = ORBITAL_RADIUS_MM
        center_x = center_x if center_x is not None else CENTER_X
        center_y = center_y if center_y is not None else CENTER_Y

        rps = rpm / 60.0
        omega = rps * 2 * np.pi
        calculated_speed_f = (2 * np.pi * amplitude_mm * rps) * 60
        speed_f = max(2000, calculated_speed_f)
        
        # 명령 수 최적화: time_sec가 길어질수록 steps_per_sec를 줄여서 지연 최소화
        # 짧은 시간(1-5초): 50 steps/sec (부드러운 궤도)
        # 중간 시간(5-10초): 30 steps/sec
        # 긴 시간(10초 이상): 20 steps/sec
        if time_sec <= 5:
            steps_per_sec = 50
        elif time_sec <= 10:
            steps_per_sec = 30
        else:
            steps_per_sec = 20
        
        num_steps = int(time_sec * steps_per_sec) + 1  # time_sec까지 포함하기 위해 +1
        time_points = np.linspace(0, time_sec, num_steps, endpoint=True)  # endpoint=True로 정확히 time_sec까지 포함

        gcode_commands = []
        gcode_commands.append("G21 ; 단위를 mm로 설정")
        gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} F6000 ; 중심 좌표로 이동")

        # time_sec 동안 정확히 궤도 동작 수행
        # 명령을 효율적으로 생성하여 지연 최소화
        for t in time_points:
            x = amplitude_mm * np.cos(omega * t) + center_x
            y = amplitude_mm * np.sin(omega * t) + center_y
            gcode_commands.append(f"G1 X{x:.4f} Y{y:.4f} F{int(speed_f)}")
        
        # 궤도 동작 완료 후 모든 이동 완료 대기
        gcode_commands.append("M400 ; 궤도 동작 완료 대기")

        logger.info("=" * 50)
        logger.info("[ORBITAL G-code 생성 파라미터]")
        logger.info(f"  RPM: {rpm}")
        logger.info(f"  시간(초): {time_sec}")
        logger.info(f"  RPS: {rps:.4f}")
        logger.info(f"  Omega: {omega:.4f}")
        logger.info(f"  중심 좌표: X={center_x}, Y={center_y}")
        logger.info(f"  진폭(반경): {amplitude_mm} mm")
        logger.info(f"  속도(F): {int(speed_f)}")
        logger.info(f"  스텝 수: {num_steps}")
        logger.info("=" * 50)
        logger.info("[생성된 G-code]")
        for cmd in gcode_commands:
            logger.info(cmd)
        logger.info("=" * 50)

        return "\n".join(gcode_commands)

    @staticmethod
    def generate_linear_gcode(rpm: int, time_sec: float) -> str:
        """LINEAR 모드 G-code 시퀀스 생성"""
        center_x = CENTER_X
        center_y = CENTER_Y
        amplitude_y = 25.0

        rps = rpm / 60.0
        omega = rps * 2 * np.pi
        calculated_speed_f = (4 * amplitude_y * rps) * 60
        speed_f = max(2000, calculated_speed_f)

        steps_per_sec = 50
        num_steps = int(time_sec * steps_per_sec)
        time_points = np.linspace(0, time_sec, num_steps, endpoint=False)

        gcode_commands = []
        gcode_commands.append("G21 ; 단위를 mm로 설정")
        gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} F6000 ; 중심 좌표로 이동")

        for t in time_points:
            y = amplitude_y * np.sin(omega * t) + center_y
            x = center_x
            gcode_commands.append(f"G1 X{x:.4f} Y{y:.4f} F{int(speed_f)}")

        gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} F6000 ; 중심 좌표로 복귀")
        gcode_commands.append("M400 ; 모든 이동이 완료될 때까지 기다립니다.")
        gcode_commands.append(f"G92 X{center_x:.4f} Y{center_y:.4f} ; 현재 위치를 중심 좌표로 재설정")

        logger.info("=" * 50)
        logger.info("[LINEAR G-code 생성 파라미터]")
        logger.info(f"  RPM: {rpm}")
        logger.info(f"  시간(초): {time_sec}")
        logger.info(f"  RPS: {rps:.4f}")
        logger.info(f"  Omega: {omega:.4f}")
        logger.info(f"  중심 좌표: X={center_x}, Y={center_y}")
        logger.info(f"  Y축 진폭: {amplitude_y} mm")
        logger.info(f"  속도(F): {int(speed_f)}")
        logger.info(f"  스텝 수: {num_steps}")
        logger.info("=" * 50)
        logger.info("[생성된 G-code]")
        for cmd in gcode_commands:
            logger.info(cmd)
        logger.info("=" * 50)

        return "\n".join(gcode_commands)

    @staticmethod
    def generate_3d_gcode(rpm: int, time_sec: float) -> str:
        """3D (헬리컬 와블링) 모드 G-code 시퀀스 생성"""
        center_x = CENTER_X
        center_y = CENTER_Y
        center_z = CENTER_Z
        amplitude_xy = FIXED_ORBITAL_RADIUS_3D
        amplitude_z = FIXED_AMPLITUDE_Z_3D
        amplitude_z_half = amplitude_z / 2.0

        rps = rpm / 60.0
        omega = rps * 2 * np.pi
        calculated_speed_xy = (2 * np.pi * amplitude_xy * rps) * 60
        final_feedrate = min(calculated_speed_xy, MAX_Z_FEEDRATE_MM_MIN)
        final_feedrate = max(2000, final_feedrate)

        steps_per_sec = 50
        num_steps = int(time_sec * steps_per_sec)
        time_points = np.linspace(0, time_sec, num_steps, endpoint=False)

        gcode_commands = []
        gcode_commands.append("G21 ; 단위를 mm로 설정")
        gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} Z{center_z:.4f} F6000 ; 중심 좌표로 이동")

        for t in time_points:
            x = amplitude_xy * np.cos(omega * t) + center_x
            y = amplitude_xy * np.sin(omega * t) + center_y
            z = amplitude_z_half * np.sin(omega * t) + center_z
            gcode_commands.append(f"G1 X{x:.4f} Y{y:.4f} Z{z:.4f} F{int(final_feedrate)}")

        gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} Z{center_z:.4f} F6000 ; 중심 좌표로 복귀")
        gcode_commands.append("M400 ; 모든 이동이 완료될 때까지 기다립니다.")
        gcode_commands.append(f"G92 X{center_x:.4f} Y{center_y:.4f} Z{center_z:.4f} ; 현재 위치를 중심 좌표로 재설정")

        return "\n".join(gcode_commands)

    @staticmethod
    def get_orbital_parameters() -> dict:
        """Orbital 모드 파라미터 반환"""
        return {
            "fixed_radius_mm": ORBITAL_RADIUS_MM,
            "center_xy": (CENTER_X, CENTER_Y)
        }

    @staticmethod
    def get_3d_parameters() -> dict:
        """3D 모드 파라미터 반환"""
        return {
            "orbital_radius_mm": FIXED_ORBITAL_RADIUS_3D,
            "amplitude_z_mm": FIXED_AMPLITUDE_Z_3D,
            "center_xyz": (CENTER_X, CENTER_Y, CENTER_Z)
        }

    @staticmethod
    def generate_move_gcode(target: str, feedrate: int = DEFAULT_FEEDRATE) -> str:
        """
        Vial 타겟 위치로 이동하는 G-code 생성

        - target: vial_1 또는 vial_2
        - z가 0이면 Z축 명령 생략
        """
        coords = VIAL_COORDINATES.get(target)
        if not coords:
            raise ValueError(f"알 수 없는 타겟: {target}")

        x = coords["x"]
        y = coords["y"]
        z = coords["z"]

        # z가 0이면 Z축 생략
        if z == 0:
            gcode = f"G1 X{x} Y{y} F{feedrate}"
        else:
            gcode = f"G1 X{x} Y{y} Z{z} F{feedrate}"

        logger.info(f"[이동 G-code 생성] target={target}, gcode={gcode}")
        return gcode

    @staticmethod
    def get_vial_coordinates(target: str) -> dict:
        """Vial 좌표 반환"""
        coords = VIAL_COORDINATES.get(target)
        if not coords:
            raise ValueError(f"알 수 없는 타겟: {target}")
        return coords

    @staticmethod
    def generate_home_gcode(home_x: float = CENTER_X, home_y: float = CENTER_Y, feedrate: int = 6000) -> str:
        """
        원점으로 복귀하는 G-code 생성

        - home_x, home_y: 원점 좌표 (기본값: 150, 150)
        - feedrate: 이동 속도
        """
        gcode_commands = []
        gcode_commands.append(f"G0 X{home_x:.4f} Y{home_y:.4f} F{feedrate} ; 원점으로 복귀")
        gcode_commands.append("M400 ; 모든 이동이 완료될 때까지 기다립니다.")
        
        logger.info(f"[원점 복귀 G-code 생성] 원점=({home_x}, {home_y})")
        return "\n".join(gcode_commands)