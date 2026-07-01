"""
CLI: build the vector index from a resume file + a job-description file.

Usage:
    python scripts/build_index.py --resume data/resumes/john.pdf --jd data/job_descriptions/role.txt
"""
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.ingest import build_documents
from src.vectorstore import build_vectorstore, save_vectorstore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", required=True, help="Path to resume file (pdf/docx/txt)")
    parser.add_argument("--jd", required=True, help="Path to job description file (pdf/docx/txt)")
    args = parser.parse_args()

    print(f"Loading resume: {args.resume}")
    print(f"Loading job description: {args.jd}")
    docs = build_documents(args.resume, args.jd, jd_is_file=True)
    print(f"Created {len(docs)} chunks. Embedding + building FAISS index...")

    store = build_vectorstore(docs)
    save_vectorstore(store)
    print("Vector store saved. You can now run: streamlit run app.py")


if __name__ == "__main__":
    main()
