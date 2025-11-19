#!/usr/bin/env python
"""
Convenience script to run database seeds
"""
import sys
from app.database import SessionLocal
from app.seeds.seed_data import run_seeds

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Running Exit Builder Database Seeds")
    print("="*50 + "\n")

    db = SessionLocal()
    try:
        run_seeds(db)
        print("\n" + "="*50)
        print("✓ Seeding completed successfully!")
        print("="*50 + "\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        sys.exit(1)
    finally:
        db.close()
