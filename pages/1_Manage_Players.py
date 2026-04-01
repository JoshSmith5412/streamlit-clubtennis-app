import streamlit as st
import psycopg2
import pandas as pd
import re

st.set_page_config(page_title="Manage Players", page_icon="👤")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("👤 Manage Players")

with st.form("add_player_form"):
    st.subheader("Add Player")
    name = st.text_input("Player Name")
    email = st.text_input("Player Email")
    skill_level = st.selectbox("Skill Level", ["A", "B", "C", "D"])
    submitted = st.form_submit_button("Add Player")

    if submitted:
        errors = []

        if not name.strip():
            errors.append("Name is required.")

        if not email.strip():
            errors.append("Email is required.")
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append("Enter a valid email address.")

        if not skill_level.strip():
            errors.append("Skill level is required.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO players10 (name, email, skill_level) VALUES (%s, %s, %s);",
                    (name.strip(), email.strip(), skill_level)
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ {name} added successfully!")
            except psycopg2.errors.UniqueViolation:
                st.error("A player with that email already exists.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.subheader("Current Players")

search = st.text_input("Search players by name")

try:
    conn = get_connection()
    cur = conn.cursor()

    if search.strip():
        cur.execute(
            """
            SELECT id, name, email, skill_level
            FROM players10
            WHERE name ILIKE %s
            ORDER BY name;
            """,
            (f"%{search.strip()}%",)
        )
    else:
        cur.execute(
            """
            SELECT id, name, email, skill_level
            FROM players10
            ORDER BY name;
            """
        )

    players = cur.fetchall()
    cur.close()
    conn.close()

    if players:
        df = pd.DataFrame(players, columns=["ID", "Name", "Email", "Skill Level"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No players found.")

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")
st.subheader("Edit Player")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM players10 ORDER BY name;")
    player_rows = cur.fetchall()
    cur.close()
    conn.close()

    if player_rows:
        player_options = {row[1]: row[0] for row in player_rows}
        selected_player_name = st.selectbox("Select a player to edit", player_options.keys())
        selected_player_id = player_options[selected_player_name]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT name, email, skill_level FROM players10 WHERE id = %s;",
            (selected_player_id,)
        )
        player_data = cur.fetchone()
        cur.close()
        conn.close()

        with st.form("edit_player_form"):
            edit_name = st.text_input("Edit Name", value=player_data[0])
            edit_email = st.text_input("Edit Email", value=player_data[1])
            edit_skill = st.selectbox("Edit Skill Level", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(player_data[2]))
            update_submitted = st.form_submit_button("Update Player")

            if update_submitted:
                errors = []

                if not edit_name.strip():
                    errors.append("Name is required.")

                if not edit_email.strip():
                    errors.append("Email is required.")
                else:
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, edit_email):
                        errors.append("Enter a valid email address.")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute(
                            """
                            UPDATE players10
                            SET name = %s, email = %s, skill_level = %s
                            WHERE id = %s;
                            """,
                            (edit_name.strip(), edit_email.strip(), edit_skill, selected_player_id)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("✅ Player updated successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("No players to edit yet.")

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")
st.subheader("Delete Player")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM players10 ORDER BY name;")
    delete_rows = cur.fetchall()
    cur.close()
    conn.close()

    if delete_rows:
        delete_options = {row[1]: row[0] for row in delete_rows}
        delete_player_name = st.selectbox("Select a player to delete", delete_options.keys(), key="delete_player")
        delete_player_id = delete_options[delete_player_name]

        confirm_delete = st.checkbox("I confirm I want to delete this player.")
        if st.button("Delete Player"):
            if confirm_delete:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM players10 WHERE id = %s;", (delete_player_id,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("✅ Player deleted successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please confirm deletion first.")
    else:
        st.info("No players to delete yet.")

except Exception as e:
    st.error(f"Error: {e}")
