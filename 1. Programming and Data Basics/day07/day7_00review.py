# [1교시] - [Streamlit]

# 노트북 환경에서 안돼고 .py환경에서 가능하다
# 폴더이름도 사용하는 환경과 같으면 안된다
# 스트림릿 실행 : streamlit run prj2/app.py
# 스트림릿 링크 사이트 : Backend 역할
# 스트림릿은 실시간으로 계속 구동중이다
# Ctrl + c : 구동 멈춤
# streamlit은 파이썬 구조로 심플하고 간단하게 보여줄 때 활용
# st.markdown(' ')을 입력하면 다양한 스타일 적용이 가능

import streamlit as st
import pandas as pd
# 페이지 제목을 설정(브라우저 탭에 표시되는 것)
st.set_page_config(page_title="기초화면구성")

# 타이틀 출력(가장 큰 제목)
st.title("화면 구성")

# 헤더 출력(중간 크기 제목)
st.header("1. 다양한 텍스트 출력 방법")

# 일반 텍스트 출력
st.write('st.write는 가장 기본적인 출력')
st.write('숫자, 문자열, 데이터프레임 등 거의 모든것을 출력')
# 서브 헤더(작은 제목)
st.subheader("2. markdown활용하기")

# 마크다운 문법으로 다양한 스타일 적용
st.markdown('''
### 마크다운으로 할 수 있는 것들 :
            - '** 굵은 글씨 **'
            - '* 기울임 글씨 *'
            - "` 코드 표시 ``"
            - [링크 만들기](https://streamlit.io)

            > 이것은 인용구입니다.
            ''')
st.markdown('**굵은 글씨**')
st.markdown('*기울임 글씨*')
st.markdown("`import streamlit as st`")
st.markdown("`st.title('제목')`")
st.markdown("""
```python
import pandas as pd
pd.DataFrame(array)
```            
            """)

# [2교시]
# 취소선
st.divider()

# 데이터 프레임 생성 및 출력
st.header("3.pandas 데이터프레임 출력")

# 가상의 데이터
data = {
    "이름": ["김철수", "이영희", "박민수", "정지은", "최동욱"],
    "나이": [25, 23, 26, 24, 27],
    "수학": [85, 92, 78, 95, 88],
    "영어": [90, 88, 85, 92, 86],
    "과학": [88, 90, 92, 89, 91]
}
df = pd.DataFrame(data)


# 데이터프레임 출력 방법 1 : st.write()사용
st.subheader("방법 1 : st.write()로 출력")
st.write(df)

# 데이터프레임 출력 방법 2 : st.dataframe()사용
st.subheader("방법 2 : st.dataframe() 스크롤 정렬 가능")
st.dataframe(df, use_container_width=True)

# 데이터프레임 출력 방법3  : st.table()사용 / 사용자가 수정 할 수 없다.
st.subheader("방법 3 : st.table()로 정적 테이블")
st.table(df)

df.divide() # 구분선

# [3교시]
# 매트릭 카드(주요 지표 표시)
st.header('4. 매트릭 카드로 주요 지표 표시')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label='총 학생수', value=len(df))
with col2:
    st.metric(label='평균 수학 점수', value=f'{df['수학'].mean():.1f}점')
with col3:
    st.metric(label='총 학생수', value=f'{df['영어'].max()}점')

# 정보박스
st.info('Tip : st.write()는 만능 출력 함수, 특정 용도에는 전용 함수 st.dataframe() st.metric')

import streamlit as st
import pandas as pd

# 가상의 데이터 2
data = {
    "이름": ["김철수", "이영희", "박민수", "정지은", "최동욱", "김철호", "윤태희", "장민지"],
    "나이": [25, 23, 26, 24, 27, 22, 25, 23],
    "학년": ["3학년", "2학년", "4학년", "3학년", "4학년", "1학년", "3학년", "2학년"],
    "수학": [85, 92, 78, 95, 88, 70, 91, 87],
    "영어": [90, 88, 85, 92, 86, 75, 89, 90],
    "과학": [88, 90, 92, 89, 91, 80, 85, 88]
}
df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)
st.divider()

# 위젯
# st.text_input() 입력칸 만들기
# 텍스트 입력
st.subheader('텍스트 입력') # 무엇을 입력할지 알려줄 때
student_name = st.text_input('학생 이름을 입력하세요',placeholder="예: 김철수",
              help="검색하고 싶은 이름을 입력하세요") # 입력 칸 설명
# 입력된 이름으로 데이터 필터링
if student_name:
    filtered_by_name = df[df['이름'].str.contains(student_name)]
    if not filtered_by_name.empty:  
        st.success('성공')
        st.dataframe(filtered_by_name, use_container_width=True)
    else:
        st.warning('검색실패')

st.divider()

# 슬라이더
min_age =  st.slider('최소 나이를 선택하세요',
          min_value=int(df['나이'].min()),
          max_value=int(df['나이'].max()),
          value=int(df['나이'].mean()),
          step=1
          )

# 슬라이드바로 활용한 나이로 필터링
filtered_by_age = df[df['나이'] >= min_age]
st.dataframe(filtered_by_age, use_container_width=True)

st.divider()

# Select Box
selected_grade = st.selectbox('학년을 선택하세요',
                              options= ['전체'] + sorted(df['학년'].unique().tolist()))
# 학년으로 필터링
if selected_grade == '전체':
    filtered_by_grade = df
else:
    filtered_by_grade = df[df['학년'] == selected_grade]
st.dataframe(filtered_by_grade, use_container_width=True)

st.divider()

# [4교시]
# multiselect
selected_subject = st.multiselect("과목을 선택하세요",
               options=['수학', '과학', '영어'], default=['수학', '과학'])
selected_subject = ['이름', '나이', '학년'] + selected_subject
filtered_by_subject = df[selected_subject]
st.dataframe(filtered_by_subject)

# [5교시] - 레이아웃 제작
import streamlit as st
import pandas as pd

# 사이드바, 컬럼, 탭을 활용하여 화면 구성
st.set_page_config(
    page_title='레이아웃디자인',
    layout='wide'
)
st.title('레이아웃디자인')

data = {
    "이름": ["김철수", "이영희", "박민수", "정지은", "최동욱", "강서연", "윤태희", "장민지"],
    "나이": [25, 23, 26, 24, 27, 22, 25, 23],
    "학년": ["3학년", "2학년", "4학년", "3학년", "4학년", "1학년", "3학년", "2학년"],
    "수학": [85, 92, 78, 95, 88, 70, 91, 87],
    "영어": [90, 88, 85, 92, 86, 75, 89, 90],
    "과학": [88, 90, 92, 89, 91, 80, 85, 88]
}
df = pd.DataFrame(data)

# 1. 사이드바 (Sidebar) 사용하기
st.sidebar.title('설정메뉴')
st.sidebar.write('사이드바에 필터링 옵션을 모아둘수 있습니다.')

# 사이드바에 필터 옵션 배치
st.sidebar.header('데이터 필터')

# 사이드바 - 학년 선택
sidebar_grade = st.sidebar.selectbox(
    '학년 선택',
    options=["전체"] + sorted(df['학년'].unique().tolist())
)

# 사이드바 - 최소 나이
sidebar_min_age = st.sidebar.slider(
    "최소 나이",
    min_value = df['나이'].min(),
    max_value = df['나이'].max(),
    value = int(df["나이"].mean())
)

# 사이드바 - 과목 선택
sidebar_subjects = st.sidebar.multiselect(
    "표시할 과목",
    options=['수학', '영어', '과학'],
    default=['수학', '영어', '과학']
)

# 사이드바 구분선
st.sidebar.divider()

# 사이드바 - 추가 옵션
st.sidebar.header("추가 옵션")
show_stats = st.sidebar.checkbox("통계표시", value = True)
show_chart = st.sidebar.checkbox("차트표시", value = True)

# 필터링 적용
filtered_df = df.copy() # 원본 훼손을 방지하기 위해 복사

if sidebar_grade != '전체':
    filtered_df = filtered_df[filtered_df['학년'] == sidebar_grade]

filtered_df = filtered_df[filtered_df['나이'] >= sidebar_min_age]

st.sidebar.success(f"{len(filtered_df)}명의 학생이 검색되었습니다.")

# 2. 컬럼(Columns)으로 화면 나누기
st.header("1. 컬럼으로 화면 분할하기")
st.write("화면을 여러개의 열로 나눠서 정보를 정리할 수 있습니다.")

# 3개의 컬럼 생성 (동일한 너비)
col1, col2, col3 = st.columns(3)

#각 컬럼에 매트릭 카드 배치
with col1:
    st.metric(
        '총 학생수',
        value=len(filtered_df),
        delta = f"{len(filtered_df) - len(df)} (필터적용)"
        # 필터가 적용되어 원본대비 -가 작게보임
    )

with col2:
    if sidebar_subjects:
        avg_score = filtered_df[sidebar_subjects].mean().mean()
        st.metric(
            label=" 평균 점수",
            value=f"{avg_score:.1f}점",
            delta="2.3점" if avg_score > 85 else "-1.2점"
        )
    else:
        st.metric(label=" 평균 점수", value="N/A")   

with col3:
    if sidebar_subjects:
        max_score = filtered_df[sidebar_subjects].max().max()
        st.metric(
            label="최고 점수",
            value=f"{max_score}점"
        )
    else:
        st.metric(label="최고 점수", value="N/A")

st.divider()

# [6교시]
# 2:1 비율로 컬럼 나누기
st.header("2. 비율을 조정한 컬럼 레이아웃")

col_left, col_right = st.columns([2, 1])  # 2:1 비율

with col_left:
    st.subheader(" 필터링된 학생 데이터")
    if sidebar_subjects:
        columns_to_show = ["이름", "나이", "학년"] + sidebar_subjects
        st.dataframe(filtered_df[columns_to_show], use_container_width=True, height=300)
    else:
        st.dataframe(filtered_df[["이름", "나이", "학년"]], use_container_width=True, height=300)

with col_right:
    st.subheader(" 요약 정보")
    if show_stats and sidebar_subjects:
        st.write("**과목별 평균**")
        for subject in sidebar_subjects:
            avg = filtered_df[subject].mean()
            st.write(f"• {subject}: {avg:.1f}점")
    else:
        st.info("사이드바에서 '통계 표시'를 선택하세요.")

st.divider()
# 3. 탭(Tabs)으로 콘텐츠 구분하기
st.header("3. 탭으로 콘텐츠 구분하기")
st.write("탭을 사용하면 많은 정보를 깔끔하게 정리할 수 있습니다.")

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs([" 데이터", " 차트", " 랭킹", " 정보"])

# 탭 1: 데이터 테이블
with tab1:
    st.subheader("전체 데이터 테이블")
    st.dataframe(filtered_df, use_container_width=True)
    
    # 탭 안에서도 컬럼 사용 가능
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("데이터 요약")
        st.write(f" 학생 수: {len(filtered_df)}명")
        st.write(f" 평균 나이: {filtered_df['나이'].mean():.1f}세")
    with col_b:
        st.write("학년 분포")
        grade_counts = filtered_df['학년'].value_counts()
        st.dataframe(grade_counts.to_frame(name="인원"), use_container_width=True)

# 탭 2: 차트
with tab2:
    st.subheader("성적 시각화")
    
    if show_chart and sidebar_subjects:
        # 과목별 평균 점수 차트
        st.write("과목별 평균 점수")
        avg_by_subject = filtered_df[sidebar_subjects].mean()
        st.bar_chart(avg_by_subject)
        
        # 학생별 점수 추이 (첫 5명만)
        st.write("학생별 성적 비교 (상위 5명)")
        chart_df = filtered_df[["이름"] + sidebar_subjects].head(5).set_index("이름")
        st.line_chart(chart_df)
    else:
        st.info("사이드바에서 '차트 표시'를 선택하고 과목을 선택하세요.")

# 탭 3: 랭킹
with tab3:
    st.subheader("성적 순위")
    
    if sidebar_subjects:
        rank_df = filtered_df.copy()
        rank_df['평균'] = rank_df[sidebar_subjects].mean(axis=1)
        rank_df['총점'] = rank_df[sidebar_subjects].sum(axis=1)
        rank_df = rank_df.sort_values('평균', ascending=False)
        
        # 순위 추가
        rank_df['순위'] = range(1, len(rank_df) + 1)
        
        st.dataframe(
            rank_df[['순위', '이름', '학년'] + sidebar_subjects + ['평균', '총점']],
            use_container_width=True
        )
        
        # 1등 학생 하이라이트
        if len(rank_df) > 0:
            top_student = rank_df.iloc[0]
            st.success(f" 1등: {top_student['이름']} ({top_student['학년']}) - 평균 {top_student['평균']:.1f}점")
    else:
        st.warning("사이드바에서 최소 하나의 과목을 선택하세요.")

# 탭 4: 정보
with tab4:
    st.subheader(" 레이아웃 가이드")
    
    st.markdown("""
    ### 배운 레이아웃 기능들:
    
    1. 사이드바 (Sidebar)
       - `st.sidebar.title()`, `st.sidebar.selectbox()` 등
       - 필터나 설정을 별도 공간에 배치
    
    2. 컬럼 (Columns)
       - `st.columns(3)` - 동일한 너비로 3개 분할
       - `st.columns([2, 1])` - 2:1 비율로 분할
       - `with col1:` 구문으로 각 컬럼에 콘텐츠 추가
    
    3. 탭 (Tabs)
       - `st.tabs(["탭1", "탭2"])` - 여러 탭 생성
       - `with tab1:` 구문으로 각 탭에 콘텐츠 추가
    
    4. 페이지 설정
       - `layout="wide"` - 화면을 넓게 사용
       - `layout="centered"` - 중앙 정렬 (기본값)
    """)

st.divider()

st.info("Tip: 실제 대시보드를 만들 때는 사이드바에 필터를, 메인 영역에는 탭으로 구분된 콘텐츠를 배치하는 것이 일반적입니다!")

# ---------------------------------------------
# [7교시]

# 조건문 활용해서 합격/불합격 확인한다

score = 10
if score >=60:
    result = '합격'
else:
    result = '불합격'

result

# 위의 조건문을 한줄로 만들어서 사용할 수 있다

score = 10
result = '합격' if score >=60 else '불합격'
result

# 데이터프레임을 관리할 때 pandas로 작업 진행한다

import pandas as pd

data = {
    "이름": ["김철수", "이영희", "박민수", "정지은", "최동욱", "강서연", "윤태희", "장민지"],
    "나이": [25, 23, 26, 24, 27, 22, 25, 23],
    "학년": ["3학년", "2학년", "4학년", "3학년", "4학년", "1학년", "3학년", "2학년"],
    "수학": [85, 92, 78, 95, 88, 70, 91, 87],
    "영어": [90, 88, 85, 92, 86, 75, 89, 90],
    "과학": [88, 90, 92, 89, 91, 80, 85, 88]
}
df = pd.DataFrame(data)

# 각 리스트의 최대값을 구한다
df[['수학', '영어']].max()

# 각 리스트의 최대값중에 제일 큰 최대값을 구한다
df[ ['수학','영어'] ].max().max()

# 두개의 리스트를 하나로 묶어서 데이터프레임 형식으로 만들어준다
df[ ["이름", "나이", "학년"] + ['수학', '영어'] ]

df[ '수학' ] # --> series 타입으로 반환된다.

df[ ['수학','과학'] ] # --> dataframe 타입으로 반환된다.

# 각 과목의 평균값을 구한다.
for subject in ['수학', '영어', '과학']:
    print(subject, df[subject].mean())

[8교시]
과제 : app3.py를 streamlit으로 들어가서 버그 있는것들 수정하기, json연동하기, 학생추가에서 추가를하고나면 빈칸이 되도록 만들기
밑의 로직들 활용해서 버그 수정해보기!

# 입력 위젯 (key 지정)
new_name = st.text_input("이름", key="new_name")
new_age = st.text_input("나이", key="new_age")

# 저장 로직
if save_students_to_json(df_updated):
    st.success(f"'{new_name}' 학생이 추가되었습니다!")
    st.balloons()
    # 입력값 초기화
    st.session_state["new_name"] = ""
    st.session_state["new_age"] = ""
    # 페이지 재실행하여 UI 반영
    st.rerun()
else:
    st.error("저장에 실패했습니다.")