import yaml
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the root directory to sys.path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Base, Source, Metric, InterventionCard, InterventionEffect
from src.config import settings

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def seed():
    engine = create_engine(settings.database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge')
    
    try:
        sources_data = load_yaml(os.path.join(base_dir, 'sources.yaml'))['sources']
        for s in sources_data:
            session.add(Source(**s))
            
        metrics_data = load_yaml(os.path.join(base_dir, 'metrics.yaml'))['metrics']
        for m in metrics_data:
            session.add(Metric(**m))

        cards_data = load_yaml(os.path.join(base_dir, 'cards.yaml'))['cards']
        for c in cards_data:
            card = InterventionCard(
                id=c['id'],
                name=c['name'],
                description=c['description'],
                preconditions=c['preconditions'],
                conflicts_with=c.get('conflicts_with', [])
            )
            session.add(card)
            
            for effect in c.get('effects', []):
                eff = InterventionEffect(
                    card_id=c['id'],
                    metric_id=effect['metric_id'],
                    source_id=effect['source_id'],
                    value_change=effect['value_change'],
                    time_horizon_years=effect['time_horizon_years'],
                    confidence_score=effect['confidence_score']
                )
                session.add(eff)

        session.commit()
        print("Database seeded successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed()
