import streamlit as st
import requests

# Backend API URL
API_URL = "http://127.0.0.1:5000"

# Helper Functions
def fetch_data(endpoint):
    """Fetch data from a specified endpoint."""
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return []

def post_data(endpoint, payload):
    """Post data to a specified endpoint."""
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=payload)
        if response.status_code == 200:
            st.success("Operation successful!")
            return response.json()
        else:
            st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")

def put_data(endpoint, payload):
    """Put (update) data to a specified endpoint."""
    try:
        response = requests.put(f"{API_URL}/{endpoint}", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")

def delete_data(endpoint):
    """Delete data from a specified endpoint."""
    try:
        response = requests.delete(f"{API_URL}/{endpoint}")
        if response.status_code == 200:
            st.success("Deleted successfully!")
        else:
            st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")

# Main App Layout
st.title("University Research Grant Allocation System (URGAS)")

# Navigation Menu
menu = st.sidebar.selectbox("Navigation", ["Professors", "Projects", "Grants", "Funding Agencies", "Views", "Project Audit Log"])

if menu == "Professors":
    st.header("Manage Professors")

    # Fetch and display professors
    professors = fetch_data("professors")
    st.subheader("Existing Professors")
    if professors:
        st.table(professors)
    else:
        st.write("No professors found.")

    # Add a new professor
    with st.form("Add Professor"):
        st.subheader("Add a New Professor")
        name = st.text_input("Name")
        department = st.text_input("Department")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Add Professor")
        if submitted:
            if name and department and email:
                post_data("professors", {"name": name, "department": department, "email": email})
            else:
                st.error("All fields are required to add a professor.")

    # Update professor details
    with st.form("Update Professor"):
        st.subheader("Update a Professor")
        professor_id = st.number_input("Professor ID to Update", min_value=1, step=1)
        updated_name = st.text_input("Updated Name")
        updated_department = st.text_input("Updated Department")
        updated_email = st.text_input("Updated Email")
        update_submitted = st.form_submit_button("Update Professor")
        if update_submitted:
            payload = {}
            if updated_name:
                payload["name"] = updated_name
            if updated_department:
                payload["department"] = updated_department
            if updated_email:
                payload["email"] = updated_email
            if payload:
                put_data(f"professors/{professor_id}", payload)
            else:
                st.error("At least one field must be filled to update a professor.")

    # Delete a professor
    st.subheader("Delete a Professor")
    professor_id_to_delete = st.number_input("Professor ID to Delete", min_value=1, step=1)
    if st.button("Delete Professor"):
        if professor_id_to_delete:
            delete_data(f"professors/{professor_id_to_delete}")
        else:
            st.error("Please provide a valid Professor ID to delete.")

     # Associate a professor with a project
    st.subheader("Associate Professor with Project")
    professor_id = st.number_input("Professor ID", min_value=1, step=1)
    project_id = st.number_input("Project ID", min_value=1, step=1)
    if st.button("Assign Professor to Project"):
        if professor_id and project_id:
            post_data("assign_professor_to_project", {"professor_id": professor_id, "project_id": project_id})
        else:
            st.error("Both Professor ID and Project ID are required.")

    # View Publications by a Professor
    st.subheader("View Publications by a Professor")
    professor_id_for_publications = st.number_input("Enter Professor ID for Publications", min_value=1, step=1)
    if st.button("Get Publications"):
        professor_publications = fetch_data(f"professor_publications/{professor_id_for_publications}")
        if professor_publications:
            st.table(professor_publications)
        else:
            st.write("No publications found for this professor.")

elif menu == "Projects":
    st.header("Manage Projects")

    # Fetch and display projects
    projects = fetch_data("projects")
    st.subheader("Existing Projects")
    if projects:
        st.table(projects)
    else:
        st.write("No projects found.")

    # Add a new project
    with st.form("Add Project"):
        st.subheader("Add a New Project")
        title = st.text_input("Title")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        submitted = st.form_submit_button("Add Project")
        if submitted and title:
            post_data("projects", {"title": title, "start_date": start_date.isoformat(), "end_date": end_date.isoformat() if end_date else None})

    # Update project details
    with st.form("Update Project"):
        st.subheader("Update a Project")
        project_id = st.number_input("Project ID to Update", min_value=1, step=1)
        updated_title = st.text_input("Updated Title")
        updated_start_date = st.date_input("Updated Start Date")
        updated_end_date = st.date_input("Updated End Date")
        update_submitted = st.form_submit_button("Update Project")
        if update_submitted and project_id:
            payload = {
                "title": updated_title if updated_title else None,
                "start_date": updated_start_date.isoformat() if updated_start_date else None,
                "end_date": updated_end_date.isoformat() if updated_end_date else None
            }
            put_data(f"projects/{project_id}", payload)

    # Convert a project to a publication
    st.subheader("Convert Project to Publication")
    project_id = st.number_input("Project ID to Convert", min_value=1, step=1)
    publication_title = st.text_input("Publication Title")
    if st.button("Convert to Publication"):
        post_data("convert_project_to_publication", {"project_id": project_id, "publication_title": publication_title})

elif menu == "Grants":
    st.header("Manage Grants")

    # Fetch and display grants
    grants = fetch_data("grants")
    st.subheader("Existing Grants")
    if grants:
        st.table(grants)
    else:
        st.write("No grants found.")

    # Add a new grant
    with st.form("Add Grant"):
        st.subheader("Add a New Grant")
        amount = st.number_input("Amount", min_value=1, step=1)
        funding_agency_id = st.number_input("Funding Agency ID", min_value=1, step=1)
        submitted = st.form_submit_button("Add Grant")
        if submitted:
            post_data("grants", {"amount": amount, "funding_agency_id": funding_agency_id})

    # Associate a grant with a project
    st.subheader("Associate Grant with Project")
    project_id = st.number_input("Project ID for Association", min_value=1, step=1)
    grant_id = st.number_input("Grant ID for Association", min_value=1, step=1)
    if st.button("Associate Grant"):
        post_data("assign_grant_to_project", {"project_id": project_id, "grant_id": grant_id})

    # Deduct used grant amount
    st.subheader("Deduct Grant Usage")
    grant_id = st.number_input("Grant ID to Deduct Usage", min_value=1, step=1)
    used_amount = st.number_input("Amount Used", min_value=0.01, step=0.01)
    if st.button("Deduct Grant Usage"):
        if grant_id and used_amount > 0:
            response = put_data(f"use_grant/{grant_id}", {"amount": used_amount})
            if response and "remaining_amount" in response:
                st.success(f"Grant updated successfully. Remaining amount: {response['remaining_amount']}")
        else:
            st.error("Valid Grant ID and usage amount are required.")


elif menu == "Funding Agencies":
    st.header("Manage Funding Agencies")

    # Fetch and display funding agencies
    funding_agencies = fetch_data("fundingagencies")
    st.subheader("Existing Funding Agencies")
    if funding_agencies:
        st.table(funding_agencies)
    else:
        st.write("No funding agencies found.")

    # Add a new funding agency
    with st.form("Add Funding Agency"):
        st.subheader("Add a New Funding Agency")
        name = st.text_input("Name")
        budget = st.number_input("Budget", min_value=1, step=1)
        submitted = st.form_submit_button("Add Funding Agency")
        if submitted and name:
            post_data("fundingagencies", {"name": name, "budget": budget})

    # Delete a funding agency
    st.subheader("Delete a Funding Agency")
    funding_agency_id = st.number_input("Funding Agency ID to Delete", min_value=1, step=1)
    if st.button("Delete Funding Agency"):
        if funding_agency_id:
            delete_data(f"fundingagencies/{funding_agency_id}")

elif menu == "Views":
    st.header("Views and Reports")

    # Professor Projects View
    st.subheader("Professor Projects")
    professor_projects = fetch_data("professor_projects")
    if professor_projects:
        st.table(professor_projects)
    else:
        st.write("No data found.")

    # Project Grants Funding View
    st.subheader("Project Grants and Funding Agencies")
    project_grants_funding = fetch_data("project_grants_funding")
    if project_grants_funding:
        st.table(project_grants_funding)
    else:
        st.write("No data found.")

    # Professors Without Projects View
    st.subheader("Professors Without Projects")
    professors_without_projects = fetch_data("professors_without_projects")
    if professors_without_projects:
        st.table(professors_without_projects)
    else:
        st.write("No data found.")

    # All Publications
    st.subheader("All Publications")
    publications = fetch_data("publications")
    if publications:
        st.table(publications)
    else:
        st.write("No publications found.")

elif menu == "Project Audit Log":
    st.header("Project Audit Log")

    # Fetch and display the audit log
    audit_log = fetch_data("project_audit_log")
    if audit_log:
        st.subheader("Audit Log")
        st.table(audit_log)
    else:
        st.write("No entries found in the project audit log.")
