"""Seed data for pipelines and stages"""
from sqlalchemy.orm import Session
from app.models.pipeline import DealPipeline, DealStage, PipelineType


def seed_pipelines_and_stages(db: Session) -> None:
    """
    Create default seller and buyer pipelines with their stages.

    This function is idempotent - it won't create duplicates if pipelines
    already exist.
    """
    # Check if pipelines already exist
    existing = db.query(DealPipeline).first()
    if existing:
        print("Pipelines already seeded, skipping...")
        return

    # Seller Pipeline
    seller_pipeline = DealPipeline(
        name="Seller Pipeline",
        type=PipelineType.SELLER,
        is_active=True,
    )
    db.add(seller_pipeline)
    db.flush()  # Get the ID

    seller_stages = [
        {"name": "Exit Ready Engagement", "order_index": 1},
        {"name": "Facilitator Engagement", "order_index": 2},
        {"name": "Broker Engagement", "order_index": 3},
        {"name": "Marketing", "order_index": 4},
        {"name": "LOI Acceptance", "order_index": 5},
        {"name": "Due Diligence", "order_index": 6},
        {"name": "Closing", "order_index": 7},
        {"name": "Won", "order_index": 8, "is_closed_won": True},
        {"name": "Lost", "order_index": 9, "is_closed_lost": True},
    ]

    for stage_data in seller_stages:
        stage = DealStage(
            pipeline_id=seller_pipeline.id,
            name=stage_data["name"],
            order_index=stage_data["order_index"],
            is_closed_won=stage_data.get("is_closed_won", False),
            is_closed_lost=stage_data.get("is_closed_lost", False),
        )
        db.add(stage)

    # Buyer Pipeline
    buyer_pipeline = DealPipeline(
        name="Buyer Pipeline",
        type=PipelineType.BUYER,
        is_active=True,
    )
    db.add(buyer_pipeline)
    db.flush()  # Get the ID

    buyer_stages = [
        {"name": "Buyer Access Agreement", "order_index": 1},
        {"name": "Finder Agreement", "order_index": 2},
        {"name": "Broker Engagement", "order_index": 3},
        {"name": "Marketing", "order_index": 4},
        {"name": "LOI Acceptance", "order_index": 5},
        {"name": "Due Diligence", "order_index": 6},
        {"name": "Closing", "order_index": 7},
        {"name": "Won", "order_index": 8, "is_closed_won": True},
        {"name": "Lost", "order_index": 9, "is_closed_lost": True},
    ]

    for stage_data in buyer_stages:
        stage = DealStage(
            pipeline_id=buyer_pipeline.id,
            name=stage_data["name"],
            order_index=stage_data["order_index"],
            is_closed_won=stage_data.get("is_closed_won", False),
            is_closed_lost=stage_data.get("is_closed_lost", False),
        )
        db.add(stage)

    db.commit()
    print("Successfully seeded seller and buyer pipelines with stages!")


if __name__ == "__main__":
    # Allow running this script directly
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        seed_pipelines_and_stages(db)
    finally:
        db.close()
