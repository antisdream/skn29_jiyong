# 자료구조의 중첩과 메소드 활용
# 리스트 안의 딕셔너리(복잡한 형태의 json을 모방)
factory_lines = [
    {"line":"A", 'defects':2, "active":True },
    {"line":"B", 'defects':0, "active":True },
]
# B라인을 중지.. active 속성을 False로 변경
factory_lines[1]['active'] = False

motor_config = {"id": "MTR-001", 'rpm': 1500, 'status': 'Running'}

# 딕셔너리에서 키(keys) 와 값(values)만 분리해서 리스트로 저장 하고 리스트별로 출력
config_keys = list(motor_config.keys())
config_values = list(motor_config.values())
print(f"keys = {config_keys}")
print(f"values = {config_values}")

# 정렬
temp_logs = [24.5, 25.1, 24.8, 26.0, 25.5] # 온도데이터
# 온도가 높은순으로 정렬, 위험군을 먼저 파악 (정렬할 때 기본은 오름차순)
temp_logs.sort(reverse=True)
print(f'온도를 높은순으로 정렬 : {temp_logs}')

# ascending : 오름차순 / 내림차순 : descending