import streamlit as st

import streamlit as st
import pandas as pd
import joblib
import numpy as np
from utils.weather import get_weather_features
st.set_page_config(page_title="Agri AI System", layout="wide")
st.markdown("""
<style>
/* Make page full height */
html, body, .stApp {
    height: 100%;
}

/* Push footer to bottom */
.main {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

/* Footer styling */
.footer {
    margin-top: auto;
    padding: 20px;
    text-align: center;
    font-size: 14px;
    color: #aaa;
    border-top: 1px solid #444;
}

/* Tabs spacing */
.footer-tabs {
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)
# =========================
# CONFIG
# =========================
#st.set_page_config(page_title="Agri AI System", layout="wide")

# =========================
# LOAD MODELS
# =========================
yield_model = joblib.load("models/yield_model.pkl")
price_model = joblib.load("models/price_model.pkl")

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("data/crop_data.csv")
df.columns = df.columns.str.strip()

# =========================
# TITLE
# =========================
st.title("🌾 Smart Agriculture AI System")

# =========================
# SIDEBAR MENU
# =========================
menu = st.sidebar.radio("Navigation", ["Prediction", "Suggest My Crop", "Insights"])
with st.sidebar:

    st.title("🌾 Agri AI Guide")

    # =========================
    # SYSTEM INFO
    # =========================
    st.subheader("📊 System Facts")
    st.write("""
    - Uses Machine Learning models  
    - Based on Indian agriculture data  
    - Combines Yield + Price + Weather  
    - Helps in smart crop selection  
    """)

    # =========================
    # RISK LEVELS (UPDATED LOGIC)
    # =========================
    st.subheader("⚠️ Risk Levels")

    st.write("""
    🔴 Risky (Score < 0.4)  
    - Low yield OR poor price  
    - Not recommended  

    🟡 Moderate (0.4 – 0.7)  
    - Average performance  
    - Acceptable but not ideal  

    🟢 Good (0.7 – 0.85)  
    - Balanced yield & price  

    🔥 Excellent (> 0.85)  
    - High profit potential  
    """)

    # =========================
    # OUTPUT EXPLANATION
    # =========================
    st.subheader("📈 Output Meaning")

    st.write("""
    🌱 Production → Total crop output (tonnes)  

    🌾 Yield → Production per hectare (t/ha)  

    💰 Price → Market price (₹ per quintal)  

    📊 Score → Combined performance index  
    """)

    # =========================
    # EXTRA INSIGHT (🔥 PRO TOUCH)
    # =========================
    st.subheader("🧠 Smart Insight")

    st.write("""
    - High yield ≠ high profit always  
    - Market price plays a major role  
    - Weather impacts long-term output  
    - Always compare multiple crops  
    """)
with st.sidebar:
    st.subheader("📊 System Info")
    st.write("""
    - ML based crop prediction  
    - Uses weather + price + yield  
    - Works on Indian dataset  
    """)

# =========================
# PREDICTION PAGE
# =========================
if menu == "Prediction":

    st.header("🌱 Smart Crop Prediction")

    col1, col2 = st.columns(2)

    with col1:
        state = st.selectbox("State", df['State'].unique())
        district = st.selectbox("District", df[df['State'] == state]['District'].unique())
        valid_crops = df[df['District'] == district]['Crop'].unique()
        all_crops = df['Crop'].unique()

        crop = st.selectbox("Crop", all_crops)

    with col2:
        season = st.selectbox("Season", df['Season'].unique())
        area = st.number_input("Area (hectare)", value=1000.0)
        year = st.number_input("Year", value=2025)

    # LOCATION FIX
    district_to_city = {
        "RAMPUR": "Rampur,IN",
        "AGRA": "Agra,IN",
        "LUCKNOW": "Lucknow,IN"
    }

    default_city = district_to_city.get(district.upper(), "Agra,IN")
    city = st.text_input("📍 Location", value=default_city)

    # =========================
    # BUTTON
    # =========================
    if st.button("🚀 Predict Smart Result"):

        # WEATHER
        temp, rainfall = get_weather_features(city)

        if temp is None:
            temp, rainfall = 25, 1000
            st.warning("⚠️ Invalid location, using default weather")

        st.info(f"🌡 Temp: {temp:.2f} °C | 🌧 Rainfall: {rainfall:.2f}")
# YIELD MODEL
# =========================
        yield_input = pd.DataFrame({
            'State': [state],
            'District': [district],
            'Crop': [crop],
            'Season': [season],
            'Crop_Year': [year],
            'Area': [area]
        })

        # Predict Yield (per hectare)
        yield_value = yield_model.predict(yield_input)[0]

        # Safety Check
        if np.isnan(yield_value) or yield_value <= 0:
            st.error("⚠️ Invalid prediction. Try another crop.")
            st.stop()

        # Calculate Production
        production = yield_value * area
        # =========================
        # PRICE MODEL
        # =========================
        month = 6
        season_code = month % 12 // 3

        price_input = pd.DataFrame({
            'Crop': [crop],
            'District': [district],
            'Month': [month],
            'Season': [season_code]
        })

        price_pred = price_model.predict(price_input)[0]

        # =========================
        # RESULTS
        # =========================
        st.subheader("📊 Results")

        c1, c2, c3 = st.columns(3)

        c1.metric("🌱 Production", f"{production:.0f}")
        c2.metric("🌾 Yield", f"{yield_value:.2f}")
        c3.metric("💰 Price (₹/Quintal)", f"{price_pred:.0f}")

        # =========================
        # AI LOGIC
        # =========================
 #       score = (yield_value * 0.6) + (price_pred * 0.4)
        yield_norm = yield_value / 10
        price_norm = price_pred / 8000

        score = (yield_norm * 0.6) + (price_norm * 0.4)

        st.subheader("🧠 AI Recommendation")
        if score > 0.7:
            st.success("🔥 Excellent Choice")
        elif score > 0.4:
            st.warning("⚡ Moderate Choice")
        else:
            st.error("⚠️ Risky Selection")
            st.write(f"""
        📊 Analysis:
        - Yield Score: {yield_norm:.2f}
        - Price Score: {price_norm:.2f}
        - Final Score: {score:.2f}
        """)
        st.write("""
        📌 Explanation:
        - Production = total output (tonnes)
        - Yield = per hectare productivity
        - Low yield may indicate poor conditions or crop mismatch
        """)


# =========================
# 🤖 AUTO CROP SUGGESTION
# =========================
elif menu == "Suggest My Crop":

    st.header("🤖 AI Crop Recommendation")

    state = st.selectbox("State", df['State'].unique())
    district = st.selectbox("District", df[df['State']==state]['District'].unique())
    season = st.selectbox("Season", df['Season'].unique())

    area = st.number_input("Area", value=1000.0)
    year = st.number_input("Year", value=2025)

    city = st.text_input("📍 Location", district)

    if st.button("🚀 Suggest Best Crops"):

        temp, rainfall = get_weather_features(city)

        crops = df['Crop'].unique()
        results = []

        for crop in crops:
            try:
                yield_input = pd.DataFrame({
                    'State': [state],
                    'District': [district],
                    'Crop': [crop],
                    'Season': [season],
                    'Crop_Year': [year],
                    'Area': [area]
                })

                # ✅ Correct prediction (NO expm1)
                yield_val = yield_model.predict(yield_input)[0]

                # Safety check
                if np.isnan(yield_val) or yield_val <= 0:
                    continue

                # ✅ Correct production
                production = yield_val * area

                # =========================
                # PRICE MODEL
                # =========================
                price_input = pd.DataFrame({
                    'Crop': [crop],
                    'District': [district],
                    'Month': [6],
                    'Season': [2]
                })

                price_val = price_model.predict(price_input)[0]

                # =========================
                # NORMALIZATION (IMPORTANT)
                # =========================
                yield_norm = yield_val / 10      # adjust based on your data
                price_norm = price_val / 5000    # adjust based on price range

                # FINAL SCORE
                score = (yield_norm * 0.6) + (price_norm * 0.4)

                results.append([crop, yield_val, price_val, score])

            except:
                continue

        results_df = pd.DataFrame(results, columns=["Crop", "Yield", "Price", "Score"])
        results_df = results_df.sort_values(by="Score", ascending=False)

        st.subheader("🏆 Top 3 Crops")

        for i in range(3):
            row = results_df.iloc[i]
            st.success(f"{i+1}. {row['Crop']} → Score: {row['Score']:.0f}")


# =========================
# INSIGHTS
# =========================
else:
    st.header("📈 Insights")

    st.bar_chart(df['Crop'].value_counts().head(10))


st.markdown('<div class="footer">', unsafe_allow_html=True)

st.markdown("### 📚 System Documentation")

tab1, tab2, tab3, tab4 = st.tabs([
    "📘 How to Use",
    "🌱 Yield Model",
    "💰 Price Model",
    "🌦 Weather Model"
])

with tab1:
    st.write("""
    This system helps users make smart agricultural decisions using AI models.

    - Select location and crop details  
    - Enter area and year  
    - System predicts yield and price  
    - AI suggests best decision  

    It is designed for farmers, students, and researchers.
    """)

with tab2:
    st.write("""
    Yield Model predicts production based on:
    - State, District, Crop
    - Season, Year, Area

    Uses Machine Learning (XGBoost)

    Helps estimate:
    - Total production
    - Yield per hectare
    """)

with tab3:
    st.write("""
    Price Model predicts market price.

    Uses:
    - Crop
    - District
    - Season & Month

    Based on mandi data.

    Helps estimate profit potential.
    """)

with tab4:
    st.write("""
    Weather system uses OpenWeather API.

    Provides:
    - Temperature
    - Rainfall estimation

    Helps in climate-based decision making.
    """)

st.markdown("""
---
© 2026 Smart Agriculture AI System | Built with ❤️ using Machine Learning
""")

st.markdown('</div>', unsafe_allow_html=True)
# st.write("API KEY:", API_KEY)