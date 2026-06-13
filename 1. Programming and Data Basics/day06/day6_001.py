# 현재 디렉터리 확인
import os
import sys

# 현재 작업 디렉토리를 확인하는 기능
print(f'현재 작업디렉터리 : {os.getcwd()}')

# Pyhton 파일의 위치 확인
print(f'파일위치 확인 : {os.path.abspath(__file__)}')

print(f'__file__ : {__file__}')
