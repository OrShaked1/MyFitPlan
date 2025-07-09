import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="🏠 דף הבית - MyFirstApp",
    layout="centered"
)

st.title("🏠 דף הבית")

today_str = datetime.today().strftime('%Y-%m-%d')

LOG_FILE = "food_log.csv"
GOALS_FILE = "goals_by_date.csv"

# יומן
if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
    daily_log = log_df[log_df["Date"] == today_str]
else:
    daily_log = pd.DataFrame()

# יעדים
if os.path.exists(GOALS_FILE):
    goals_df = pd.read_csv(GOALS_FILE)
    daily_goal = goals_df[goals_df["תאריך"] == today_str]
else:
    daily_goal = pd.DataFrame()

st.markdown(f"### 📅 היום: `{today_str}`")

if daily_log.empty:
    st.info("🙋‍♀️ עוד לא הוזנו פריטים ליומן היום.")
else:
    totals = daily_log[["Carb_units", "Protein_units", "Fat_units", "Calories"]].sum()

    if not daily_goal.empty:
        carb_goal = daily_goal['יעד פחמימה (יח\')'].values[0]
        protein_goal = daily_goal['יעד חלבון (יח\')'].values[0]
        fat_goal = daily_goal['יעד שומן (יח\')'].values[0]

        st.divider()
        st.markdown("### 🎯 מצב לפי רכיב")

        # חישוב אחוזים בבטיחות
        carb_pct = min(100, max(0, (totals['Carb_units'] / carb_goal) * 100)) if carb_goal > 0 else 0
        protein_pct = min(100, max(0, (totals['Protein_units'] / protein_goal) * 100)) if protein_goal > 0 else 0
        fat_pct = min(100, max(0, (totals['Fat_units'] / fat_goal) * 100)) if fat_goal > 0 else 0

        col1, col2, col3 = st.columns(1) if st.session_state.get('is_mobile') else st.columns(3)

        with col1:
            st.markdown("### 🥖 פחמימה")
            st.metric("בפועל", f"{totals['Carb_units']:.2f} יח׳", f"{totals['Carb_units'] - carb_goal:+.2f} יח׳")
            st.caption(f"🎯 יעד: {carb_goal:.2f} יח׳")
            st.progress(carb_pct / 100, text=f"{carb_pct:.0f}% מהיעד")

        with col2:
            st.markdown("### 🍗 חלבון")
            st.metric("בפועל", f"{totals['Protein_units']:.2f} יח׳", f"{totals['Protein_units'] - protein_goal:+.2f} יח׳")
            st.caption(f"🎯 יעד: {protein_goal:.2f} יח׳")
            st.progress(protein_pct / 100, text=f"{protein_pct:.0f}% מהיעד")

        with col3:
            st.markdown("### 🥑 שומן")
            st.metric("בפועל", f"{totals['Fat_units']:.2f} יח׳", f"{totals['Fat_units'] - fat_goal:+.2f} יח׳")
            st.caption(f"🎯 יעד: {fat_goal:.2f} יח׳")
            st.progress(fat_pct / 100, text=f"{fat_pct:.0f}% מהיעד")

        st.divider()
        st.subheader("🔥 סה\"כ קלוריות היום")
        st.info(f"{totals['Calories']:.0f} קק\"ל")

    else:
        st.warning("⚠️ לא הוגדר יעד עבור היום.")

