# 리스트 내포(list comprehension) : 반복문을 한줄로 압축
# 1부터 5개의 숫자를 가진 아이디 만들기 ID-1 ID-2... range(5) 01234 range(1,6) 1,2,3,4,5

sensor_ids = [ 'ID-'+str(i) for i in range(1,6) ]
print(f'아이디 집합 : {sensor_ids}')

# 기존의 리스트의 데이터 일괄 변환(단위변환 섭씨 -> 화씨)
celsius = [0, 10, 20, 30]
converted_celsius = [ (i*9/5)+32 for i in celsius ]
print(converted_celsius)

# 센서이름을 키로 기본값으로 0.0을 하는 초기화 딕셔너리
sensors = ['Temp', 'Humid', 'Vibration']
sensor_init_status = { i:0.0 for i in sensors }
print(sensor_init_status)