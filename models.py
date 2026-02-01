"""
Data models for student information and application tracking
"""
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

Base = declarative_base()

class Student(Base):
    """Student master data model"""
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    nationality = Column(String(100))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    # Academic Information
    high_school_name = Column(String(255))
    graduation_year = Column(Integer)
    gpa = Column(String(10))
    sat_score = Column(Integer)
    act_score = Column(Integer)
    
    # Additional Info
    intended_major = Column(String(255))
    extracurriculars = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'nationality': self.nationality,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'high_school_name': self.high_school_name,
            'graduation_year': self.graduation_year,
            'gpa': self.gpa,
            'sat_score': self.sat_score,
            'act_score': self.act_score,
            'intended_major': self.intended_major,
            'extracurriculars': self.extracurriculars
        }


class Application(Base):
    """Application tracking model"""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable=False)
    university_name = Column(String(255), nullable=False)
    university_url = Column(String(500), nullable=False)
    
    # Account Info
    account_created = Column(Boolean, default=False)
    account_email = Column(String(255))
    account_password = Column(String(255))  # Should be encrypted in production
    email_verified = Column(Boolean, default=False)
    
    # Application Status
    status = Column(String(50), default='pending')  # pending, in_progress, submitted, failed
    application_id = Column(String(100))
    submission_date = Column(DateTime)
    
    # Error Tracking
    last_error = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StudentData(BaseModel):
    """Pydantic model for validation"""
    first_name: str
    last_name: str
    email: EmailStr
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[str] = None
    sat_score: Optional[int] = None
    act_score: Optional[int] = None
    intended_major: Optional[str] = None
    extracurriculars: Optional[str] = None


# Database initialization
def init_db(db_path: str = 'student_data.db'):
    """Initialize database"""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine)
