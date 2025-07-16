import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import altair as alt
import os

st.set_page_config(page_title="📊 סיכומים")

# 🗂️ הגדרות חיבור
SUPABASE_HOST = "db.ifykewhyhxkyffvnfblm.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_PORT = 5432

conn = psycopg2.connect(
    host=SUPABASE_HOST,
    database=SUPABASE_DB,
    user=SUPABASE_USER,
    password=SUPABASE_PASSWORD,
    port=SUPABASE_PORT
)
cur = conn.cursor()

st.header("📊 סיכום והשוואה ליעדים")

# 🗂️ רענון יומן: עדכון ערכים לפי מאגר המזון
def recalculate_food_log():
    food_db = pd.read_sql("SELECT * FROM food_db;", conn)
    food_log = pd.read_sql("SELECT * FROM food_log;", conn)

    for index, row in food_log.iterrows():
        food_name = row["food"]
        grams = row["grams"]
        food_row = food_db[food_db["food"] == food_name]

        if not food_row.empty:
            carb = food_row["carb_per_100g"].values[0] * grams / 100 / 20
            protein = food_row["protein_per_100g"].values[0] * grams / 100 / 25
            fat = food_row["fat_per_100g"].values[0] * grams / 100 / 10
            cal = food_row["calories_per_100g"].values[0] * grams / 100

            update_query = """
                UPDATE food_log
                SET carb_units = %s,
                    protein_units = %s,
                    fat_units = %s,
                    calories = %s
                WHERE id = %s;
            """
            cur.execute(update_query, (carb, protein, fat, cal, row['id']))

    conn.commit()

# 📌 בחירת תאריך לסיכום
selected_date = st.date_input("בחרי תאריך לסיכום:", datetime.today())
date_str = selected_date.strftime('%Y-%m-%d')

daily_log = pd.read_sql(f"SELECT * FROM food_log WHERE date = '{date_str}';", conn)
daily_goal = pd.read_sql(f"SELECT * FROM goals_by_date WHERE date = '{date_str}';", conn)

if daily_log.empty:
    st.info("🙋‍♀️ אין רשומות ביומן לתאריך זה.")
else:
    st.subheader(f"📅 סיכום עבור {date_str}")

    st.dataframe(
        daily_log[["food", "grams", "carb_units", "protein_units", "fat_units", "calories"]],
        use_container_width=True
    )

    totals = daily_log[["carb_units", "protein_units", "fat_units", "calories"]].sum()

    if not daily_goal.empty:
        carb_goal = daily_goal["carb_goal"].values[0]
        protein_goal = daily_goal["protein_goal"].values[0]
        fat_goal = daily_goal["fat_goal"].values[0]

        # ✅ כפתור רענון
        if st.button("🔄 רענון כל הערכים ביומן"):
            recalculate_food_log()
            st.success("✨ כל הערכים עודכנו מחדש לפי המאגר!")
            st.experimental_rerun()

        # אחוזים
        carb_pct = min(100, max(0, (totals['carb_units'] / carb_goal) * 100)) if carb_goal > 0 else 0
        protein_pct = min(100, max(0, (totals['protein_units'] / protein_goal) * 100)) if protein_goal > 0 else 0
        fat_pct = min(100, max(0, (totals['fat_units'] / fat_goal) * 100)) if fat_goal > 0 else 0

        st.divider()
        st.markdown("### 🎯 השוואה ליעדים")

        col1, col2, col3 = st.columns(1) if st.session_state.get('is_mobile') else st.columns(3)

        with col1:
            st.metric("🥖 פחמימה", f"{totals['carb_units']:.2f} יח׳", f"{totals['carb_units'] - carb_goal:+.2f} יח׳")
            st.progress(carb_pct / 100, text=f"{carb_pct:.0f}% מהיעד")

        with col2:
            st.metric("🍗 חלבון", f"{totals['protein_units']:.2f} יח׳", f"{totals['protein_units'] - protein_goal:+.2f} יח׳")
            st.progress(protein_pct / 100, text=f"{protein_pct:.0f}% מהיעד")

        with col3:
            st.metric("🥑 שומן", f"{totals['fat_units']:.2f} יח׳", f"{totals['fat_units'] - fat_goal:+.2f} יח׳")
            st.progress(fat_pct / 100, text=f"{fat_pct:.0f}% מהיעד")

        st.info(f"🔥 סה\"כ קלוריות: {totals['calories']:.0f} קק\"ל")

        # גרף
        st.divider()
        st.markdown("### 📊 גרף השוואת יעד מול בפועל")

        chart_df = pd.DataFrame({
            "רכיב": ["פחמימה", "חלבון", "שומן"],
            "בפועל": [totals['carb_units'], totals['protein_units'], totals['fat_units']],
            "יעד": [carb_goal, protein_goal, fat_goal]
        })

        chart_df_melted = chart_df.melt("רכיב", var_name="סוג", value_name="יחידות")

        bars = alt.Chart(chart_df_melted).mark_bar().encode(
            x=alt.X('רכיב:N', title="רכיב תזונתי"),
            y=alt.Y('יחידות:Q', title="יחידות"),
            color='סוג:N',
            xOffset='סוג:N'
        )

        text = alt.Chart(chart_df_melted).mark_text(
            dy=-10, size=14
        ).encode(
            x='רכיב:N',
            y='יחידות:Q',
            detail='סוג:N',
            xOffset='סוג:N',
            text=alt.Text('יחידות:Q', format='.1f')
        )

        chart = (bars + text).properties(
            width=600,
            height=400
        )

        st.altair_chart(chart, use_container_width=True)

    else:
        st.warning("⚠️ לא הוגדר יעד עבור תאריך זה.")

cur.close()
conn.close()
