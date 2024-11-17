# University Research Grant Allocation System (URGAS)

URGAS is a web-based application designed to manage research grants, professors, projects, and funding agencies for universities. The system features a frontend built with Streamlit and a backend developed using Flask and MySQL.

## Features

### Professors Management
- Add, update, delete, and view professors.
- Associate professors with projects.
- View publications by professors.

### Projects Management
- Add, update, delete, and view projects.
- Convert projects to publications.
- Assign grants to projects.

### Grants Management
- Add, view, and deduct amounts from grants.
- Associate grants with projects.

### Funding Agencies
- Add, delete, and view funding agencies.

### Reports and Views
- View professor-project associations.
- View grant-project funding details.
- View professors without projects.
- View all publications.
- View project audit logs.

## Technologies Used
- **Frontend**: Streamlit
- **Backend**: Flask
- **Database**: MySQL
- **Communication**: Flask-REST API
- **Other Tools**: dotenv for environment variable management

## Setup Instructions

### Prerequisites
- Python 3.7+
- MySQL Server
- pip (Python package manager)
- `.env` file with the following variables:
```
DB_HOST=your_db_host
DB_USER=your_db_user 
DB_PASSWORD=your_db_password 
DB_NAME=your_db_name
```

### Installation
1. Clone the repository:
 ```bash
 git clone https://github.com/siddharth-k03/URGAS.git
 cd URGAS
 ```

2. Install dependencies:
 ```bash
 pip install -r requirements.txt
 ```

3. Set up the database:
- Create a MySQL database and populate it with the required tables and stored procedures.

4. Run the backend server:
 ```bash
 python backend.py
 ```

5. Run the frontend:
 ```bash
 streamlit run URGAS.py
 ```

6. Access the application at http://localhost:8501.

## API Endpoints
The backend exposes the following API endpoints:

/professors: Manage professors.
/projects: Manage projects.
/grants: Manage grants.
/fundingagencies: Manage funding agencies.
/convert_project_to_publication: Convert projects to publications.
/assign_professor_to_project: Associate professors with projects.
/use_grant/<grant_id>: Deduct grant usage.
/professor_projects: View professor-project associations.
/project_audit_log: View project audit logs.