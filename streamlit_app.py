from html import escape

import streamlit as st


TOTAL_BLOCKS = 12
SCORE_NAMES = ["건강", "학업", "가족", "친구", "행복"]
INITIAL_SCORES = {"건강": 0, "학업": 0, "가족": 0, "친구": 0, "행복": 30}
UNASSIGNED = "비워 두기"
AREA_COLORS = {
    "건강": "#55a630",
    "학업": "#277da1",
    "가족": "#e09f3e",
    "친구": "#d1495b",
}
AREA_BACKGROUND_COLORS = {
    "건강": "#cfe5c2",
    "학업": "#c3dfeb",
    "가족": "#f2d99f",
    "친구": "#edc1c8",
}
AREAS = {
    "건강": {
        "activities": ["낮잠 및 휴식", "가벼운 운동", "맛있는 간식 먹기"],
        "effects": {"건강": 10, "행복": 5},
    },
    "학업": {
        "activities": ["공부하기", "학원 가기", "관심 분야 독서하기"],
        "effects": {"학업": 10, "행복": -5},
    },
    "가족": {
        "activities": ["가정일 돕기", "가족과 저녁 식사하기", "가족과 대화 및 보드게임"],
        "effects": {"가족": 10, "행복": 5},
    },
    "친구": {
        "activities": ["친구랑 놀기", "친구와 온라인 게임하기", "친구 고민 들어주기"],
        "effects": {"친구": 10, "행복": 5},
    },
}
ACTIVITY_TO_AREA = {
    f"{area} · {activity}": area
    for area, details in AREAS.items()
    for activity in details["activities"]
}
ACTIVITY_OPTIONS = [UNASSIGNED, *ACTIVITY_TO_AREA]


def format_time(minutes):
    hour = minutes // 60
    period = "오전" if hour < 12 else "오후"
    display_hour = hour % 12 or 12
    return f"{period} {display_hour}:{minutes % 60:02d}"


def initialize_state():
    if "scores" not in st.session_state:
        st.session_state.scores = INITIAL_SCORES.copy()
    for slot in range(TOTAL_BLOCKS):
        st.session_state.setdefault(f"slot_{slot}", UNASSIGNED)


st.set_page_config(page_title="시간 관리 도전하기", page_icon="🕒", layout="wide")
initialize_state()

st.title("시간 관리 도전하기")

slot_selections = [
    st.session_state[f"slot_{slot}"] for slot in range(TOTAL_BLOCKS)
]
planned_changes = {name: 0 for name in SCORE_NAMES}
for selection in slot_selections:
    area = ACTIVITY_TO_AREA.get(selection)
    if area:
        for score_name, points in AREAS[area]["effects"].items():
            planned_changes[score_name] += points

projected_scores = {
    name: max(0, min(100, st.session_state.scores[name] + planned_changes[name]))
    for name in SCORE_NAMES
}

st.header("예상 점수")
st.caption("시간 칸을 선택하면 계획을 반영한 점수가 바로 표시돼요.")
score_columns = st.columns(len(SCORE_NAMES))
for column, name in zip(score_columns, SCORE_NAMES):
    current_score = st.session_state.scores[name]
    projected_score = projected_scores[name]
    with column:
        st.metric(
            name,
            f"{projected_score}점",
            delta=f"{projected_score - current_score:+d}점",
            help=f"현재 {current_score}점에서 오늘 계획을 반영한 예상 점수예요.",
        )
        st.progress(projected_score / 100)

st.header("오늘의 시간표")
st.caption("오후 3시부터 9시까지, 각 칸은 30분이에요. 원하는 시간 칸을 골라 활동을 배치하세요.")
used_blocks = sum(selection != UNASSIGNED for selection in slot_selections)
st.markdown(f"### 채운 블록: {used_blocks} / {TOTAL_BLOCKS}")
area_counts = {area: 0 for area in AREAS}
for selection in slot_selections:
    area = ACTIVITY_TO_AREA.get(selection)
    if area:
        area_counts[area] += 1
count_columns = st.columns(len(AREAS))
for column, (area, count) in zip(count_columns, area_counts.items()):
    with column:
        st.markdown(
            f'<span style="display:inline-block;width:12px;height:12px;'
            f'border-radius:50%;background:{AREA_COLORS[area]};'
            f'margin-right:6px"></span><strong>{area}: {count}블록</strong>',
            unsafe_allow_html=True,
        )
        effects = " · ".join(
            f"{score_name} {points:+d}점"
            for score_name, points in AREAS[area]["effects"].items()
        )
        st.caption(f"1블록당 {effects}")

for slot, selection in enumerate(slot_selections):
    start_minutes = 15 * 60 + slot * 30
    end_minutes = start_minutes + 30
    start_time = format_time(start_minutes)
    end_time = format_time(end_minutes)
    area = ACTIVITY_TO_AREA.get(selection)
    color = AREA_COLORS.get(area, "#cbd5e1")
    marker_column, time_column, activity_column = st.columns([0.12, 0.32, 1])
    with marker_column:
        st.markdown(
            f'<div style="height:64px;position:relative;display:flex;'
            f'align-items:center;justify-content:center">'
            f'<span style="position:absolute;top:-20px;bottom:-20px;width:3px;'
            f'background:#d1d5db"></span>'
            f'<span style="z-index:1;width:24px;height:24px;border-radius:50%;'
            f'background:{color};border:3px solid white;box-sizing:border-box"></span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with time_column:
        st.markdown(
            f'<div style="height:64px;display:flex;align-items:center;'
            f'font-weight:600;white-space:nowrap">{start_time}–{end_time}</div>',
            unsafe_allow_html=True,
        )
    with activity_column:
        st.selectbox(
            f"{start_time} 활동",
            ACTIVITY_OPTIONS,
            key=f"slot_{slot}",
            label_visibility="collapsed",
        )

st.header("한눈에 보는 블록 배치")
st.caption("12개 블록을 한눈에 확인할 수 있어요. 각 칸은 30분이며, 색으로 영역을 구분해요.")
overview_blocks = []
for slot, selection in enumerate(slot_selections):
    start_time = format_time(15 * 60 + slot * 30)
    area = ACTIVITY_TO_AREA.get(selection)
    background_color = AREA_BACKGROUND_COLORS.get(area, "#e2e8f0")
    activity = selection.removeprefix(f"{area} · ") if area else UNASSIGNED
    area_label = area or "미배치"
    overview_blocks.append(
        f'<div role="listitem" style="min-width:0;box-sizing:border-box;min-height:104px;'
        f'padding:8px 6px;border-right:2px solid white;background:{background_color}">'
        f'<div style="font-size:12px;color:#000;white-space:nowrap">'
        f'{escape(start_time)}</div>'
        f'<div style="margin-top:5px;font-size:12px;font-weight:700;color:#000">'
        f'{escape(area_label)}</div>'
        f'<div title="{escape(selection)}" style="margin-top:4px;font-size:12px;'
        f'line-height:1.3;overflow-wrap:anywhere;color:#000">'
        f'{escape(activity)}</div></div>'
    )
st.markdown(
    '<div style="width:100%;border:1px solid #cbd5e1;border-radius:8px;'
    'overflow:hidden"><div role="list" aria-label="오늘의 블록 배치 요약" '
    f'style="display:grid;grid-template-columns:repeat({TOTAL_BLOCKS},minmax(0,1fr))">'
    + "".join(overview_blocks)
    + "</div></div>",
    unsafe_allow_html=True,
)

if used_blocks == TOTAL_BLOCKS:
    st.header("최종 점수")
    final_score_columns = st.columns(len(SCORE_NAMES))
    for column, name in zip(final_score_columns, SCORE_NAMES):
        with column:
            st.metric(name, f"{projected_scores[name]}점")
            st.progress(projected_scores[name] / 100)
