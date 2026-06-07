import streamlit as st
import pandas as pd
from predictor import get_live_fixtures, calculate_handicap_prob

# ตั้งค่าหน้าจอเว็บ
st.set_page_config(page_title="StepV2 - Handicap AI Predictor", layout="wide", page_icon="⚽")
st.title("⚽ AI Football Step Predictor (สูตรคำนวณราคาต่อรองแฮนดิแคป)")
st.write("ระบบคำนวณและจัดชุดสเต็ป 3-20 คู่ โดยคัดเลือกทีมที่มี **โอกาสชนะราคาต่อรองสูงสุด** ด้วยโมเดล Poisson")
st.markdown("---")

fixtures = get_live_fixtures()

if not fixtures:
    st.error("⚠️ ไม่สามารถดึงข้อมูลปัจจุบันได้ หรือตอนนี้ไม่มีแมตช์ที่ยังไม่เริ่มแข่งขัน")
else:
    analyzed_matches = []
    for f in fixtures:
        st.write(f"คู่: {f.get('home_team')} vs {f.get('away_team')} | Att: {f.get('home_att')} | HDP: {f.get('hdp')}")
        # --- 🚨 คำสั่งดักแบบด่วน 🚨 ---
    
        # ดักที่ 1: ถ้าไม่มีราคาต่อรอง (hdp เป็น 0 หรือค่าว่าง) ให้ข้ามเลย
        if f.get('hdp') is None or f.get('hdp') == 0 or f.get('hdp') == "0" or f.get('hdp') == "":
            continue
        
        # ดักที่ 2: ถ้าค่าเกมรุกทีมเหย้าและทีมเยือนเท่ากันเป๊ะ (แสดงว่าเป็นค่า Default ของระบบ) ให้ข้าม
        if f.get('home_att') == f.get('away_att'):
            continue
        
        # ----------------------------
        # 1. เพิ่มระบบคัดกรอง: ถ้าคู่ไหนไม่มีสถิติรุก-รับ หรือไม่มีราคาแฮนดิแคป ให้ "ข้าม" ทันที
        if f.get('home_att') is None or f.get('away_att') is None or f.get('hdp') is None:
            continue  # 👈 สั่งข้ามคู่นี้ไปเลย ไม่เอาไปคำนวณให้โมเดลเพี้ยน

        # 2. ป้องกันกรณีค่าสถิติหลุดมาเป็น 0 (ซึ่งทำให้ Poisson คำนวณไม่ได้)
        if f['home_att'] == 0 or f['away_att'] == 0:
            continue  # 👈 สั่งข้ามเช่นกันถ้าค่าเป็น 0
        # คำนวณโอกาสชนะราคาต่อรอง
        prob = calculate_handicap_prob(f['home_att'], f['home_def'], f['away_att'], f['away_def'], f['hdp'])
        
        # เปรียบเทียบฝั่งที่ได้เปรียบตามราคาต่อรอง
        if prob['home_cover_prob'] >= prob['away_cover_prob']:
            pick_team = f['home']
            win_prob = prob['home_cover_prob']
            final_odds = f['odds_home']
            hdp_text = f"ต่อ {abs(f['hdp'])}" if f['hdp'] < 0 else f"รอง {f['hdp']}"
        else:
            pick_team = f['away']
            win_prob = prob['away_cover_prob']
            final_odds = f['odds_away']
            hdp_text = f"รอง {abs(f['hdp'])}" if f['hdp'] < 0 else f"ต่อ {f['hdp']}"

        analyzed_matches.append({
            "league": f['league'],  # เก็บข้อมูลลีกไว้ใช้งาน
            "match": f"{f['home']} vs {f['away']}",
            "hdp": f['hdp'],
            "hdp_text": hdp_text,
            "pick": pick_team,
            "win_probability": win_prob,
            "expected_score": prob['expected_score'],
            "odds": final_odds
        })

    # --- SIDEBAR CONTROL ---
    st.sidebar.header("🎯 ตั้งค่าสเต็ปแฮนดิแคป")
    num_pairs = st.sidebar.slider("เลือกจำนวนคู่ในสเต็ป", min_value=3, max_value=20, value=3)
    bet_money = st.sidebar.number_input("เงินทุนเดิมพัน (บาท)", min_value=50, value=100, step=50)
    generate_button = st.sidebar.button("🚀 จัดชุดสเต็ปกินเต็ม", type="primary")

    # --- ส่วนของการแสดงผล OUTPUT ---
    if generate_button:
        st.subheader(f"📋 ทีเด็ดสเต็ป {num_pairs} คู่ (คัดจากโอกาสกินราคาต่อรองสูงสุด)")
        
        # เรียงลำดับคู่ที่ AI มั่นใจว่าจะชนะราคามากที่สุด
        sorted_step = sorted(analyzed_matches, key=lambda x: x['win_probability'], reverse=True)
        final_selection = sorted_step[:num_pairs]
        
        total_odds = 1.0
        table_data = []
        
        for i, match in enumerate(final_selection, 1):
            total_odds *= match['odds']
            table_data.append({
                "คู่ที่": i,
                "ลีก": match['league'],          # ✨ เพิ่มชื่อลีกตรง Output ส่วนที่แสดงผลแล้วครับ!
                "คู่แข่งขัน": match['match'],
                "ราคาต่อรอง": match['hdp_text'],
                "ทีเด็ดที่เลือก": f"🔥 {match['pick']}",
                "โอกาสกินราคา (%)": f"{match['win_probability']}%",
                "คาดการณ์สกอร์": match['expected_score'],
                "ค่าน้ำแฮนดิแคป": f"{match['odds']:.2f}"
            })
            
        df = pd.DataFrame(table_data)
        st.dataframe(df.set_index("คู่ที่"), use_container_width=True)
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="ราคารวมสเต็ปแฮนดิแคป", value=f"{total_odds:.2f} เท่า")
        with col2:
            st.metric(label="เงินลงทุนเดิมพัน", value=f"{bet_money:,.2f} บาท")
        with col3:
            potential_payout = bet_money * total_odds
            st.metric(label="ประมาณการเงินรางวัล (ถ้ากินเต็มทุกคู่)", value=f"{potential_payout:,.2f} บาท", delta=f"+{potential_payout-bet_money:,.2f} กำไร")
        st.balloons()
    else:
        st.info("💡 เลือกจำนวนคู่ด้านซ้าย แล้วกดปุ่มจัดชุดเพื่อดูทีเด็ดกินราคาแฮนดิแคปได้เลยครับ")
