import pandas as pd
import numpy as np
import xmlrpc.client
import streamlit as st

# Df with 4 columns Project_id, Task_id, predecessor_id
def upload_file(df, username_email, password_input):
    url = "https://fenix.codesign.codes"
    db = "fenix-opportunities"
    username = username_email
    password = password_input

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))

    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    
    for idx, record in df.iterrows():
        print(idx)
        print(type(record["Predecessor"]))
        print(record["Predecessor"])
        if type(record["Predecessor"]) != float:
            predecessors_names = record["Predecessor"].split(',')
            print(predecessors_names)
            predecessors_id = df[df["Title"].isin(predecessors_names)]["ID"].to_list()
            print(predecessors_id)

            models.execute_kw(db, uid, password, 'project.task', 'write', [[int(record["ID"])], {"depend_on_ids": [(6, 0, predecessors_id)]}])

# --- Streamlit User Interface ---

# Set the page title and layout
st.set_page_config(layout="centered", page_title="Odoo Task Uploader")

# Main title
st.title("🔗 Odoo Task Predecessor Uploader")

st.info("This app updates task dependencies in Odoo from an Excel file.")

# --- Step 1: File Uploader ---
st.header("1. Upload Your Task File")
uploaded_file = st.file_uploader(
    "Your Excel file must contain the columns: 'ID', 'Title', and 'Predecessor'.",
    type="xlsx"
)

# --- Step 2: Odoo Credentials ---
st.header("2. Enter Odoo Credentials")
email = st.text_input("Odoo Username (Email)")
password = st.text_input("Odoo Password", type="password")

# --- Step 3: Run the Process ---
st.header("3. Run the Update")
if st.button("🚀 Start Update Process"):
    # Check if all inputs are provided
    if uploaded_file is not None and email and password:
        try:
            # Read the uploaded Excel file into a DataFrame
            tasks_df = pd.read_excel(uploaded_file)
            st.write("### File Preview:")
            st.dataframe(tasks_df.head())

            # Check for required columns
            required_cols = ["ID", "Title", "Predecessor"]
            if not all(col in tasks_df.columns for col in required_cols):
                st.error(f"Error: The Excel file must contain these columns: {', '.join(required_cols)}")
            else:
                # Execute the main function with UI feedback elements
                st.write("---")
                st.write("### Processing Log")
                progress_bar = st.progress(0)
                status_text = st.empty() # A placeholder for dynamic text
                upload_file(tasks_df, email, password)
                progress_bar = st.progress(100)

        except Exception as e:
            st.error(f"Failed to read or process the Excel file: {e}")
    else:
        st.warning("⚠️ Please upload a file and enter your credentials before running.")
