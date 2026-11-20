# Employee Management System - Advanced Edition

A comprehensive Flask-based Employee Management System with advanced features including pagination, searching, sorting, filtering, and an improved user interface.

## 🚀 Features

### Core CRUD Operations
- ✅ Create new employee records
- ✅ Read and view employee details
- ✅ Update existing employee information
- ✅ Delete employee records

### Advanced Features
- 📄 **Pagination**: Display employees with 5 or 10 records per page
- 🔍 **Search**: Search employees by name, email, or department
- 🔄 **Sorting**: Sort employees by name, email, department, or salary (ascending/descending)
- 🎯 **Filtering**: Filter employees by department and salary range
- 🔗 **Combined Functionality**: All features work seamlessly together
- 📱 **Responsive Design**: Bootstrap 5.3.8 for mobile-friendly interface

### User Interface
- Clean and modern dashboard
- Responsive Bootstrap components
- Intuitive search and filter controls
- Professional employee table with action buttons
- Success and error message displays
- "No records found" messaging

## 🛠️ Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: Bootstrap 5.3.8, Jinja2 Templates
- **Python Version**: 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server (running and accessible)
- pip (Python package manager)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/TheHKJ04/Employee-Management-System.git
cd Flask-self-learning
```

### 2. Create a Virtual Environment
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database

Edit `config.py` and update the database configuration:
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:newpassword@localhost:3306/employee_db"
```

Replace with your MySQL credentials:
- `root`: MySQL username
- `newpassword`: MySQL password
- `localhost`: MySQL host
- `3306`: MySQL port
- `employee_db`: Database name

### 5. Create Database
```bash
mysql -u root -p
CREATE DATABASE employee_db;
EXIT;
```

### 6. Run Database Migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## 📖 Usage Guide

### 1. Home Page
Navigate to `http://localhost:5000/home` to access the home page.

### 2. Employee List
Visit `http://localhost:5000/employee/list` to view all employees with advanced features:

#### Search
- Enter employee name, email, or department in the search box
- Click "Search" button

#### Filter
- Select a department from the dropdown
- Enter minimum and/or maximum salary
- Click "Search" button

#### Sort
- Choose sort field (Name, Email, Department, Salary)
- Select order (Ascending/Descending)
- Results update automatically

#### Pagination
- Choose records per page (5 or 10)
- Use Previous/Next buttons or page numbers
- All filters are preserved when navigating

#### Combined Search
Example URL with all parameters:
```
/employee/list?search=John&department=IT&min_salary=50000&max_salary=100000&sort_by=salary&sort_order=desc&per_page=10&page=1
```

### 3. Add Employee
1. Click "Add New Employee" button
2. Fill in all fields:
   - Full Name
   - Email Address
   - Password
   - Department
   - Salary
3. Click "Submit"

### 4. View Employee Details
- Click "View" button on any employee row
- See complete employee information
- Option to edit or delete from this page

### 5. Update Employee
1. Click "Edit" button on any employee row
2. Modify desired fields
3. Click "Update" button

### 6. Delete Employee
- Click "Delete" button on any employee row
- Confirm deletion when prompted

## 🗂️ Project Structure

```
Flask-self-learning/
├── app.py                    # Main application entry point
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models/
│   │   ├── __init__.py
│   │   └── employee.py      # Employee model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── employee.py      # Employee routes with advanced features
│   │   ├── department.py    # Department routes
│   │   ├── auth.py          # Authentication routes
│   │   └── home.py          # Home routes
│   ├── templates/
│   │   ├── base.html        # Base template
│   │   ├── navbar.html      # Navigation bar
│   │   ├── employee.html    # Employee list with pagination & filters
│   │   ├── add_employee.html
│   │   ├── update_employee.html
│   │   ├── employee_detail.html
│   │   ├── department.html
│   │   └── home.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── script.js
│   └── utils/
│       └── __init__.py
├── migrations/              # Database migrations
└── instance/
```

## 🔄 Advanced Features Implementation

### Pagination
- Uses Flask-SQLAlchemy `paginate()` method
- Configurable page size (5 or 10 records)
- Previous/Next navigation
- Direct page number selection
- Preserves filter and sort parameters

### Searching
- Multi-field search (Name, Email, Department)
- Case-insensitive using SQLAlchemy `ilike()`
- Uses OR logic for multiple fields
- Real-time filtering

### Sorting
- Sort by Name, Email, Department, or Salary
- Ascending and Descending options
- Query parameter based (`sort_by`, `sort_order`)
- Maintains with other filters

### Filtering
- Department-based filtering
- Salary range filtering (min/max)
- Multiple filters work simultaneously
- Proper data type conversion and validation

### Combined Functionality
- All features integrated seamlessly
- URL parameters preserved across navigation
- Proper form submission and GET requests
- Dynamic query building

## 🧪 Testing Checklist

- [x] Pagination works with different page sizes
- [x] Search filters correctly
- [x] Sorting applies properly
- [x] Department filtering works
- [x] Salary range filtering works
- [x] Combined filters work together
- [x] Pagination preserves filters
- [x] CRUD operations still function
- [x] UI is responsive and user-friendly
- [x] No records message displays correctly
- [x] All buttons and links work properly

## 🎨 UI Improvements

- Modern, clean interface using Bootstrap 5.3.8
- Responsive design for mobile and desktop
- Color-coded buttons (Success, Warning, Info, Danger)
- Icon integration for better UX
- Professional card layouts
- Proper spacing and padding
- Hover effects on tables
- Validation feedback on forms
- Success/error alerts
- Professional footer

## 🐛 Troubleshooting

### Database Connection Error
```
Error: Unable to connect to database
```
- Verify MySQL server is running
- Check database credentials in `config.py`
- Ensure database exists

### Migration Issues
```
flask db upgrade
```

### Module Not Found
```
pip install -r requirements.txt
```

### Port Already in Use
```
python app.py --port 5001
```

## 📝 Notes

- Passwords are stored as plain text (for learning purposes only - use hashing in production)
- Flask debug mode is enabled by default (disable in production)
- Database URI uses PyMySQL driver

## 🤝 Contributing

Feel free to fork and create pull requests for any improvements.

## 📄 License

This project is open source and available for educational purposes.

## 📧 Support

For issues or questions, please open an issue on GitHub or contact the repository owner.

---

**Last Updated**: 2026-07-19  
**Version**: 2.0 (Advanced Edition)  
