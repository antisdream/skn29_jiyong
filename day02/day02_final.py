# 장비에서 넘어온 문자열 로그를 분석해서 의미있는 딕셔너리 리스트로 변환
log_data = [
    '2026-03-13 |MTR-1|RUN|1500',
    '2026-03-13 |MTR-2|STOP|0',
    '2026-03-13 |MTR-3|ERR|1450',
]

# 로그 리스트에서 구분자(|)를 기준으로 분리해서 딕셔너리로 조립
# log_data[0].split('|') # [2026-03-13, MTR-1, RUN, 1500 ]
logs = [
    {
        'date' : i.split('|')[0],
        'device' : i.split('|')[1],
        'status' : i.split('|')[2],
        'rpm' : i.split('|')[3]
      }
    for i in log_data
]
print(f'logs = {logs}')