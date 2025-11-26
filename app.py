"""
체대 입시생 기록 관리 및 영상 피드백 시스템
메인 Streamlit 애플리케이션
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# 페이지 설정
st.set_page_config(
    page_title="체대 입시 기록 관리 시스템",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 디렉토리 생성
os.makedirs("data", exist_ok=True)
os.makedirs("videos", exist_ok=True)
os.makedirs("data/records", exist_ok=True)
os.makedirs("data/videos", exist_ok=True)
os.makedirs("data/feedback", exist_ok=True)

# 세션 상태 초기화
if 'records_df' not in st.session_state:
    st.session_state.records_df = pd.DataFrame()
if 'goals' not in st.session_state:
    st.session_state.goals = {}

# 유틸리티 함수 임포트
from utils import (
    load_records, save_records, load_goals, save_goals,
    calculate_improvement_rate, get_pb, format_time
)

# 메인 타이틀
st.title("🏃 체대 입시 기록 관리 시스템")
st.markdown("---")

# 사이드바 메뉴
st.sidebar.title("📋 메뉴")
menu = st.sidebar.radio(
    "기능 선택",
    ["📊 기록 입력", "📈 기록 비교 및 분석", "🎥 영상 관리", "💬 피드백", "📄 리포트"]
)

# 기록 입력 페이지
if menu == "📊 기록 입력":
    st.header("📊 운동 기록 입력")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sport_type = st.selectbox(
            "종목 선택",
            ["100m", "200m", "400m", "800m", "1500m", "3000m", "높이뛰기", "멀리뛰기", "포환던지기", "기타"]
        )
        
        if sport_type == "기타":
            sport_type = st.text_input("종목명을 입력하세요")
        
        record_value = st.number_input(
            "기록 입력",
            min_value=0.0,
            step=0.01,
            format="%.2f"
        )
        
        unit = st.selectbox(
            "단위",
            ["초", "미터", "센티미터", "회"]
        )
    
    with col2:
        date = st.date_input("날짜", value=datetime.now().date())
        time_of_day = st.selectbox("시간대", ["오전", "오후", "저녁"])
        weather = st.selectbox("날씨", ["맑음", "흐림", "비", "바람", "기타"])
        condition = st.selectbox("컨디션", ["최고", "좋음", "보통", "나쁨", "최악"])
        notes = st.text_area("메모 (선택사항)")
    
    if st.button("기록 저장", type="primary"):
        # 기록 데이터 로드
        records_df = load_records()
        
        # 새 기록 추가
        new_record = {
            "날짜": date.strftime("%Y-%m-%d"),
            "종목": sport_type,
            "기록": record_value,
            "단위": unit,
            "시간대": time_of_day,
            "날씨": weather,
            "컨디션": condition,
            "메모": notes,
            "입력시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        records_df = pd.concat([records_df, pd.DataFrame([new_record])], ignore_index=True)
        save_records(records_df)
        st.session_state.records_df = records_df
        
        st.success(f"✅ {sport_type} 기록이 저장되었습니다!")
        st.balloons()

# 기록 비교 및 분석 페이지
elif menu == "📈 기록 비교 및 분석":
    st.header("📈 기록 비교 및 분석")
    
    records_df = load_records()
    
    if records_df.empty:
        st.warning("⚠️ 저장된 기록이 없습니다. 먼저 기록을 입력해주세요.")
    else:
        # 종목 선택
        sport_types = records_df["종목"].unique().tolist()
        selected_sport = st.selectbox("분석할 종목 선택", sport_types)
        
        # 해당 종목의 기록 필터링
        sport_records = records_df[records_df["종목"] == selected_sport].copy()
        sport_records = sport_records.sort_values("날짜")
        sport_records["날짜"] = pd.to_datetime(sport_records["날짜"])
        
        if not sport_records.empty:
            # 통계 정보
            col1, col2, col3, col4 = st.columns(4)
            
            pb = get_pb(sport_records, selected_sport)
            latest = sport_records.iloc[-1]["기록"]
            first = sport_records.iloc[0]["기록"]
            improvement = calculate_improvement_rate(first, latest, selected_sport)
            
            with col1:
                st.metric("개인 최고 기록 (PB)", f"{pb['value']:.2f} {pb['unit']}")
            with col2:
                st.metric("최근 기록", f"{latest:.2f} {sport_records.iloc[-1]['단위']}")
            with col3:
                st.metric("첫 기록", f"{first:.2f} {sport_records.iloc[0]['단위']}")
            with col4:
                st.metric("향상률", f"{improvement:.2f}%")
            
            # 기록 추이 그래프
            st.subheader("📊 기록 추이 그래프")
            
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sport_records["날짜"],
                y=sport_records["기록"],
                mode='lines+markers',
                name='기록',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=8)
            ))
            
            # PB 라인 추가
            pb_value = pb['value']
            fig.add_hline(
                y=pb_value,
                line_dash="dash",
                line_color="red",
                annotation_text=f"PB: {pb_value:.2f} {pb['unit']}",
                annotation_position="right"
            )
            
            fig.update_layout(
                title=f"{selected_sport} 기록 추이",
                xaxis_title="날짜",
                yaxis_title=f"기록 ({sport_records.iloc[0]['단위']})",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 기록 상세 테이블
            st.subheader("📋 기록 상세 내역")
            display_df = sport_records[["날짜", "기록", "단위", "컨디션", "날씨", "메모"]].copy()
            display_df["날짜"] = display_df["날짜"].dt.strftime("%Y-%m-%d")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"⚠️ {selected_sport} 종목의 기록이 없습니다.")

# 영상 관리 페이지
elif menu == "🎥 영상 관리":
    st.header("🎥 훈련 영상 관리")
    
    tab1, tab2 = st.tabs(["영상 업로드", "영상 목록"])
    
    with tab1:
        st.subheader("영상 업로드")
        
        uploaded_file = st.file_uploader(
            "훈련 영상을 업로드하세요",
            type=["mp4", "mov", "avi"],
            help="MP4, MOV, AVI 형식의 영상을 업로드할 수 있습니다."
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                video_date = st.date_input("영상 촬영 날짜", value=datetime.now().date())
                sport_type = st.selectbox(
                    "종목",
                    ["100m", "200m", "400m", "800m", "1500m", "3000m", "높이뛰기", "멀리뛰기", "포환던지기", "기타"]
                )
            
            with col2:
                record_value = st.number_input("해당 기록 (선택사항)", min_value=0.0, step=0.01, format="%.2f")
                description = st.text_area("영상 설명")
            
            if st.button("영상 저장", type="primary"):
                # 영상 파일 저장
                video_filename = f"{video_date}_{sport_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{uploaded_file.name.split('.')[-1]}"
                video_path = os.path.join("data/videos", video_filename)
                
                with open(video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 영상 메타데이터 저장
                videos_df = load_records("data/videos_metadata.json")
                if videos_df.empty:
                    videos_df = pd.DataFrame(columns=["파일명", "날짜", "종목", "기록", "설명", "업로드시간"])
                
                new_video = {
                    "파일명": video_filename,
                    "날짜": video_date.strftime("%Y-%m-%d"),
                    "종목": sport_type,
                    "기록": record_value if record_value > 0 else None,
                    "설명": description,
                    "업로드시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                videos_df = pd.concat([videos_df, pd.DataFrame([new_video])], ignore_index=True)
                save_records(videos_df, "data/videos_metadata.json")
                
                st.success(f"✅ 영상이 저장되었습니다: {video_filename}")
    
    with tab2:
        st.subheader("저장된 영상 목록")
        
        videos_df = load_records("data/videos_metadata.json")
        
        if videos_df.empty:
            st.info("📹 업로드된 영상이 없습니다.")
        else:
            videos_df = videos_df.sort_values("날짜", ascending=False)
            
            for idx, row in videos_df.iterrows():
                with st.expander(f"📹 {row['종목']} - {row['날짜']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        video_path = os.path.join("data/videos", row["파일명"])
                        if os.path.exists(video_path):
                            st.video(video_path)
                        else:
                            st.error("영상 파일을 찾을 수 없습니다.")
                    
                    with col2:
                        st.write(f"**종목:** {row['종목']}")
                        st.write(f"**날짜:** {row['날짜']}")
                        if pd.notna(row['기록']) and row['기록'] > 0:
                            st.write(f"**기록:** {row['기록']}")
                        st.write(f"**설명:** {row['설명']}")
                        
                        # 피드백 확인 버튼
                        if st.button(f"피드백 보기", key=f"feedback_{idx}"):
                            st.session_state.selected_video = row["파일명"]
                            st.rerun()

# 피드백 페이지
elif menu == "💬 피드백":
    st.header("💬 코치 피드백")
    
    videos_df = load_records("data/videos_metadata.json")
    
    if videos_df.empty:
        st.warning("⚠️ 피드백을 남길 영상이 없습니다.")
    else:
        # 영상 선택
        video_list = [f"{row['종목']} - {row['날짜']} ({row['파일명']})" for _, row in videos_df.iterrows()]
        selected_video_str = st.selectbox("피드백을 남길 영상 선택", video_list)
        
        if selected_video_str:
            selected_filename = selected_video_str.split("(")[1].split(")")[0]
            selected_video = videos_df[videos_df["파일명"] == selected_filename].iloc[0]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                video_path = os.path.join("data/videos", selected_filename)
                if os.path.exists(video_path):
                    st.video(video_path)
                else:
                    st.error("영상 파일을 찾을 수 없습니다.")
            
            with col2:
                st.write(f"**종목:** {selected_video['종목']}")
                st.write(f"**날짜:** {selected_video['날짜']}")
                if pd.notna(selected_video['기록']) and selected_video['기록'] > 0:
                    st.write(f"**기록:** {selected_video['기록']}")
            
            st.markdown("---")
            
            # 피드백 입력
            st.subheader("피드백 작성")
            
            feedback_type = st.radio("피드백 유형", ["전체 평가", "기술 지적", "개선 사항", "칭찬", "기타"])
            
            timestamp = st.slider(
                "영상 시간 (초)",
                min_value=0,
                max_value=300,
                value=0,
                step=1,
                help="피드백이 해당하는 영상의 시간을 선택하세요"
            )
            
            feedback_text = st.text_area(
                "피드백 내용",
                height=200,
                placeholder="상세한 피드백을 작성해주세요..."
            )
            
            coach_name = st.text_input("코치 이름 (선택사항)")
            
            if st.button("피드백 저장", type="primary"):
                # 피드백 저장
                feedbacks_df = load_records("data/feedback.json")
                if feedbacks_df.empty:
                    feedbacks_df = pd.DataFrame(columns=["영상파일명", "피드백유형", "시간", "내용", "코치명", "작성시간"])
                
                new_feedback = {
                    "영상파일명": selected_filename,
                    "피드백유형": feedback_type,
                    "시간": timestamp,
                    "내용": feedback_text,
                    "코치명": coach_name if coach_name else "익명",
                    "작성시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                feedbacks_df = pd.concat([feedbacks_df, pd.DataFrame([new_feedback])], ignore_index=True)
                save_records(feedbacks_df, "data/feedback.json")
                
                st.success("✅ 피드백이 저장되었습니다!")
            
            # 기존 피드백 표시
            st.markdown("---")
            st.subheader("기존 피드백")
            
            feedbacks_df = load_records("data/feedback.json")
            video_feedbacks = feedbacks_df[feedbacks_df["영상파일명"] == selected_filename]
            
            if video_feedbacks.empty:
                st.info("아직 피드백이 없습니다.")
            else:
                for _, fb in video_feedbacks.iterrows():
                    with st.container():
                        st.markdown(f"**{fb['피드백유형']}** ({fb['시간']}초) - {fb['코치명']}")
                        st.write(fb['내용'])
                        st.caption(f"작성일: {fb['작성시간']}")
                        st.markdown("---")

# 리포트 페이지
elif menu == "📄 리포트":
    st.header("📄 목표 달성률 리포트")
    
    records_df = load_records()
    
    if records_df.empty:
        st.warning("⚠️ 리포트를 생성할 기록이 없습니다.")
    else:
        # 목표 설정
        st.subheader("목표 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            goal_sport = st.selectbox("목표 종목", records_df["종목"].unique().tolist())
            goal_value = st.number_input("목표 기록", min_value=0.0, step=0.01, format="%.2f")
            goal_unit = st.selectbox("단위", ["초", "미터", "센티미터", "회"])
            goal_date = st.date_input("목표 달성 기한")
        
        with col2:
            if st.button("목표 저장", type="primary"):
                goals = load_goals()
                goals[goal_sport] = {
                    "목표기록": goal_value,
                    "단위": goal_unit,
                    "기한": goal_date.strftime("%Y-%m-%d")
                }
                save_goals(goals)
                st.success("✅ 목표가 저장되었습니다!")
        
        # 리포트 생성
        st.markdown("---")
        st.subheader("목표 달성률 분석")
        
        goals = load_goals()
        
        if not goals:
            st.info("목표를 먼저 설정해주세요.")
        else:
            for sport, goal_data in goals.items():
                sport_records = records_df[records_df["종목"] == sport]
                
                if not sport_records.empty:
                    latest_record = sport_records.iloc[-1]["기록"]
                    goal_record = goal_data["목표기록"]
                    unit = goal_data["단위"]
                    deadline = goal_data["기한"]
                    
                    # 달성률 계산
                    if unit in ["초"]:  # 시간이 짧을수록 좋은 종목
                        achievement_rate = (1 - (latest_record - goal_record) / goal_record) * 100
                    else:  # 거리/높이 등
                        achievement_rate = (latest_record / goal_record) * 100
                    
                    achievement_rate = max(0, min(100, achievement_rate))
                    
                    with st.expander(f"📊 {sport} 목표 달성률"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("현재 기록", f"{latest_record:.2f} {unit}")
                        with col2:
                            st.metric("목표 기록", f"{goal_record:.2f} {unit}")
                        with col3:
                            st.metric("달성률", f"{achievement_rate:.1f}%")
                        
                        # 진행 바
                        st.progress(achievement_rate / 100)
                        
                        st.write(f"**목표 기한:** {deadline}")
                        
                        # 남은 기록 계산
                        if unit in ["초"]:
                            remaining = latest_record - goal_record
                            st.write(f"**목표까지:** {abs(remaining):.2f} {unit} {'단축' if remaining > 0 else '초과'}")
                        else:
                            remaining = goal_record - latest_record
                            st.write(f"**목표까지:** {abs(remaining):.2f} {unit} {'더 필요' if remaining > 0 else '초과'}")
            
            # 리포트 다운로드
            st.markdown("---")
            if st.button("📥 리포트 PDF 다운로드", type="primary"):
                from report_generator import generate_pdf_report
                
                pdf_path = generate_pdf_report(records_df, goals)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="PDF 다운로드",
                        data=pdf_file.read(),
                        file_name=f"체대입시_리포트_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )



