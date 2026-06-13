# 코드를 간결하게 만들고, 데이터분석이나 머신러닝 전처리에 자주 쓰이는 문법들
# 튜플 과 세트

# 1. 튜플(tuple) 생성 : 절대 바뀌면 안되는 공장의 GPS 위도/경도 좌표
factory_gps = (37.565, 126.125)
print(factory_gps[0])
# factory_gps[0] = 36.5 TypeError에러 발생 (안전성 보장)

# 2. 언패킹(unpacking) : 두개의 변수에 한번에 값을 할당
lat = factory_gps[0]
lon = factory_gps[1]

lat, lon = factory_gps[0], factory_gps[1]

lat, _ = factory_gps

print(f'latitude : {lat} longitude = {lon}')

# 3 세트(set) 생성 : 센서 로그에서 중복된 에러 코드만 걸러내기
error_codes_log = [404, 500, 404, 403, 500, 404]
unique_errors = set(error_codes_log)
print(f'발생한 에러의 종류 : {unique_errors}')

# 4 교집합과 합집합 : A라인과 B라인에서 공통으로 발생하는 불량 유형 찾기
line_a_errors = {"E01", "E03", "E05"}
line_b_errors = {"E01", "E03", "E05"}
common_errors = line_a_errors & line_b_errors
print(f'공통으로 발생하는 에러 : {common_errors}')

# 5 라인 a 그리고 b에서만 발생하는 에러
unique_line_a_error = line_a_errors - line_b_errors
unique_line_b_error = line_b_errors - line_a_errors
print(f'a라인에서 발생하는 에러 : {unique_line_a_error}')
print(f'b라인에서 발생하는 에러 : {unique_line_b_error}')