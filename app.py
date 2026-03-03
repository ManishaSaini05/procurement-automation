import streamlit as st
import pandas as pd
from pathlib import Path
from services.db import get_connection
from services.email_service import send_rfq_email

st.set_page_config(page_title="Procurement System", layout="wide")

# =========================
# SESSION INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = None

if "active_project_code" not in st.session_state:
    st.session_state.active_project_code = None


# =========================
# LOGIN PAGE
# =========================
def login_page():
    st.title("🔐 Procurement Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


# =========================
# PROJECT SELECTION
# =========================
def project_section():
    st.subheader("📂 Select Project from Design BOQ")

    boq_path = Path("data/Design_boq.xlsx")

    if not boq_path.exists():
        st.error("BOQ file not found in data folder.")
        st.stop()

    boq_df = pd.read_excel(boq_path)

    required_cols = [
        "Project_ID",
        "Project_Name",
        "Material_Name",
        "Specification",
        "BOQ_Quantity"
    ]

    for col in required_cols:
        if col not in boq_df.columns:
            st.error(f"Missing column in BOQ: {col}")
            st.stop()

    unique_projects = boq_df["Project_ID"].dropna().unique()

    selected_project_code = st.selectbox(
        "Select Project ID",
        unique_projects
    )

    if selected_project_code:

        conn = get_connection()
        cursor = conn.cursor()

        # Check if project exists
        cursor.execute(
            "SELECT * FROM projects WHERE project_code=?",
            (selected_project_code,)
        )
        existing = cursor.fetchone()

        if not existing:
            cursor.execute(
                """INSERT INTO projects 
                (project_code, project_name, client, location)
                VALUES (?, ?, ?, ?)""",
                (selected_project_code, selected_project_code, "", "")
            )
            conn.commit()

        # Fetch ID
        cursor.execute(
            "SELECT id FROM projects WHERE project_code=?",
            (selected_project_code,)
        )
        project_id = cursor.fetchone()["id"]

        conn.close()

        st.session_state.active_project_id = project_id
        st.session_state.active_project_code = selected_project_code

        st.success(f"Project {selected_project_code} Ready for Procurement")


# =========================
# MATERIAL SECTION
# =========================
def material_section():

    if not st.session_state.active_project_id:
        st.warning("Please select project first.")
        return

    st.subheader("📐 Materials From BOQ")

    boq_path = Path("data/Design_boq.xlsx")
    boq_df = pd.read_excel(boq_path)

    project_materials = boq_df[
        boq_df["Project_ID"] == st.session_state.active_project_code
    ]

    if project_materials.empty:
        st.info("No materials found for this project.")
        return

    material_names = project_materials["Material_Name"].unique()

    selected_material = st.selectbox(
        "Select Material",
        material_names
    )

    if selected_material:

        material_row = project_materials[
            project_materials["Material_Name"] == selected_material
        ].iloc[0]

        st.markdown("### 📊 Past Vendor History")

        vendor_path = Path("data/past_vendor_data.xlsx")

        if not vendor_path.exists():
            st.warning("Past vendor data file not found.")
            return

        vendor_df = pd.read_excel(vendor_path)
        vendor_df.columns = vendor_df.columns.str.strip()

        required_cols = [
            "Material_Name",
            "Vendor_Name",
            "Project_ID",
            "Unit_Price",
            "Quantity",
            "Email"
        ]

        for col in required_cols:
            if col not in vendor_df.columns:
                st.error(f"Missing column in vendor sheet: {col}")
                return

        # Clean matching
        def clean_text(text):
            return str(text).strip().lower()

        selected_material_clean = clean_text(selected_material)
        vendor_df["Material_Name"] = vendor_df["Material_Name"].apply(clean_text)

        filtered_vendors = vendor_df[
            vendor_df["Material_Name"] == selected_material_clean
        ]

        if filtered_vendors.empty:
            st.warning("No past vendor history found for this material.")
            return

        #filtered_vendors = filtered_vendors.drop_duplicates()

        #.success("Past vendor history found.")
        #st.dataframe(filtered_vendors, use_container_width=True)

        # ✅ CORRECT Vendor Selection
        # Add selection column
        filtered_vendors["Select"] = False

        edited_df = st.data_editor(
            filtered_vendors,
            use_container_width=True,
            num_rows="fixed"
        )

        if st.button("Send RFQ"):

            selected_rows = edited_df[edited_df["Select"] == True]

            if selected_rows.empty:
                st.warning("Please select at least one vendor.")
                return

            conn = get_connection()
            cursor = conn.cursor()

            for _, row in selected_rows.iterrows():

                vendor_name = row["Vendor_Name"]
                vendor_email = row["Email"]

        # 1️⃣ Send Email
                email_sent = send_rfq_email(
                    vendor_email,
                    vendor_name,
                    st.session_state.active_project_code,
                    selected_material,
                    material_row["BOQ_Quantity"]
                )

                if email_sent:
                    st.success(f"RFQ sent to {vendor_name}")
                else:
                    st.error(f"Failed to send email to {vendor_name}")

        # 2️⃣ Save RFQ entry in SQLite
                cursor.execute("""
                   INSERT INTO rfq_master (
                        project_id,
                        material_name,
                        rfq_date,
                        status
                    )
                    VALUES (?, ?, datetime('now'), ?)
                """, (st.session_state.active_project_id,selected_material_clean,"sent"))
                # Save Vendor under RFQ
                rfq_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO rfq_vendors (
                        rfq_id,
                        vendor_name,
                        vendor_email,
                        status
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    rfq_id,
                    vendor_name,
                    vendor_email,
                    "RFQ Sent"
                ))
            conn.commit()
            conn.close()

            st.success("RFQ process completed.")


# =========================
# DASHBOARD
# =========================
def dashboard():
    st.title("📦 Procurement Dashboard")

    menu = st.sidebar.radio(
        "Navigation",
        ["Projects", "Materials"]
    )

    if menu == "Projects":
        project_section()

    elif menu == "Materials":
        material_section()


# =========================
# APP FLOW
# =========================
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()