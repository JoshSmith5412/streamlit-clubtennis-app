import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Club Tennis App", page_icon="🎾")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🎾 Club Tennis Management App")
st.write("Use the sidebar to manage players, matches, and signups.")

st.markdown("---")
st.subheader("Dashboard")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM players10;")
    player_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM matches10;")
    match_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM player_matches10;")
    signup_count = cur.fetchone()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Players", player_count)
    col2.metric("Matches", match_count)
    col3.metric("Signups", signup_count)

    st.markdown("---")
    st.subheader("Recent Signups")

    cur.execute("""
        SELECT p.name, p.email, p.skill_level, m.match_name, m.match_date, m.location, pm.signup_date
        FROM player_matches10 pm
        JOIN players10 p ON pm.player_id = p.id
        JOIN matches10 m ON pm.match_id = m.id
        ORDER BY pm.signup_date DESC;
    """)
    rows = cur.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=[
            "Player", "Email", "Skill Level", "Match", "Match Date", "Location", "Signup Date"
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No signups yet.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
