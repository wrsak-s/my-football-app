from datetime import datetime
import requests
import pandas as pd
from scipy.stats import poisson

# 💡 สมัครรับ Key ฟรีได้ที่ https://dashboard.api-football.com/
API_KEY = "daae70ff813054f6edf2cbf93151d7de" 
BASE_URL = "https://v3.football.api-sports.io"

def get_live_fixtures():
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_KEY
    }
    today = datetime.now().strftime('%Y-%m-%d')
    params = {'date': today}
    
    try:
        response = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params)
        data = response.json()
        
        actual_fixtures = []
        for item in data.get('response', []):
            if item['fixture']['status']['short'] == 'NS':
                # จำลองราคาแฮนดิแคป (HDP) เช่น -0.5, -1.0, 0.0, +0.25
                # (ในระบบใหญ่จริง สามารถดึงค่าจริงจาก endpoint /odds ของ API ตัวนี้ได้ครับ)
                import random
                mock_hdp = random.choice([-0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75])
                
                actual_fixtures.append({
                    "match_id": item['fixture']['id'],
                    "league": item['league']['name'],
                    "home": item['teams']['home']['name'],
                    "away": item['teams']['away']['name'],
                    "home_att": 1.4, 
                    "home_def": 0.8,
                    "away_att": 1.0,
                    "away_def": 1.2,
                    "hdp": mock_hdp,    # 🎯 เพิ่มราคาต่อรองของคู่นี้ (ถ้าติดลบคือทีมเหย้าต่อ ถ้าเป็นบวกคือทีมเหย้ารอง)
                    "odds_home": 1.85,  # ราคาจ่ายแบบเอเชียนแฮนดิแคปมักจะอยู่แถวๆ 1.80 - 2.00
                    "odds_away": 1.95
                })
        return actual_fixtures
    except Exception as e:
        print(f"Error: {e}")
        return []

def calculate_handicap_prob(home_attack, home_defense, away_attack, away_defense, hdp, league_avg_goals=1.35):
    # บั๊กมักจะเกิดตรงนี้: ต้องแปลง hdp ให้เป็นตัวเลขทศนิยม (float) ชัวร์ๆ ก่อน
    try:
        hdp = float(hdp)
    except:
        return {"home_win": 0, "away_win": 0} # ถ้าแปลงไม่ได้ให้คืนค่า 0
    """
    คำนวณความน่าจะเป็นในการ 'ชนะราคาต่อรอง' (Asian Handicap)
    hdp: ราคาต่อรองของทีมเหย้า (เช่น -0.5 คือทีมเหย้าต่อครึ่งลูก)
    """
    expected_home_goals = home_attack * away_defense * league_avg_goals
    expected_away_goals = away_attack * home_defense * league_avg_goals
    
    max_goals = 6
    home_matrix = [poisson.pmf(i, expected_home_goals) for i in range(max_goals)]
    away_matrix = [poisson.pmf(i, expected_away_goals) for i in range(max_goals)]
    
    prob_home_cover = 0.0  # โอกาสทีมเหย้าชนะราคา
    prob_away_cover = 0.0  # โอกาสทีมเยือนชนะราคา
    
    for h in range(max_goals):
        for a in range(max_goals):
            prob = home_matrix[h] * away_matrix[a]
            
            # นำสกอร์ทีมเหย้า มาบวก/ลบ ด้วยราคาต่อรอง แล้วเทียบกับทีมเยือน
            calculated_score = h + hdp  
            
            if calculated_score > a:
                prob_home_cover += prob  # ทีมเหย้ากินราคา
            elif calculated_score < a:
                prob_away_cover += prob  # ทีมเยือนกินราคา
            else:
                # กรณีเสมอราคา (เช่น ต่อ 1 ลูกแล้วผลออก 1-0) เจ๊าคืนทุน ไม่เอามาคิดเป็นแพ้
                pass 
                
    return {
        "home_cover_prob": round(prob_home_cover * 100, 2),
        "away_cover_prob": round(prob_away_cover * 100, 2),
        "expected_score": f"{round(expected_home_goals, 1)} - {round(expected_away_goals, 1)}"
    }
