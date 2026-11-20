from functools import wraps
from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models.employee import Employee, LeaveRequest, AttendanceRecord, UpdateHistory
from app.models import db
from sqlalchemy import desc, asc, or_
from datetime import datetime, date
from werkzeug.security import generate_password_hash

employee_bp=Blueprint("employee",__name__)


def _record_update_history(entity_type, entity_id, action, description, message=None):
    display_name = "System"
    if session.get("user_name") and session.get("user_id"):
        display_name = f"{session.get('user_name')} (ID: {session.get('user_id')})"
    elif session.get("user_name"):
        display_name = session.get("user_name")
    elif session.get("user_id"):
        display_name = f"User ID: {session.get('user_id')}"

    if entity_type == "employee":
        description = f"Employee #{entity_id} — {description}"
    elif entity_type == "leave_request":
        description = f"Leave Request #{entity_id} — {description}"

    history = UpdateHistory(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        description=description,
        message=message,
        updated_by=display_name,
    )
    db.session.add(history)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        if session.get('is_admin') is not True:
            return redirect(url_for('employee.employee_portal'))
        return view(*args, **kwargs)
    return wrapped

def employee_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.employee_login'))
        if session.get('is_admin') is True:
            return redirect(url_for('home.home'))
        return view(*args, **kwargs)
    return wrapped

@employee_bp.route("/employee/<int:id>/<string:name>")
def searchByNameId(id,name):
    return f"ID : {id} Name : {name}"

@employee_bp.route("/employee")
def displaySpecific():
    department=request.args.get("department")
    page=request.args.get("page")

    return f"Department: {department} Page : {page}"

@employee_bp.route("/employeeDepartment")
def gotodept():
    return redirect (url_for("department.departmentHome"))

@employee_bp.route("/employee/register")
@login_required
def register_employee():
    return render_template("add_employee.html")


@employee_bp.route("/employee/list")
@login_required
def employee_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search_query = request.args.get("search", "", type=str).strip()
    sort_by = request.args.get("sort_by", "id", type=str)
    sort_order = request.args.get("sort_order", "asc", type=str)
    department_filter = request.args.get("department", "", type=str).strip()
    status_filter = request.args.get("status", "", type=str).strip()
    min_salary = request.args.get("min_salary", "", type=str).strip()
    max_salary = request.args.get("max_salary", "", type=str).strip()

    if per_page not in [5, 10]:
        per_page = 10

    query = Employee.query

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Employee.name.ilike(search_pattern),
                Employee.email.ilike(search_pattern),
                Employee.department.ilike(search_pattern),
                Employee.position.ilike(search_pattern)
            )
        )

    if department_filter:
        query = query.filter(Employee.department == department_filter)

    if status_filter:
        query = query.filter(Employee.status == status_filter)

    if min_salary:
        try:
            query = query.filter(Employee.salary >= float(min_salary))
        except ValueError:
            min_salary = ""

    if max_salary:
        try:
            query = query.filter(Employee.salary <= float(max_salary))
        except ValueError:
            max_salary = ""

    sort_columns = {
        "id": Employee.id,
        "name": Employee.name,
        "email": Employee.email,
        "department": Employee.department,
        "salary": Employee.salary,
        "position": Employee.position,
        "date_of_joining": Employee.date_of_joining,
        "status": Employee.status,
    }
    order_col = sort_columns.get(sort_by, Employee.id)

    if sort_order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(asc(order_col))

    paginated_employees = query.paginate(page=page, per_page=per_page, error_out=False)

    departments = [row[0] for row in db.session.query(Employee.department).distinct().all() if row[0]]
    statuses = [row[0] for row in db.session.query(Employee.status).distinct().all() if row[0]]

    context = {
        "employees": paginated_employees.items,
        "pagination": paginated_employees,
        "page": page,
        "per_page": per_page,
        "search_query": search_query,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "department_filter": department_filter,
        "status_filter": status_filter,
        "min_salary": min_salary,
        "max_salary": max_salary,
        "departments": departments,
        "statuses": statuses,
        "total_records": paginated_employees.total
    }

    return render_template("employee.html", **context)


@employee_bp.route("/employee/add",methods=["POST","GET"])
@login_required
def employeeAdd():

    if request.method == "POST":
        existing = Employee.query.filter_by(email=request.form["email"]).first()
        if existing:
            flash("Employee email already exists", "danger")
            return render_template("add_employee.html")

        employee=Employee(
            name = request.form["name"],
            email = request.form["email"],
            password_hash = generate_password_hash(request.form["password"]),
            salary = request.form["salary"],
            department = request.form["department"],
            position = request.form.get("position", "Employee"),
            date_of_joining = datetime.strptime(request.form["date_of_joining"], "%Y-%m-%d").date() if request.form.get("date_of_joining") else datetime.today().date(),
            status = request.form.get("status", "Active")
        )

        db.session.add(employee)
        db.session.flush()
        _record_update_history("employee", employee.id, "employee_created", "New employee added", "Employee record created")
        db.session.commit()

        return redirect(url_for("employee.employee_list"))

    return render_template("add_employee.html")

@employee_bp.route("/employee/employeeDetail/<int:id>",methods=["GET"])
@login_required
def employeeDetail(id):
    employee = Employee.query.get_or_404(id)
    history_entries = UpdateHistory.query.filter_by(entity_type="employee", entity_id=employee.id).order_by(UpdateHistory.created_at.desc()).all()

    return render_template("employee_detail.html", employee=employee, employee_update_history=history_entries)

@employee_bp.route("/employee/employeeUpdate/<int:id>",methods=["POST","GET"])
@login_required
def employeeUpdate(id):
    employee=Employee.query.get_or_404(id)

    if request.method == "POST":
            existing = Employee.query.filter(Employee.email == request.form["email"], Employee.id != id).first()
            if existing:
                flash("Employee email already exists", "danger")
                return render_template("update_employee.html", employee=employee)

            original_name = employee.name
            original_email = employee.email
            original_salary = employee.salary
            original_department = employee.department
            original_position = employee.position
            original_status = employee.status

            employee.name = request.form["name"]
            employee.email = request.form["email"]
            new_password = request.form.get("password", "")
            if new_password:
                employee.password_hash = generate_password_hash(new_password)
            employee.salary = request.form["salary"]
            employee.department = request.form["department"]
            employee.position = request.form.get("position", employee.position)
            employee.date_of_joining = datetime.strptime(request.form["date_of_joining"], "%Y-%m-%d").date() if request.form.get("date_of_joining") else employee.date_of_joining
            employee.status = request.form.get("status", employee.status)

            changed_fields = []
            if employee.name != original_name:
                changed_fields.append("name")
            if employee.email != original_email:
                changed_fields.append("email")
            if employee.salary != original_salary:
                changed_fields.append("salary")
            if employee.department != original_department:
                changed_fields.append("department")
            if employee.position != original_position:
                changed_fields.append("position")
            if employee.status != original_status:
                changed_fields.append("status")

            update_message = request.form.get("update_message", "").strip()
            description = "Employee profile updated"
            if changed_fields:
                description = f"Updated employee fields: {', '.join(changed_fields)}"

            _record_update_history("employee", employee.id, "employee_updated", description, update_message or "Employee details updated")
            db.session.commit()

            return redirect(url_for("employee.employee_list"))

    return render_template("update_employee.html",employee=employee)

@employee_bp.route("/employee/employeeDelete/<int:id>", methods=["POST"])
@login_required
def employeeDelete(id):

    employee=Employee.query.get_or_404(id)

    db.session.delete(employee)
    db.session.commit()

    return redirect(url_for("employee.employee_list"))


@employee_bp.route("/employee/portal")
@employee_login_required
def employee_portal():
    employee = Employee.query.get_or_404(session['user_id'])
    leaves = LeaveRequest.query.filter_by(employee_id=employee.id).order_by(LeaveRequest.applied_on.desc()).all()
    attendance = AttendanceRecord.query.filter_by(employee_id=employee.id).order_by(AttendanceRecord.attendance_date.desc()).all()
    return render_template("employee_portal.html", employee=employee, leaves=leaves, attendance=attendance)


@employee_bp.route("/employee/portal/leave", methods=["POST"])
@employee_login_required
def apply_leave():
    employee = Employee.query.get_or_404(session['user_id'])
    leave = LeaveRequest(
        employee_id=employee.id,
        reason=request.form.get("reason", ""),
        start_date=datetime.strptime(request.form["start_date"], "%Y-%m-%d").date(),
        end_date=datetime.strptime(request.form["end_date"], "%Y-%m-%d").date(),
        status="Pending"
    )
    db.session.add(leave)
    db.session.commit()
    flash("Leave request submitted", "success")
    return redirect(url_for("employee.employee_portal"))


@employee_bp.route("/employee/portal/attendance", methods=["POST"])
@employee_login_required
def mark_attendance():
    employee = Employee.query.get_or_404(session['user_id'])
    attendance_date = datetime.strptime(request.form["attendance_date"], "%Y-%m-%d").date() if request.form.get("attendance_date") else date.today()
    record = AttendanceRecord.query.filter_by(employee_id=employee.id, attendance_date=attendance_date).first()
    if record:
        flash("Attendance already marked for this date", "warning")
        return redirect(url_for("employee.employee_portal"))
    new_record = AttendanceRecord(employee_id=employee.id, attendance_date=attendance_date, status=request.form.get("status", "Present"), notes=request.form.get("notes", ""))
    db.session.add(new_record)
    db.session.commit()
    flash("Attendance marked", "success")
    return redirect(url_for("employee.employee_portal"))


@employee_bp.route("/employee/admin/dashboard")
@login_required
def admin_dashboard():
    search_query = request.args.get("search", "", type=str).strip()
    entity_filter = request.args.get("entity_type", "", type=str).strip()
    action_filter = request.args.get("action", "", type=str).strip()
    updated_by_filter = request.args.get("updated_by", "", type=str).strip()
    start_date = request.args.get("start_date", "", type=str).strip()
    end_date = request.args.get("end_date", "", type=str).strip()
    sort_by = request.args.get("sort_by", "created_at", type=str)
    sort_order = request.args.get("sort_order", "desc", type=str)

    query = UpdateHistory.query

    if search_query:
        pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                UpdateHistory.entity_type.ilike(pattern),
                UpdateHistory.action.ilike(pattern),
                UpdateHistory.description.ilike(pattern),
                UpdateHistory.message.ilike(pattern),
                UpdateHistory.updated_by.ilike(pattern),
            )
        )

    if entity_filter:
        query = query.filter(UpdateHistory.entity_type == entity_filter)

    if action_filter:
        query = query.filter(UpdateHistory.action == action_filter)

    if updated_by_filter:
        query = query.filter(UpdateHistory.updated_by.ilike(f"%{updated_by_filter}%"))

    if start_date:
        try:
            query = query.filter(UpdateHistory.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
        except ValueError:
            start_date = ""

    if end_date:
        try:
            query = query.filter(UpdateHistory.created_at <= datetime.strptime(end_date, "%Y-%m-%d"))
        except ValueError:
            end_date = ""

    sort_columns = {
        "created_at": UpdateHistory.created_at,
        "entity_type": UpdateHistory.entity_type,
        "action": UpdateHistory.action,
        "updated_by": UpdateHistory.updated_by,
        "entity_id": UpdateHistory.entity_id,
    }
    order_col = sort_columns.get(sort_by, UpdateHistory.created_at)

    if sort_order == "asc":
        query = query.order_by(asc(order_col))
    else:
        query = query.order_by(desc(order_col))

    history_entries = query.all()
    entity_types = [row[0] for row in db.session.query(UpdateHistory.entity_type).distinct().all() if row[0]]
    actions = [row[0] for row in db.session.query(UpdateHistory.action).distinct().all() if row[0]]

    return render_template(
        "admin_dashboard.html",
        history_entries=history_entries,
        search_query=search_query,
        entity_filter=entity_filter,
        action_filter=action_filter,
        updated_by_filter=updated_by_filter,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        entity_types=entity_types,
        actions=actions,
    )


@employee_bp.route("/employee/admin/leave-requests")
@login_required
def admin_leave_requests():
    search_query = request.args.get("search", "", type=str).strip()
    department_filter = request.args.get("department", "", type=str).strip()
    status_filter = request.args.get("status", "", type=str).strip()
    start_date = request.args.get("start_date", "", type=str).strip()
    end_date = request.args.get("end_date", "", type=str).strip()
    sort_by = request.args.get("sort_by", "applied_on", type=str)
    sort_order = request.args.get("sort_order", "desc", type=str)

    query = LeaveRequest.query.join(Employee)

    if search_query:
        pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Employee.name.ilike(pattern),
                Employee.email.ilike(pattern),
                LeaveRequest.reason.ilike(pattern),
                LeaveRequest.status.ilike(pattern),
            )
        )

    if department_filter:
        query = query.filter(Employee.department == department_filter)

    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)

    if start_date:
        try:
            query = query.filter(LeaveRequest.start_date >= datetime.strptime(start_date, "%Y-%m-%d").date())
        except ValueError:
            start_date = ""

    if end_date:
        try:
            query = query.filter(LeaveRequest.end_date <= datetime.strptime(end_date, "%Y-%m-%d").date())
        except ValueError:
            end_date = ""

    sort_columns = {
        "applied_on": LeaveRequest.applied_on,
        "start_date": LeaveRequest.start_date,
        "end_date": LeaveRequest.end_date,
        "status": LeaveRequest.status,
        "reason": LeaveRequest.reason,
    }
    order_col = sort_columns.get(sort_by, LeaveRequest.applied_on)

    if sort_order == "asc":
        query = query.order_by(asc(order_col))
    else:
        query = query.order_by(desc(order_col))

    requests = query.all()
    departments = [row[0] for row in db.session.query(Employee.department).distinct().all() if row[0]]
    statuses = [row[0] for row in db.session.query(LeaveRequest.status).distinct().all() if row[0]]

    return render_template(
        "admin_leave_requests.html",
        requests=requests,
        search_query=search_query,
        department_filter=department_filter,
        status_filter=status_filter,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        departments=departments,
        statuses=statuses,
    )


@employee_bp.route("/employee/admin/leave-requests/<int:request_id>/<string:action>", methods=["POST", "GET"])
@login_required
def update_leave_request(request_id, action):
    leave_request = LeaveRequest.query.get_or_404(request_id)
    if action not in ["approve", "disapprove"]:
        flash("Invalid action", "danger")
        return redirect(url_for("employee.admin_leave_requests"))

    new_status = "Approved" if action == "approve" else "Disapproved"
    leave_request.status = new_status

    message = request.form.get("message", "").strip() or f"Leave request {action}d"
    description = f"Leave status updated to {new_status} for Employee #{leave_request.employee_id}; reason: {leave_request.reason}; dates: {leave_request.start_date} to {leave_request.end_date}"
    _record_update_history("leave_request", leave_request.id, "leave_status_updated", description, message)
    db.session.commit()
    flash(f"Leave request {action}d", "success")
    return redirect(url_for("employee.admin_leave_requests"))


@employee_bp.route("/employee/admin/attendance")
@login_required
def admin_attendance():
    search_query = request.args.get("search", "", type=str).strip()
    department_filter = request.args.get("department", "", type=str).strip()
    status_filter = request.args.get("status", "", type=str).strip()
    start_date = request.args.get("start_date", "", type=str).strip()
    end_date = request.args.get("end_date", "", type=str).strip()
    sort_by = request.args.get("sort_by", "attendance_date", type=str)
    sort_order = request.args.get("sort_order", "desc", type=str)

    query = AttendanceRecord.query.join(Employee)

    if search_query:
        pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Employee.name.ilike(pattern),
                Employee.email.ilike(pattern),
                AttendanceRecord.notes.ilike(pattern),
                AttendanceRecord.status.ilike(pattern),
            )
        )

    if department_filter:
        query = query.filter(Employee.department == department_filter)

    if status_filter:
        query = query.filter(AttendanceRecord.status == status_filter)

    if start_date:
        try:
            query = query.filter(AttendanceRecord.attendance_date >= datetime.strptime(start_date, "%Y-%m-%d").date())
        except ValueError:
            start_date = ""

    if end_date:
        try:
            query = query.filter(AttendanceRecord.attendance_date <= datetime.strptime(end_date, "%Y-%m-%d").date())
        except ValueError:
            end_date = ""

    sort_columns = {
        "attendance_date": AttendanceRecord.attendance_date,
        "marked_on": AttendanceRecord.marked_on,
        "status": AttendanceRecord.status,
        "employee_name": Employee.name,
    }
    order_col = sort_columns.get(sort_by, AttendanceRecord.attendance_date)

    if sort_order == "asc":
        query = query.order_by(asc(order_col))
    else:
        query = query.order_by(desc(order_col))

    records = query.all()
    departments = [row[0] for row in db.session.query(Employee.department).distinct().all() if row[0]]
    statuses = [row[0] for row in db.session.query(AttendanceRecord.status).distinct().all() if row[0]]

    return render_template(
        "admin_attendance.html",
        records=records,
        search_query=search_query,
        department_filter=department_filter,
        status_filter=status_filter,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        departments=departments,
        statuses=statuses,
    )



