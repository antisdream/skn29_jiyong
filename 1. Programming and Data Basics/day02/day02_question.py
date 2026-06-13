# 퀴즈
# 1. 리스트에서 마지막 새로운 요소를 추가할때 사용하는 메소드는?
# 1: append
my_list = [1, 2, 3, 4]
my_list.append(5)
print(my_list)

# 2. my_list = [10,20,30,40]에서 30을 꺼내기 위한 인덱스 번호는?
# 2: my_list[2] 또는 my_list[-3]
my_list = [10, 20, 30, 40]
print(my_list[2])

# 3. 딕셔너리 순서(인덱스)로 데이터를 찾나요, 아니면 이름(key)로 찾나요?
# 3: 이름(key)
info = {'name': 'AI', 'age': 30}
print(info['name'])

# 4. info = {'name':'AI'} 딕셔너리에 나이( 'age' : 25) 추가하는 코드를 작성해 보세요
info = {'name': 'AI'}
info.update({'age': 25})
print(info)

# 5. 리스트의 일부분을 잘라내는 것을 뭐라고 하는지? 그리고 사용법은?
# 5: list slicing (이상 : 미만)
my_list = [10, 20, 30, 40, 50]
print(my_list[1:4])
print(my_list[1: ])
print(my_list[-2: ])