# 1. 3명의 사원정보를 리스트에 저장해서 변수로 관리
employees = [
    {"name" : "홍길동", "pay" : 100000, "status" : "관리자" },
    {"name" : "고길동", "pay" : 200000, "status" : "부서장" },
    {"name" : "저길동", "pay" : 50000, "status" : "평사원"},
]

# 2. pay가 가장 큰 사원 이름을 출력
max_pay = 0
highest_paid_employee_name = ""

for employee in employees:
  if employee["pay"] > max_pay:
     max_pay = employee["pay"]
     highest_paid_employee_name = employee["name"]

print(f"pay가 가장 큰 사원은 {highest_paid_employee_name}입니다")

# 3. 임의 집합 두개를 만들어서 교집합 합집합 차집합 각 집합중에 가장큰값과 작은값을 찾아서 출력
# import random
# a = [random.randint(1,15) for i in range(10)]
# b = [random.randint(1,15) for i in range(10)]


