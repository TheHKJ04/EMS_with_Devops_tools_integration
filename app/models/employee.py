from datetime import date, datetime
from app.models import db


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    salary = db.Column(db.Float, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False, default="Employee")
    date_of_joining = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default="Active")

    leave_requests = db.relationship("LeaveRequest", backref="employee", lazy=True, cascade="all, delete-orphan")
    attendance_records = db.relationship("AttendanceRecord", backref="employee", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Employee Name: {self.name}"


class UpdateHistory(db.Model):
    __tablename__ = "update_history"

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=True)
    updated_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    applied_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default="Present")
    notes = db.Column(db.String(255), nullable=True)
    marked_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("employee_id", "attendance_date", name="uq_employee_attendance_date"),)