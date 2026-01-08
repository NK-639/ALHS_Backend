#!/bin/bash
# Railway 빌드 전에 app/ 폴더를 현재 디렉토리로 복사하는 스크립트

# 상위 디렉토리의 app/ 폴더를 현재 디렉토리로 복사
if [ -d "../app" ]; then
    echo "📁 app/ 폴더를 복사합니다..."
    cp -r ../app .
    echo "✅ app/ 폴더 복사 완료"
else
    echo "⚠️  ../app 폴더를 찾을 수 없습니다."
    exit 1
fi
