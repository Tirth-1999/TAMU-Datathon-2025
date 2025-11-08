"""
Audit log models for tracking all system actions
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from .document import Base


class AuditLog(Base):
    """Audit trail for compliance and tracking"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Action details
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)  # document, classification, feedback
    entity_id = Column(Integer, nullable=True)

    # User and context
    user = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Details
    description = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)

    # Status
    success = Column(Text, default=True)
    error_message = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', entity='{self.entity_type}')>"
