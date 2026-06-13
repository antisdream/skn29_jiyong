import day3_mycalc as mycalc

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("숫자를 입력하세요.")

def main():
    print("간단한 계산기 (종료: q)")
    while True:
        op = input("연산자 입력 (+, -, *, /) 또는 q로 종료: ").strip()
        if op.lower() == 'q':
            break
        if op not in ('+', '-', '*', '/'):
            print("유효한 연산자를 입력하세요.")
            continue

        a = get_number("첫 번째 숫자: ")
        b = get_number("두 번째 숫자: ")

        try:
            if op == '+':
                result = mycalc.add(a, b)
            elif op == '-':
                result = mycalc.sub(a, b)
            elif op == '*':
                result = mycalc.mul(a, b)
            elif op == '/':
                result = mycalc.div(a, b)
            print(f"결과: {result}")
        except ZeroDivisionError as e:
            print(e)

if __name__ == "__main__":
    main()