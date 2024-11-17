from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database connection configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Helper Functions
def connect_to_database():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(query, params=None):
    """Execute a query with optional parameters."""
    connection = connect_to_database()
    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def fetch_query(query, params=None):
    """Fetch data from the database."""
    connection = connect_to_database()
    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching data: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

# CRUD Endpoints

@app.route('/professors', methods=['GET'])
def get_professors():
    """Get all professors."""
    query = "SELECT * FROM Professors;"
    data = fetch_query(query)
    return jsonify(data)

@app.route('/professors', methods=['POST'])
def add_professor():
    """Add a new professor."""
    data = request.json
    query = "INSERT INTO Professors (Name, Department, Email) VALUES (%s, %s, %s);"
    professor_id = execute_query(query, (data['name'], data['department'], data['email']))
    return jsonify({'professor_id': professor_id})

@app.route('/professors/<int:professor_id>', methods=['DELETE'])
def delete_professor(professor_id):
    """Delete a professor by ID."""
    query = "DELETE FROM Professors WHERE ProfessorID = %s;"
    execute_query(query, (professor_id,))
    return jsonify({'message': f'Professor with ID {professor_id} deleted.'})

@app.route('/professors/<int:professor_id>', methods=['PUT'])
def update_professor(professor_id):
    """Update a professor by ID."""
    data = request.json
    updates = []
    params = []
    if data.get("name"):
        updates.append("Name = %s")
        params.append(data["name"])
    if data.get("department"):
        updates.append("Department = %s")
        params.append(data["department"])
    if data.get("email"):
        updates.append("Email = %s")
        params.append(data["email"])
    query = f"UPDATE Professors SET {', '.join(updates)} WHERE ProfessorID = %s;"
    params.append(professor_id)
    execute_query(query, tuple(params))
    return jsonify({'message': f'Professor with ID {professor_id} updated.'})

@app.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects."""
    query = "SELECT * FROM Projects;"
    data = fetch_query(query)
    return jsonify(data)

@app.route('/projects', methods=['POST'])
def add_project():
    """Add a new project."""
    data = request.json
    query = "INSERT INTO Projects (Title, StartDate, EndDate) VALUES (%s, %s, %s);"
    project_id = execute_query(query, (data['title'], data['start_date'], data.get('end_date')))
    return jsonify({'project_id': project_id})

@app.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update a project."""
    data = request.json
    updates = []
    params = []
    if data.get("title"):
        updates.append("Title = %s")
        params.append(data["title"])
    if data.get("start_date"):
        updates.append("StartDate = %s")
        params.append(data["start_date"])
    if data.get("end_date"):
        updates.append("EndDate = %s")
        params.append(data["end_date"])
    query = f"UPDATE Projects SET {', '.join(updates)} WHERE ProjectID = %s;"
    params.append(project_id)
    execute_query(query, tuple(params))
    return jsonify({'message': f'Project with ID {project_id} updated.'})

@app.route('/grants', methods=['GET'])
def get_grants():
    """Get all grants."""
    query = "SELECT * FROM Grants;"
    data = fetch_query(query)
    return jsonify(data)

@app.route('/grants', methods=['POST'])
def add_grant():
    """Add a new grant."""
    data = request.json
    query = "INSERT INTO Grants (Amount, FundingAgencyID) VALUES (%s, %s);"
    grant_id = execute_query(query, (data['amount'], data['funding_agency_id']))
    return jsonify({'grant_id': grant_id})

@app.route('/fundingagencies', methods=['GET'])
def get_funding_agencies():
    """Get all funding agencies."""
    query = "SELECT * FROM FundingAgencies;"
    data = fetch_query(query)
    return jsonify(data)

@app.route('/fundingagencies', methods=['POST'])
def add_funding_agency():
    """Add a new funding agency."""
    data = request.json
    query = "INSERT INTO FundingAgencies (Name, Budget) VALUES (%s, %s);"
    agency_id = execute_query(query, (data['name'], data['budget']))
    return jsonify({'funding_agency_id': agency_id})

@app.route('/fundingagencies/<int:agency_id>', methods=['DELETE'])
def delete_funding_agency(agency_id):
    """Delete a funding agency by ID."""
    query = "DELETE FROM FundingAgencies WHERE AgencyID = %s;"
    execute_query(query, (agency_id,))
    return jsonify({'message': f'Funding Agency with ID {agency_id} deleted.'})

@app.route('/professor_projects', methods=['GET'])
def get_professor_projects():
    """Get data from the ProfessorProjects view."""
    query = "SELECT * FROM ProfessorProjects;"
    data = fetch_query(query)
    return jsonify(data)

@app.route('/project_grants_funding', methods=['GET'])
def get_project_grants_funding():
    """Get data from the ProjectGrantsFunding view."""
    query = "SELECT * FROM ProjectGrantsFunding;"
    data = fetch_query(query)
    return jsonify(data)

@app.route('/professors_without_projects', methods=['GET'])
def get_professors_without_projects():
    """Get data from the ProfessorsWithoutProjects view."""
    query = "SELECT * FROM ProfessorsWithoutProjects;"
    data = fetch_query(query)
    return jsonify(data)

@app.route('/publications', methods=['GET'])
def get_publications():
    """Get all publications."""
    query = "SELECT * FROM Publications;"
    data = fetch_query(query)
    return jsonify(data)

@app.route('/professor_publications/<int:professor_id>', methods=['GET'])
def get_professor_publications(professor_id):
    """Get publications made by a specific professor."""
    query = """
        SELECT pub.PublicationID, pub.Title AS PublicationTitle, pr.ProjectID, pr.Title AS ProjectTitle
        FROM Publications pub
        JOIN Projects pr ON pub.ProjectID = pr.ProjectID
        JOIN Professors_Projects pp ON pr.ProjectID = pp.ProjectID
        WHERE pp.ProfessorID = %s;
    """
    data = fetch_query(query, (professor_id,))
    return jsonify(data)

@app.route('/convert_project_to_publication', methods=['POST'])
def convert_project_to_publication():
    """Convert a project to a publication."""
    data = request.json
    query = "CALL ConvertProjectToPublication(%s, %s);"
    execute_query(query, (data['project_id'], data['publication_title']))
    return jsonify({'message': 'Project converted to publication.'})

@app.route('/assign_grant_to_project', methods=['POST'])
def assign_grant_to_project():
    """Associate a grant with a project."""
    data = request.json
    project_id = data.get('project_id')
    grant_id = data.get('grant_id')

    # Ensure both ProjectID and GrantID exist
    project_exists = fetch_query("SELECT 1 FROM Projects WHERE ProjectID = %s", (project_id,))
    grant_exists = fetch_query("SELECT 1 FROM Grants WHERE GrantID = %s", (grant_id,))

    if not project_exists:
        return jsonify({"error": f"Project with ID {project_id} does not exist."}), 400
    if not grant_exists:
        return jsonify({"error": f"Grant with ID {grant_id} does not exist."}), 400

    # Insert the association
    query = "INSERT INTO Projects_Grants (ProjectID, GrantID) VALUES (%s, %s)"
    try:
        execute_query(query, (project_id, grant_id))
        return jsonify({"message": "Grant successfully associated with project."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/project_audit_log', methods=['GET'])
def get_project_audit_log():
    """Fetch the project audit log."""
    query = "SELECT * FROM ProjectAudit ORDER BY Timestamp DESC;"
    data = fetch_query(query)
    return jsonify(data)

@app.route('/assign_professor_to_project', methods=['POST'])
def assign_professor_to_project():
    """Associate a professor with a project."""
    data = request.json
    professor_id = data.get('professor_id')
    project_id = data.get('project_id')

    # Validate that both ProfessorID and ProjectID exist
    professor_exists = fetch_query("SELECT 1 FROM Professors WHERE ProfessorID = %s", (professor_id,))
    project_exists = fetch_query("SELECT 1 FROM Projects WHERE ProjectID = %s", (project_id,))

    if not professor_exists:
        return jsonify({"error": f"Professor with ID {professor_id} does not exist."}), 400
    if not project_exists:
        return jsonify({"error": f"Project with ID {project_id} does not exist."}), 400

    # Insert into Professors_Projects table
    query = "INSERT INTO Professors_Projects (ProfessorID, ProjectID) VALUES (%s, %s)"
    try:
        execute_query(query, (professor_id, project_id))
        return jsonify({"message": "Professor successfully associated with project."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/use_grant/<int:grant_id>', methods=['PUT'])
def use_grant(grant_id):
    """Deduct the used amount from the grant."""
    data = request.json
    used_amount = data.get('amount')

    # Validate input
    if not used_amount or used_amount <= 0:
        return jsonify({"error": "Invalid used amount."}), 400

    # Call the stored procedure
    try:
        execute_query("CALL DeductGrantAmount(%s, %s)", (grant_id, used_amount))
        return jsonify({"message": "Grant updated successfully or deleted if amount reached zero."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Run the app
if __name__ == '__main__':
    app.run(debug=True)
