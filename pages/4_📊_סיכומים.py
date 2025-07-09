import streamlit as st
import pandas as pd
import os
from datetime import datetime
import altair as alt

st.set_page_config(page_title="📊 סיכומים")

st.header("📊 סיכום והשוואה ליעדים")

LOG_FILE = "food_log.csv"
GOALS_FILE = "goals_by_date.csv"

# טען יומן
if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
else:
    st.warning("⚠️ אין יומן אכילה.")
    st.stop()

# טען יעדים
if os.path.exists(GOALS_FILE):
    goals_df = pd.read_csv(GOALS_FILE)
else:
    st.warning("⚠️ לא הוגדרו יעדים.")
    st.stop()

# בחר תאריך
selected_date = st.date_input("בחרי תאריך לסיכום:", datetime.today())
date_str = selected_date.strftime('%Y-%m-%d')

daily_log = log_df[log_df["Date"] == date_str]
daily_goal = goals_df[goals_df["תאריך"] == date_str]

if daily_log.empty:
    st.info("🙋‍♀️ אין רשומות ביומן לתאריך זה.")
else:
    st.subheader(f"📅 סיכום עבור {date_str}")

    st.dataframe(daily_log[["Food", "Grams", "Carb_units", "Protein_units", "Fat_units", "Calories"]])

    totals = daily_log[["Carb_units", "Protein_units", "Fat_units", "Calories"]].sum()

    if not daily_goal.empty:
        carb_goal = daily_goal["יעד פחמימה (יח')"].values[0]
        protein_goal = daily_goal["יעד חלבון (יח')"].values[0]
        fat_goal = daily_goal["יעד שומן (יח')"].values[0]

        # אחוזים
        carb_pct = min(100, max(0, (totals['Carb_units'] / carb_goal) * 100)) if carb_goal > 0 else 0
        protein_pct = min(100, max(0, (totals['Protein_units'] / protein_goal) * 100)) if protein_goal > 0 else 0
        fat_pct = min(100, max(0, (totals['Fat_units'] / fat_goal) * 100)) if fat_goal > 0 else 0

        st.divider()
        st.markdown("### 🎯 השוואה ליעדים")

        col1, col2, col3 = st.columns(1) if st.session_state.get('is_mobile') else st.columns(3)

        with col1:
            st.metric("🥖 פחמימה", f"{totals['Carb_units']:.2f} יח׳", f"{totals['Carb_units'] - carb_goal:+.2f} יח׳")
            st.progress(carb_pct / 100, text=f"{carb_pct:.0f}% מהיעד")

        with col2:
            st.metric("🍗 חלבון", f"{totals['Protein_units']:.2f} יח׳", f"{totals['Protein_units'] - protein_goal:+.2f} יח׳")
            st.progress(protein_pct / 100, text=f"{protein_pct:.0f}% מהיעד")

        with col3:
            st.metric("🥑 שומן", f"{totals['Fat_units']:.2f} יח׳", f"{totals['Fat_units'] - fat_goal:+.2f} יח׳")
            st.progress(fat_pct / 100, text=f"{fat_pct:.0f}% מהיעד")

        st.info(f"🔥 סה\"כ קלוריות: {totals['Calories']:.0f} קק\"ל")

        # גרף השוואה
        st.divider()
        st.markdown("### 📊 גרף השוואת יעד מול בפועל")

        chart_df = pd.DataFrame({
            "רכיב": ["פחמימה", "חלבון", "שומן"],
            "בפועל": [totals['Carb_units'], totals['Protein_units'], totals['Fat_units']],
            "יעד": [carb_goal, protein_goal, fat_goal]
        })

        chart_df_melted = chart_df.melt("רכיב", var_name="סוג", value_name="יחידות")

        # גרף עם ערכים ברורים
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
