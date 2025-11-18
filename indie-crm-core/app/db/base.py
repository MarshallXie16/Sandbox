"""Base model for all SQLAlchemy models"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here for Alembic to detect them
# This file will be imported by alembic/env.py
from app.models.contact import Contact  # noqa
from app.models.company import Company  # noqa
from app.models.deal import Deal  # noqa
from app.models.activity import Activity  # noqa
from app.models.pipeline import DealPipeline, DealStage  # noqa
from app.models.associations import (  # noqa
    ContactCompany,
    ContactDeal,
    CompanyDeal,
    ActivityContact,
    ActivityCompany,
    ActivityDeal,
)
