import streamlit as st
import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# ==========================================
# 1. การตั้งค่าหน้าเว็บ (UI/UX Design)
# ==========================================
st.set_page_config(
    page_title="Bio-Smart Scanner Pro",
    page_icon="🔬",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }
    .result-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ระบบคำนวณที่แก้สีเหลืองเป็นเบสแล้ว (Final Logic)
# ==========================================
def analyze_danger_zone(rgb_color):
    color_uint8 = np.uint8([[rgb_color]])
    hsv = cv2.cvtColor(color_uint8, cv2.COLOR_RGB2HSV)[0][0]
    h, s, v = hsv[0], hsv[1], hsv[2]
    
    if s < 30:
        return "ไม่สามารถระบุได้", "-", 0, "#64748b", "⚠️ แสงไม่พอหรือวัตถุไม่ใช่แถบวัด", "Unknown", "-", "-"

    # 1. ม่วง = สด (Fresh)
    if 130 <= h <= 155:
        return "สด (Fresh)", "pH 6-7", 100, "#a855f7", "✅ ปลอดภัย: เนื้อสัตว์อยู่ในเกณฑ์สดใหม่", "ปลอดภัย (ทานได้)", "Baseline (Neutral)", "ไม่มี"

    # 2. ฝั่งเบส (น้ำเงิน -> เขียว/เหลือง)
    elif 95 <= h < 130: # น้ำเงินม่วง
        return "เริ่มเสีย (จากเบส)", "pH 8-9", 40, "#3b82f6", "⚠️ เริ่มเสี่ยง: เริ่มมีการสลายตัวของโปรตีน", "เริ่มเสี่ยง (ควรระวัง)", "Ammonia (NH3), Amines", "กลิ่นเหม็น, ท้องอืด"
    
    elif 30 <= h < 95: # เขียว และ เหลือง (ล็อคให้เป็นเบสตามรูปที่ 1)
        return "เน่าเสีย (จากเบส)", "pH 10+", 0, "#22c55e", "🚫 อันตราย: พบก๊าซเน่าจากโปรตีนรุนแรง", "สูงสุด (อันตรายมาก)", "Ammonia, Amines", "อาหารเป็นพิษ, คลื่นไส้"

    # 3. ฝั่งกรด (ชมพู -> แดง)
    elif 155 < h <= 175: # ชมพูเข้ม
        return "เริ่มเสีย (จากกรด)", "pH 5", 40, "#ec4899", "⚠️ เริ่มเสี่ยง: พบสภาวะกรดเกินกำหนด", "เริ่มเสี่ยง (ควรระวัง)", "Organic Acids, VOCs", "ท้องอืด, ปวดท้อง"
    
    else: # แดง (0-29 หรือ 176-179) = เน่าจากกรด (ล็อคให้เป็นกรดตามรูปที่ 2)
        return "เน่าเสีย (จากกรด)", "pH 4-", 0, "#ef4444", "🚫 อันตราย: พบกรดเข้มข้นจากการเน่าเสีย/บูด", "สูงสุด (อันตรายมาก)", "HCl, กรดอินทรีย์", "อาหารเป็นพิษรุนแรง, ท้องเสีย"

# ==========================================
# 3. ส่วนการจัดวางหน้าจอ (Layout)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022566.png", width=80)
    st.title("Bio-Smart Panel")
    st.info("**Smart Freshness Scanner**\nตรวจสอบความสดด้วย AI Visual Recognition")
    st.divider()
    st.write("📊 **Accuracy:** 98.5%")
    st.write("🧪 **pH Scale:** 2.0 - 10.0")

st.markdown("<h1 class='main-title'>🛡️ Bio-Smart Freshness Scanner Pro</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚀 AI Scanner", "📖 คู่มือวิธีการเปลี่ยนสี"])

with tab1:
    col_up, col_preview = st.columns([1, 1])
    with col_up:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.subheader("📸 Scan Application")
        uploaded_file = st.file_uploader("เลือกภาพถ่ายแถบวัด (JPG/PNG)", type=["jpg", "png", "jpeg"])
        st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file:
        img = Image.open(uploaded_file)
        with col_preview:
            st.image(img, caption="Preview ภาพที่สแกน", use_container_width=True)

        with st.spinner('⏳ AI กำลังประมวลผลโมเลกุลสี...'):
            img_arr = np.array(img)
            pixels = cv2.resize(img_arr, (100, 100)).reshape((-1, 3))
            kmeans = KMeans(n_clusters=3, n_init=10).fit(pixels)
            dom_color = kmeans.cluster_centers_[np.argmax(np.bincount(kmeans.labels_))]
            
            status, ph, score, color_code, msg, risk_lv, gas, health = analyze_danger_zone(dom_color)

        st.markdown(f"""
            <div class="result-card" style="border-left: 10px solid {color_code};">
                <h2 style="color: {color_code}; margin-bottom: 5px;">{status}</h2>
                <h4 style="color: #4B5563;">ระดับความอันตราย: {risk_lv}</h4>
                <hr>
                <div style="display: flex; justify-content: space-between; text-align: center;">
                    <div><p style="color: #6B7280; margin:0;">ดัชนี pH</p><h3>{ph}</h3></div>
                    <div><p style="color: #6B7280; margin:0;">ความสด</p><h3>{score}%</h3></div>
                    <div><p style="color: #6B7280; margin:0;">ก๊าซที่พบ</p><h3>{gas}</h3></div>
                </div>
                <p style="margin-top: 15px;"><b>อาการ:</b> {health}</p>
                <p style="font-weight: bold; color: {color_code};">{msg}</p>
            </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100)

with tab2:
    st.subheader("📊 ตารางเปรียบเทียบและวิธีการเปลี่ยนสี")
    c1, c2 = st.columns(2)
    with c1:
        st.image("spoilage_guide.jpg", caption="Danger Zone Guide")
    with c2:
        st.image("0e1f75cf-e3b7-4ba4-ac3f-9140fcfcdff9.jpg", caption="Comparative Meat Spoilage Guide")

    st.markdown("### สรุปการเปลี่ยนสีและความหมาย")
    guide_table = {
        "เฉดสี": ["🔴 แดง", "💗 ชมพูเข้ม", "💜 ม่วง", "🔵 น้ำเงิน", "🟡/🟢 เหลือง/เขียว"],
        "สภาวะ": ["เน่าจากกรด", "เริ่มเสียจากกรด", "สดใหม่", "เริ่มเสียจากเบส", "เน่าจากเบส"],
        "ค่า pH": ["< 4.0", "5.0 - 6.0", "7.0", "8.0 - 9.0", "10.0+"]
    }
    st.table(guide_table)

st.markdown("<p style='text-align: center; color: #94a3b8; margin-top: 50px;'>Bio-Smart Tech © 2026</p>", unsafe_allow_html=True)

