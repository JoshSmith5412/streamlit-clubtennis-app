import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Player Signups", page_icon="✅")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("✅ Player Match Signups")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM players10 ORDER BY name;")
    players = cur.fetchall()

    cur.execute("SELECT id, match_name FROM matches10 ORDER BY match_name;")
    matches = cur.fetchall()

    cur.close()
    conn.close()

    if not players:
        st.warning("No players found. Add players first.")
    elif not matches:
        st.warning("No matches found. Add matches first.")
    else:
        player_options = {p[1]: p[0] for p in players}
        match_options = {m[1]: m[0] for m in matches}

        with st.form("signup_form"):
            selected_player = st.selectbox("Select Player", player_options.keys())
            selected_match = st.selectbox("Select Match", match_options.keys())
            submitted = st.form_submit_button("Sign Up Player")

            if submitted:
                player_id = player_options[selected_player]
                match_id = match_options[selected_match]

                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO player_matches10 (player_id, match_id) VALUES (%s, %s);",
                        (player_id, match_id)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"✅ {selected_player} signed up for {selected_match}!")
                except psycopg2.errors.UniqueViolation:
                    st.error("That player is already signed up for that match.")
                except Exception as e:
                    st.error(f"Error: {e}")

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")
st.subheader("Current Signups")

search = st.text_input("Filter by player name")

try:
    conn = get_connection()
    cur = conn.cursor()

    if search.strip():
        cur.execute(
            """
            SELECT pm.id, p.name, m.match_name, m.match_date, m.location, pm.signup_date
            FROM player_matches10 pm
            JOIN players10 p ON pm.player_id = p.id
            JOIN matches10 m ON pm.match_id = m.id
            WHERE p.name ILIKE %s
            ORDER BY pm.signup_date DESC;
            """,
            (f"%{search.strip()}%",)
        )
    else:
        cur.execute(
            """
            SELECT pm.id, p.name, m.match_name, m.match_date, m.location, pm.signup_date
            FROM player_matches10 pm
            JOIN players10 p ON pm.player_id = p.id
            JOIN matches10 m ON pm.match_id = m.id
            ORDER BY pm.signup_date DESC;
            """
        )

    signups = cur.fetchall()
    cur.close()
    conn.close()

    if signups:
        df = pd.DataFrame(signups, columns=["Signup ID", "Player", "Match", "Match Date", "Location", "Signup Date"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No signups yet.")

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")
st.subheader("Delete Signup")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT pm.id, p.name, m.match_name
        FROM player_matches10 pm
        JOIN players10 p ON pm.player_id = p.id
        JOIN matches10 m ON pm.match_id = m.id
        ORDER BY p.name, m.match_name;
    """)
    signup_rows = cur.fetchall()
    cur.close()
    conn.close()

    if signup_rows:
        signup_options = {f"{row[1]} - {row[2]}": row[0] for row in signup_rows}
        selected_signup = st.selectbox("Select signup to delete", signup_options.keys())
        selected_signup_id = signup_options[selected_signup]

        confirm_delete = st.checkbox("I confirm I want to delete this signup.")
        if st.button("Delete Signup"):
            if confirm_delete:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM player_matches10 WHERE id = %s;", (selected_signup_id,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("✅ Signup deleted successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please confirm deletion first.")
    else:
        st.info("No signups to delete.")

except Exception as e:
    st.error(f"Error: {e}")
