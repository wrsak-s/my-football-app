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
        # --- 🚨 1. คำสั่งดักคู่บอลที่ข้อมูลไม่สมบูรณ์ (ด่วน) 🚨 ---
    
        # ดักเช็กชื่อทีม: ถ้าไม่มีชื่อทีมเหย้า/เยือน หรือเป็นค่าว่าง ให้ข้ามทันที
        if f.get('home') is None or f.get('away') is None or f.get('home') == "" or f.get('away') == "":
            continue
        
        # ดักเช็กราคาต่อรอง: ถ้าไม่มีราคา (hdp เป็น 0, ค่าว่าง หรือ None) ให้ข้ามทันที
        if f.get('hdp') is None or f.get('hdp') == 0 or f.get('hdp') == "0" or f.get('hdp') == "":
            continue
        
        # ดักเช็กค่าสถิติ Default: ถ้าค่าเกมรุกเท่ากันเป๊ะทุกจุด (แสดงว่าไม่มีข้อมูลสถิติจริง) ให้ข้าม
        if f.get('home_att') == f.get('away_att'):
            continue

        # แปลงค่า hdp ให้เป็นตัวเลขชัวร์ๆ ก่อน แล้วใส่เครื่องหมายลบสวนกลับไปให้สูตรคำนวณถูกต้อง
        try:
            current_hdp = -float(f['hdp'])
        except:
            current_hdp = 0  # ถ้าแปลงไม่ได้ให้เป็น 0 เพื่อไม่ให้โปรแกรมพัง
            
        # --- 🟢 2. โซนคำนวณและแสดงผล (ทำงานเฉพาะคู่ที่ข้อมูลผ่านเกณฑ์) ---
        # คำนวณโอกาสชนะราคาต่อรอง
        prob = calculate_handicap_prob(f['home_att'], f['home_def'], f['away_att'], f['away_def'], current_hdp)

        """
        # 1. สมมติว่าได้ค่าแฮนดิแคปที่โมเดลแนะนำออกมาจากตัวแปร (หรือแปลงจาก % ชนะมาเป็นราคาต่อ)
        # ในที่นี้สมมติชื่อตัวแปร model_hdp คือราคาที่โมเดลคิดได้ (เช่น 0.25)
        # และ real_hdp คือราคาปัจจุบันในสนาม (เช่น 0.75)

        # 2. แปลงค่าให้เป็นตัวเลขเพื่อเปรียบเทียบ
        try:
            model_hdp = float(prob.get('recommended_hdp', 0)) # ปรับตามตัวแปรที่โมเดลคุณส่งออกมา
            real_hdp = float(f['hdp'])
        except:
            model_hdp, real_hdp = 0, 0

        # 3. ตรรกะคัดสรรสูตรสเต็ปอัตโนมัติ
        recommendation = "⚖️ ราคาเสมอควบคู่ / ข้าม"

        if model_hdp > real_hdp:
        # ถ้าโมเดลคิดว่าควรต่อแพง แต่ราคาจริงเปิดมาถูก -> น่าเชียร์ "ทีมต่อ"
            recommendation = f"🔥 เชียร์ [ทีมต่อ]: {f['home']}"
    
        elif model_hdp < real_hdp:
        # ถ้าโมเดลคิดว่าควรต่อถูก แต่ราคาจริงเปิดมาแพงเกินหน้าเสื่อ -> น่าเชียร์ "ทีมรอง"
            recommendation = f"🛡️ เชียร์ [ทีมรอง]: {f['away']}"

        # 4. พ่นคำแนะนำออกหน้าจอ Streamlit ไปดูบน iPhone สวยๆ
        st.success(f"บทวิเคราะห์: {recommendation}")
        """

        # 📝 จุดที่ต้องเปลี่ยนตอนแสดงผลบนหน้าจอ Streamlit (เปลี่ยนจาก home_team เป็น home)
        # สมมติโค้ดเดิมของคุณเขียนแสดงผลไว้ประมาณนี้ ให้เปลี่ยนคีย์เป็น 'home' และ 'away' ครับ:
        #st.write(f"⚽ {f['home']} vs {f['away']}")
        #st.write(f"ราคาต่อรอง: {f['hdp']}")
    
        # ตรงนี้ให้แสดงค่า Ratio หรือผลลัพธ์ % จากตัวแปร prob ตามโค้ดเดิมของคุณได้เลยครับ
        # st.write(f"โอกาสชนะแฮนดิแคป: {prob}")
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
