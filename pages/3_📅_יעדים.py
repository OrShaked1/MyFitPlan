import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="📅 ניהול יעדים")

st.header("📅 הגדרת יעדים לפי תאריכים")

GOALS_FILE = "goals_by_date.csv"

# קובץ יעד
if os.path.exists(GOALS_FILE):
    goals_df = pd.read_csv(GOALS_FILE)
else:
    goals_df = pd.DataFrame(columns=["תאריך", "יעד פחמימה (יח')", "יעד חלבון (יח')", "יעד שומן (יח')"])
    goals_df.to_csv(GOALS_FILE, index=False)

# טופס הוספה/עדכון יעד
with st.form("date_goals_form"):
    goal_date = st.date_input("בחרי תאריך:", datetime.today())
    carb_goal = st.number_input("יעד פחמימה (יח')", min_value=0.0, step=0.5)
    protein_goal = st.number_input("יעד חלבון (יח')", min_value=0.0, step=0.5)
    fat_goal = st.number_input("יעד שומן (יח')", min_value=0.0, step=0.5)
    save_goal = st.form_submit_button("💾 שמור יעד")

    if save_goal:
        date_str = goal_date.strftime('%Y-%m-%d')
        if date_str in goals_df["תאריך"].values:
            goals_df.loc[goals_df["תאריך"] == date_str,
                         ["יעד פחמימה (יח')", "יעד חלבון (יח')", "יעד שומן (יח')"]] = [carb_goal, protein_goal, fat_goal]
            st.success(f"✅ יעד עודכן עבור {date_str}")
        else:
            new_row = pd.DataFrame([[date_str, carb_goal, protein_goal, fat_goal]], columns=goals_df.columns)
            goals_df = pd.concat([goals_df, new_row], ignore_index=True)
            st.success(f"✅ יעד נוסף עבור {date_str}")
        goals_df.to_csv(GOALS_FILE, index=False)

# טבלת יעדים קיימים
st.subheader("📋 טבלת היעדים הקיימת")
st.dataframe(goals_df)
