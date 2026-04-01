import streamlit as st
import psycopg2
import pandas as pd
from datetime import date

st.set_page_config(page_title="Manage Matches", page_icon="📅")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📅 Manage Matches")

with st.form("add_match_form"):
    st.subheader("Add Match")
    match_name = st.text_input("Match Name")
    match_date = st.date_input("Match Date", value=date.today())
    location = st.text_input("Location")
    submitted = st.form_submit_button("Add Match")

    if submitted:
        errors = []

        if not match_name.strip():
            errors.append("Match name is required.")
        if not location.strip():
            errors.append("Location is required.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO matches10 (match_name, match_date, location) VALUES (%s, %s, %s);",
                    (match_name.strip(), match_date, location.strip())
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ {match_name} added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.subheader("Current Matches")

search = st.text_input("Search matches by name")

try:
    conn = get_connection()
    cur = conn.cursor()

    if search.strip():
        cur.execute(
            """
            SELECT id, match_name, match_date, location
            FROM matches10
            WHERE match_name ILIKE %s
            ORDER BY match_date;
            """,
            (f"%{search.strip()}%",)
        )
    else:
        cur.execute(
            """
            SELECT id, match_name, match_date, location
            FROM matches10
            ORDER BY match_date;
            """
        )

    matches = cur.fetchall()
    cur.close()
    conn.close()

    if matches:
        df = pd.DataFrame(matches, columns=["ID", "Match Name", "Match Date", "Location"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No matches found.")

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")
st.subheader("Edit Match")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, match_name FROM matches10 ORDER BY match_name;")
    match_rows = cur.fetchall()
    cur.close()
    conn.close()

    if match_rows:
        match_options = {row[1]: row[0] for row in match_rows}
        selected_match_name = st.selectbox("Select a match to edit", match_options.keys())
        selected_match_id = match_options[selected_match_name]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT match_name, match_date, location FROM matches10 WHERE id = %s;",
            (selected_match_id,)
        )
        match_data = cur.fetchone()
        cur.close()
        conn.close()

        with st.form("edit_match_form"):
            edit_match_name = st.text_input("Edit Match Name", value=match_data[0])
            edit_match_date = st.date_input("Edit Match Date", value=match_data[1])
            edit_location = st.text_input("Edit Location", value=match_data[2])
            update_submitted = st.form_submit_button("Update Match")

            if update_submitted:
                errors = []

                if not edit_match_name.strip():
                    errors.append("Match name is required.")
                if not edit_location.strip():
                    errors.append("Location is required.")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute(
                            """
                            UPDATE matches10
                            SET match_name = %s, match_date = %s, location = %s
                            WHERE id = %s;
                            """,
                            (edit_match_name.strip(), edit_match_date, edit_location.strip(), selected_match_id)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("✅ Match updated successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("No matches to edit yet.")

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")
st.subheader("Delete Match")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, match_name FROM matches10 ORDER BY match_name;")
    delete_rows = cur.fetchall()
    cur.close()
    conn.close()

    if delete_rows:
        delete_options = {row[1]: row[0] for row in delete_rows}
        delete_match_name = st.selectbox("Select a match to delete", delete_options.keys(), key="delete_match")
        delete_match_id = delete_options[delete_match_name]

        confirm_delete = st.checkbox("I confirm I want to delete this match.")
        if st.button("Delete Match"):
            if confirm_delete:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM matches10 WHERE id = %s;", (delete_match_id,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("✅ Match deleted successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please confirm deletion first.")
    else:
        st.info("No matches to delete yet.")

except Exception as e:
    st.error(f"Error: {e}")
