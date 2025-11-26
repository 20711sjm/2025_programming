"""
리포트 생성 모듈
PDF 리포트 생성 기능
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import pandas as pd
import os


def generate_pdf_report(records_df, goals):
    """PDF 리포트를 생성합니다."""
    
    # 파일 경로 설정
    filename = f"data/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # PDF 문서 생성
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    
    # 스타일 설정
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # 제목
    story.append(Paragraph("체대 입시 기록 관리 리포트", title_style))
    story.append(Paragraph(f"생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # 전체 기록 요약
    if not records_df.empty:
        story.append(Paragraph("전체 기록 요약", heading_style))
        
        summary_data = [["종목", "기록 수", "최고 기록", "최근 기록"]]
        
        for sport in records_df["종목"].unique():
            sport_records = records_df[records_df["종목"] == sport]
            count = len(sport_records)
            
            if sport in ["100m", "200m", "400m", "800m", "1500m", "3000m"]:
                best = sport_records["기록"].min()
            else:
                best = sport_records["기록"].max()
            
            latest = sport_records.iloc[-1]["기록"]
            unit = sport_records.iloc[0]["단위"]
            
            summary_data.append([
                sport,
                str(count),
                f"{best:.2f} {unit}",
                f"{latest:.2f} {unit}"
            ])
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
    
    # 목표 달성률
    if goals:
        story.append(Paragraph("목표 달성률", heading_style))
        
        goal_data = [["종목", "현재 기록", "목표 기록", "달성률", "기한"]]
        
        for sport, goal_info in goals.items():
            sport_records = records_df[records_df["종목"] == sport]
            
            if not sport_records.empty:
                current = sport_records.iloc[-1]["기록"]
                goal = goal_info["목표기록"]
                unit = goal_info["단위"]
                deadline = goal_info["기한"]
                
                # 달성률 계산
                if unit in ["초"]:
                    achievement = (1 - (current - goal) / goal) * 100
                else:
                    achievement = (current / goal) * 100
                
                achievement = max(0, min(100, achievement))
                
                goal_data.append([
                    sport,
                    f"{current:.2f} {unit}",
                    f"{goal:.2f} {unit}",
                    f"{achievement:.1f}%",
                    deadline
                ])
        
        if len(goal_data) > 1:
            goal_table = Table(goal_data)
            goal_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(goal_table)
            story.append(Spacer(1, 0.3*inch))
    
    # PDF 빌드
    doc.build(story)
    
    return filename



