from setuptools import setup, find_packages

setup(
    name="indie-engagement-tracker",
    version="0.1.0",
    description="Client Engagement Tracker for IndieStack CRM and Capital Ink Hub",
    author="IndieStack Team",
    packages=find_packages(exclude=["tests", "docs"]),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.23",
        "alembic>=1.12.1",
        "psycopg2-binary>=2.9.9",
        "typer>=0.9.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dateutil>=2.8.2",
        "httpx>=0.25.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "faker>=20.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "tracker=app.cli.main:app",
        ],
    },
)
