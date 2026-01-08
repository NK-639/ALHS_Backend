-- Shaker Control Database 초기화 스크립트
-- 이 스크립트는 Docker 컨테이너 시작 시 자동으로 실행됩니다.

USE shaker_db;

-- Shaker 로그 테이블 (예시)
-- SQLAlchemy에서 자동으로 생성하므로 선택사항입니다.

-- 타임존 설정
SET time_zone = '+09:00';

-- UTF-8 인코딩 설정
ALTER DATABASE shaker_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 초기 데이터 삽입 (필요시)
-- INSERT INTO shaker_logs (mode, rpm, duration, status) VALUES ('orbital', 100, 60, 'success');

SELECT 'Database initialized successfully' AS message;
