# 리스트와 딕셔너리(데이터 그룹화)
# 데이터가 많을 떄 사용하는 자료구조
# 스마트팩토리의 생산라인 데이터나 시계열 센서데이터를 다룰때 필수
# 1. 리스트생성 : 특정 공정의 최근 5분간 온도 기록
temp_logs = [24.5, 25.1, 24.8, 26.0, 25.5]

# 2. 리스트의 요소 접근 및 수정(가장 오래된 데이터 수정)
temp_logs[0] = 24.6

# 3. 딕셔너리 : 특정 모터의 설정값 관리(키-값 쌍)
motor_config = {"id" : 'MTR-A1', 'rpm': 1500, 'status': 'Running'}

# 1. 온도중에 가장 최근 3개의 데이터만 추출
print(temp_logs[-3:])
# 2. 모터의 설정값중에 status의 상태를 출력
print(motor_config['status'])
# 3. 온도데이터에 추가 최신데이터인 25.9를 추가해서 전체 출력
temp_logs.append(25.9)
print(temp_logs)
# 4. 특정 모터의 설정값에 새로운 "temperature" 45.2, "rpm" 값을 1600 수정해서 전체 출력 
motor_config['temperature'] = 45.2
motor_config['rpm'] = 1600
print(motor_config)

# 1. 온도중에 가장 최근 3개의 데이터만 추출
print(f'가장 최신데이터(top3) : { temp_logs[-3 : ] }')
# 2. 모터의 설정값중에 status의 상태를 출력
print( f"모터의 상태 : {motor_config['status']}" )
# 3. 온도데이터에 추가 최신데이터인 25.9를 추가해서 전체 출력
temp_logs.append(25.9)
print( f'온도데이터 : {temp_logs}')
# 4. 특정 모터의 설정값에 새로운 "temperature" 45.2, "rpm" 값을 1600 수정해서 전체 출력 
motor_config['temperature'] = 45.2
motor_config['rpm'] = 1600
print(f'모터의 환경변수 값들 : {motor_config}')