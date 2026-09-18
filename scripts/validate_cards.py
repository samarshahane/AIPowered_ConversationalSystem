import yaml
import sys
import os

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def validate():
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge')
    
    try:
        sources_data = load_yaml(os.path.join(base_dir, 'sources.yaml'))['sources']
        source_ids = {s['id'] for s in sources_data}
        
        metrics_data = load_yaml(os.path.join(base_dir, 'metrics.yaml'))['metrics']
        metric_ids = {m['id'] for m in metrics_data}
        
        cards_data = load_yaml(os.path.join(base_dir, 'cards.yaml'))['cards']
        
        errors = 0
        for card in cards_data:
            for effect in card.get('effects', []):
                if 'source_id' not in effect or effect['source_id'] not in source_ids:
                    print(f"ERROR: Card '{card['id']}' effect has invalid or missing source_id: {effect.get('source_id')}")
                    errors += 1
                if 'metric_id' not in effect or effect['metric_id'] not in metric_ids:
                    print(f"ERROR: Card '{card['id']}' effect has invalid or missing metric_id: {effect.get('metric_id')}")
                    errors += 1

        if errors > 0:
            print(f"Validation failed with {errors} errors.")
            sys.exit(1)
        else:
            print("All cards validated successfully.")
            
    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    validate()
