# 결측치가 포함된 데이터의 전처리
# 결측치 NA 데이터수집이 안되어 있거나 잘못된 값일때 ex) 센서데이터를 추출하는데. 실패하거나 오류로 인해서 잘못된 값
# 스마트팩토리에서 센서에서 수집된 데이터 원본(중간에 에러코드 -999 포함)
raw_sensor_data = {
    'device' : 'Presure_Sensor_01',
    "values" : [10.2, 10.5, -999, 10.8, 11.1, -999, 15.5]
}
# 에러코드가 몇개 있는지 확인하고 제거
# 에러코드 개수 확인
error_count = raw_sensor_data["values"].count(-999)
print(f'통신에러 갯수 : {error_count}')

for i in range(error_count) :
    raw_sensor_data["values"].remove(-999)

print('오류제거된 values : {raw_sensor_data["values"]}')

raw_sensor_data["values"].remove(-999)
raw_sensor_data["values"].remove(-999)

error_count = raw_sensor_data["values"].count(-999)
if error_count > 0 :
    raw_sensor_data["values"].remove(-999)