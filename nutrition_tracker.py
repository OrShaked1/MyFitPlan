import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import os

st.set_page_config(
    page_title="🏠 דף הבית - MyFirstApp",
    layout="centered"
)

st.title("🏠 דף הבית")

# פרטי חיבור מה-Environment (אל תכתבי סיסמה ישירות בקוד!)
SUPABASE_HOST = st.secrets["SUPABASE_HOST"]
SUPABASE_DB = st.secrets["SUPABASE_DB"]
SUPABASE_USER = st.secrets["SUPABASE_USER"]
SUPABASE_PASSWORD = st.secrets["SUPABASE_PASSWORD"]
SUPABASE_PORT = int(st.secrets["SUPABASE_PORT"])



st.write("HOST:", SUPABASE_HOST)
st.write("USER:", SUPABASE_USER)
st.write("PASSWORD IS NONE?", SUPABASE_PASSWORD is None)
st.write(f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}")


# יצירת חיבור
conn = psycopg2.connect(
    host=SUPABASE_HOST,
    database=SUPABASE_DB,
    user=SUPABASE_USER,
    password=SUPABASE_PASSWORD,
    port=SUPABASE_PORT
)

today_str = datetime.today().strftime('%Y-%m-%d')

# קריאה מהיומן
log_query = f"SELECT * FROM food_log WHERE date = '{today_str}';"
log_df = pd.read_sql(log_query, conn)

# קריאה מהיעדים
goals_query = f"SELECT * FROM goals_by_date WHERE date = '{today_str}';"
goals_df = pd.read_sql(goals_query, conn)

conn.close()

st.markdown(f"### 📅 היום: `{today_str}`")

if log_df.empty:
    st.info("🙋‍♀️ עוד לא הוזנו פריטים ליומן היום.")
else:
    totals = log_df[["carb_units", "protein_units", "fat_units", "calories"]].sum()

    if not goals_df.empty:
        carb_goal = goals_df['carb_goal'].values[0]
        protein_goal = goals_df['protein_goal'].values[0]
        fat_goal = goals_df['fat_goal'].values[0]

        st.divider()
        st.markdown("### 🎯 מצב לפי רכיב")

        carb_pct = min(100, max(0, (totals['carb_units'] / carb_goal) * 100)) if carb_goal > 0 else 0
        protein_pct = min(100, max(0, (totals['protein_units'] / protein_goal) * 100)) if protein_goal > 0 else 0
        fat_pct = min(100, max(0, (totals['fat_units'] / fat_goal) * 100)) if fat_goal > 0 else 0

        col1, col2, col3 = st.columns(1) if st.session_state.get('is_mobile') else st.columns(3)

        with col1:
            st.markdown("### 🥖 פחמימה")
            st.metric("בפועל", f"{totals['carb_units']:.2f} יח׳", f"{totals['carb_units'] - carb_goal:+.2f} יח׳")
            st.caption(f"🎯 יעד: {carb_goal:.2f} יח׳")
            st.progress(carb_pct / 100, text=f"{carb_pct:.0f}% מהיעד")

        with col2:
            st.markdown("### 🍗 חלבון")
            st.metric("בפועל", f"{totals['protein_units']:.2f} יח׳", f"{totals['protein_units'] - protein_goal:+.2f} יח׳")
            st.caption(f"🎯 יעד: {protein_goal:.2f} יח׳")
            st.progress(protein_pct / 100, text=f"{protein_pct:.0f}% מהיעד")

        with col3:
            st.markdown("### 🥑 שומן")
            st.metric("בפועל", f"{totals['fat_units']:.2f} יח׳", f"{totals['fat_units'] - fat_goal:+.2f} יח׳")
            st.caption(f"🎯 יעד: {fat_goal:.2f} יח׳")
            st.progress(fat_pct / 100, text=f"{fat_pct:.0f}% מהיעד")

        st.divider()
        st.subheader("🔥 סה\"כ קלוריות היום")
        st.info(f"{totals['calories']:.0f} קק\"ל")

    else:
        st.warning("⚠️ לא הוגדר יעד עבור היום.")
