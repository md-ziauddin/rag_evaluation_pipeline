#!/usr/bin/env python3
"""
CLI Execution Script for Dataset Ingestion (Milestone 1).
Usage:
    python scripts/ingest.py --dataset pubmedqa
    python scripts/ingest.py --dataset medqa
    python scripts/ingest.py --all
"""

import argparse
import sys
from pathlib import Path

# Add src to pythonpath if running as standalone script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_eval.ingestion.manifest import create_manifest
from rag_eval.ingestion.medqa import MedQALoader
from rag_eval.ingestion.pubmedqa import PubMedQALoader


def run_ingestion(dataset_type: str, output_dir: Path):
    print(f"=== Starting Ingestion for {dataset_type.upper()} ===")

    if dataset_type == "pubmedqa":
        loader = PubMedQALoader()
    elif dataset_type == "medqa":
        loader = MedQALoader()
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")

    docs, queries, qrels = loader.process()
    print(
        f"[{dataset_type}] Processed {len(docs)} docs, {len(queries)} queries, {len(qrels)} qrels."
    )
    manifest = create_manifest(
        output_dir=output_dir,
        dataset_name=dataset_type,
        version="v1.0.0",
        docs=docs,
        queries=queries,
        qrels=qrels,
    )
    # Utilize the returned Pydantic object
    print(
        f"[{dataset_type}] Ingestion complete! "
        f"Version: {manifest.version} | "
        f"Docs: {manifest.document_count} | Queries: {manifest.query_count}"
    )


def main():
    parser = argparse.ArgumentParser(description="Ingest and normalize medical datasets.")
    parser.add_argument(
        "--dataset",
        choices=["pubmedqa", "medqa", "all"],
        default="pubmedqa",
        help="Target dataset to ingest",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed"),
        help="Output directory for processed JSONL artifacts",
    )
    args = parser.parse_args()
    if args.dataset == "all":
        run_ingestion("pubmedqa", args.output_dir)
        run_ingestion("medqa", args.output_dir)
    else:
        run_ingestion(args.dataset, args.output_dir)


if __name__ == "__main__":
    main()
