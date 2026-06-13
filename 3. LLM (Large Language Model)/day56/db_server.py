import sqlite3
import json
import random
from fastmcp import FastMCP

mcp = FastMCP(name='DbServer')

DB_FILE = 'C:\\python-src\\Daily\\day56\\teacher\\sample.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # 기존 테이블 삭제 후 새 스키마로 재생성
    cursor.execute('DROP TABLE IF EXISTS emp')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emp (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            department TEXT    NOT NULL,
            position   TEXT    NOT NULL,
            salary     INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@mcp.tool
def insert_emp(name: str, department: str, position: str, salary: int) -> str:
    """emp 테이블에 직원 1건을 삽입합니다."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO emp (name, department, position, salary) VALUES (?, ?, ?, ?)",
        (name, department, position, salary)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return f"삽입 완료: id={new_id}, name={name}, dept={department}, pos={position}, salary={salary}"

@mcp.tool
def insert_emp_bulk(records: list) -> str:
    """emp 테이블에 여러 직원을 한 번에 삽입합니다. records는 (name, department, position, salary) 튜플 리스트입니다."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO emp (name, department, position, salary) VALUES (?, ?, ?, ?)",
        records
    )
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return f"{count}건 삽입 완료"

@mcp.tool
def get_database_schema() -> str:
    """데이터베이스의 테이블 스키마를 반환합니다."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schemas = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return "\n\n".join(schemas)

def seed_data():
    """가상 직원 데이터 100건을 emp 테이블에 삽입합니다."""
    first_names = [
        "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
        "한", "오", "서", "신", "권", "황", "안", "송", "류", "전"
    ]
    last_names = [
        "민준", "서연", "도윤", "서현", "지호", "지민", "준서", "수아",
        "예준", "소율", "현우", "지유", "건우", "채원", "우진", "수빈",
        "선우", "하은", "민재", "지안", "시우", "나은", "준혁", "다은",
        "지훈", "예린", "승민", "혜원", "태양", "보람"
    ]
    departments = ["개발팀", "기획팀", "마케팅팀", "영업팀", "인사팀", "재무팀", "디자인팀", "운영팀"]
    # 직급별 연봉 범위 (만원)
    position_salary = {
        "인턴":   (2400,  3000),
        "사원":   (3000,  4000),
        "대리":   (4000,  5000),
        "과장":   (5000,  6500),
        "차장":   (6500,  8000),
        "부장":   (8000, 10000),
        "이사":  (10000, 15000),
    }

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM emp")
    if cursor.fetchone()[0] > 0:
        print("이미 데이터가 있습니다. seed_data() 건너뜀.")
        conn.close()
        return

    records = []
    for _ in range(100):
        name       = random.choice(first_names) + random.choice(last_names)
        department = random.choice(departments)
        position   = random.choice(list(position_salary.keys()))
        sal_min, sal_max = position_salary[position]
        salary     = random.randrange(sal_min, sal_max, 100)  # 100만원 단위
        records.append((name, department, position, salary))

    cursor.executemany(
        "INSERT INTO emp (name, department, position, salary) VALUES (?, ?, ?, ?)",
        records
    )
    conn.commit()
    print(f"가상 데이터 {cursor.rowcount}건 삽입 완료")
    conn.close()

@mcp.tool()
def execute_sql_query(query:str)->str:
    '''sqlite 데이터베이스에 select sql 쿼리를 실행하고 결과를 json 형태로 반환
    주의 : 안전한 실행을 위해서 반드시 select 쿼리만 허용됩니다.
    '''
    # SELECT 쿼리만 허용
    if not query.strip().upper().startswith('SELECT'):
        return json.dumps({"error": "SELECT 쿼리만 허용됩니다."}, ensure_ascii=False)

    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # 컬럼명을 키로 사용
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        # Row 객체를 dict 리스트로 변환
        result = [dict(row) for row in rows]
        return json.dumps(result, ensure_ascii=False, indent=2)

    except sqlite3.Error as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool
def get_all_emp() -> str:
    """전체 직원 목록을 반환합니다."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emp ORDER BY id")
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool
def get_emp_by_department(department: str) -> str:
    """특정 부서의 직원 목록을 반환합니다. (ex: 개발팀, 인사팀)"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emp WHERE department = ? ORDER BY id", (department,))
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool
def get_emp_by_position(position: str) -> str:
    """특정 직급의 직원 목록을 반환합니다. (ex: 사원, 대리, 과장)"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emp WHERE position = ? ORDER BY id", (position,))
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool
def get_emp_by_salary_range(min_salary: int, max_salary: int) -> str:
    """연봉 범위(만원)로 직원을 조회합니다. (ex: min_salary=4000, max_salary=6000)"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM emp WHERE salary BETWEEN ? AND ? ORDER BY salary DESC",
        (min_salary, max_salary)
    )
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool
def get_emp_stats() -> str:
    """부서별 직원 수, 평균연봉, 최대연봉, 최소연봉 통계를 반환합니다."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            department,
            COUNT(*)        AS emp_count,
            ROUND(AVG(salary), 0) AS avg_salary,
            MAX(salary)     AS max_salary,
            MIN(salary)     AS min_salary
        FROM emp
        GROUP BY department
        ORDER BY avg_salary DESC
    """)
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(result, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    init_db()
    seed_data()
    mcp.run()