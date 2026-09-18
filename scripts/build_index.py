import os
import sys
import yaml
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

try:
    from pypdf import PdfReader
except ImportError:
    print("pypdf is required to read PDFs. Please run: pip install pypdf")
    sys.exit(1)

# Add the root directory to sys.path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import settings

def load_sources():
    sources_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge', 'sources.yaml')
    with open(sources_file, 'r') as f:
        data = yaml.safe_load(f)
    return {s['id']: s for s in data['sources']}

def extract_text_from_pdf(pdf_path):
    text_chunks = []
    try:
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text_chunks.append({
                    "text": text.strip(),
                    "page": i + 1
                })
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text_chunks

def chunk_text(text, max_length=1500, overlap=300):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_length, len(text))
        chunks.append(text[start:end])
        start += (max_length - overlap)
    return chunks

def build_index():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    corpus_dir = os.path.join(base_dir, 'data', 'corpus')
    
    if not os.path.exists(corpus_dir):
        os.makedirs(corpus_dir)
        print(f"Created {corpus_dir}. Please place PDFs there.")
        return

    sources = load_sources()
    
    # Initialize Chroma
    client = chromadb.PersistentClient(path=settings.chroma_db_dir)
    collection = client.get_or_create_collection(name="verdant_corpus")
    
    # SentenceTransformer explicitly
    model = SentenceTransformer('all-MiniLM-L6-v2')

    documents = []
    metadatas = []
    ids = []
    
    doc_id_counter = 1

    for filename in os.listdir(corpus_dir):
        if not filename.endswith('.pdf') and not filename.endswith('.txt'):
            continue
            
        source_id = filename.replace('.pdf', '').replace('.txt', '')
        if source_id not in sources:
            print(f"Warning: File {filename} has no matching source_id in sources.yaml. Using filename.")
            source_meta = {"title": filename}
        else:
            source_meta = sources[source_id]

        file_path = os.path.join(corpus_dir, filename)
        print(f"Processing {filename}...")
        
        if filename.endswith('.pdf'):
            pages = extract_text_from_pdf(file_path)
            for p in pages:
                page_text = p["text"]
                page_num = p["page"]
                
                chunks = chunk_text(page_text, max_length=1500, overlap=300)
                for chunk in chunks:
                    if len(chunk) < 50:
                        continue
                    
                    documents.append(chunk)
                    metadatas.append({
                        "source_id": source_id,
                        "title": source_meta.get("title", ""),
                        "page": page_num
                    })
                    ids.append(f"chunk_{doc_id_counter}")
                    doc_id_counter += 1
        elif filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            chunks = chunk_text(text, max_length=1500, overlap=300)
            for chunk in chunks:
                if len(chunk) < 50:
                    continue
                documents.append(chunk)
                metadatas.append({
                    "source_id": source_id,
                    "title": source_meta.get("title", ""),
                    "page": 1
                })
                ids.append(f"chunk_{doc_id_counter}")
                doc_id_counter += 1

    if not documents:
        print("No documents to index. Provide PDFs or TXT files in data/corpus/ matching source IDs.")
        return

    print(f"Encoding {len(documents)} chunks...")
    embeddings = model.encode(documents).tolist()
    
    print(f"Adding to ChromaDB at {settings.chroma_db_dir}...")
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Index built successfully.")

if __name__ == "__main__":
    build_index()
