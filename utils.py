"""
유틸리티 함수 모음
데이터 로드/저장, 계산 함수 등
"""

import pandas as pd
import json
import os
from datetime import datetime


def load_records(filepath="data/records.json"):
    """기록 데이터를 로드합니다."""
    if os.path.exists(filepath):
        try:
            df = pd.read_json(filepath, orient='records')
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()


def save_records(df, filepath="data/records.json"):
    """기록 데이터를 저장합니다."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_json(filepath, orient='records', force_ascii=False, indent=2)


def load_goals():
    """목표 데이터를 로드합니다."""
    filepath = "data/goals.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_goals(goals):
    """목표 데이터를 저장합니다."""
    filepath = "data/goals.json"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(goals, f, ensure_ascii=False, indent=2)


def calculate_improvement_rate(first_record, latest_record, sport_type):
    """향상률을 계산합니다."""
    if first_record == 0:
        return 0
    
    # 시간 종목 (초 단위) - 값이 작을수록 좋음
    if sport_type in ["100m", "200m", "400m", "800m", "1500m", "3000m"]:
        improvement = ((first_record - latest_record) / first_record) * 100
    else:  # 거리/높이 종목 - 값이 클수록 좋음
        improvement = ((latest_record - first_record) / first_record) * 100
    
    return improvement


def get_pb(records_df, sport_type):
    """개인 최고 기록(PB)을 반환합니다."""
    if records_df.empty:
        return {"value": 0, "unit": ""}
    
    # 시간 종목 (초 단위) - 값이 작을수록 좋음
    if sport_type in ["100m", "200m", "400m", "800m", "1500m", "3000m"]:
        pb_value = records_df["기록"].min()
    else:  # 거리/높이 종목 - 값이 클수록 좋음
        pb_value = records_df["기록"].max()
    
    unit = records_df.iloc[0]["단위"]
    
    return {"value": pb_value, "unit": unit}


def format_time(seconds):
    """초를 분:초 형식으로 변환합니다."""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:05.2f}"


def calculate_achievement_rate(current, goal, unit):
    """목표 달성률을 계산합니다."""
    if goal == 0:
        return 0
    
    # 시간 종목 (초 단위) - 값이 작을수록 좋음
    if unit in ["초"]:
        rate = (1 - (current - goal) / goal) * 100
    else:  # 거리/높이 등
        rate = (current / goal) * 100
    
    return max(0, min(100, rate))



