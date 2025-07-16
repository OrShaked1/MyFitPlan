import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import os

st.set_page_config(page_title="📅 ניהול יעדים")

st.header("📅 הגדרת יעדים לפי תאריכים")

# פרטי חיבור ל-Supabase
SUPABASE_HOST = "db.ifykewhyhxkyffvnfblm.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_PORT = 5432

# יצירת חיבור
conn = psycopg2.connect(
    host=SUPABASE_HOST,
    database=SUPABASE_DB,
    user=SUPABASE_USER,
    password=SUPABASE_PASSWORD,
    port=SUPABASE_PORT
)
cur = conn.cursor()

# קריאת טבלת היעדים
goals_df = pd.read_sql("SELECT * FROM goals_by_date ORDER BY date;", conn)

# טופס הוספה/עדכון יעד
with st.form("date_goals_form"):
    goal_date = st.date_input("בחרי תאריך:", datetime.today())
    carb_goal = st.number_input("יעד פחמימה (יח')", min_value=0.0, step=0.5)
    protein_goal = st.number_input("יעד חלבון (יח')", min_value=0.0, step=0.5)
    fat_goal = st.number_input("יעד שומן (יח')", min_value=0.0, step=0.5)
    save_goal = st.form_submit_button("💾 שמור יעד")

    if save_goal:
        date_str = goal_date.strftime('%Y-%m-%d')
        if date_str in goals_df["date"].values:
            update_query = """
                UPDATE goals_by_date
                SET carb_goal = %s, protein_goal = %s, fat_goal = %s
                WHERE date = %s;
            """
            cur.execute(update_query, (carb_goal, protein_goal, fat_goal, date_str))
            conn.commit()
            st.success(f"✅ יעד עודכן עבור {date_str}")
        else:
            insert_query = """
                INSERT INTO goals_by_date (date, carb_goal, protein_goal, fat_goal)
                VALUES (%s, %s, %s, %s);
            """
            cur.execute(insert_query, (date_str, carb_goal, protein_goal, fat_goal))
            conn.commit()
            st.success(f"✅ יעד נוסף עבור {date_str}")

        st.experimental_rerun()

# טבלת יעדים קיימים
st.subheader("📋 טבלת היעדים הקיימת")
if goals_df.empty:
    st.info("⚠️ אין יעדים מוגדרים עדיין.")
else:
    st.dataframe(goals_df, use_container_width=True)

cur.close()
conn.close()
