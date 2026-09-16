#!/usr/bin/env python3
"""
Full Dataset Experiment & Benchmark Execution Runner.

Executes complete benchmark sweeps across the ingested medical dataset (PubMedQA / MedQA),
evaluating retrieval strategies (Dense vs. Hybrid RRF) and orchestration pipelines
(Linear vs. Agentic) under real competition with hundreds or thousands of distractor documents.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_eval.config.settings import settings
from rag_eval.experiments.matrix import MatrixExpander
from rag_eval.experiments.reporter import ComparisonReporter
from rag_eval.experiments.runner import ExperimentRunner
from rag_eval.ingestion.pubmedqa import PubMedQALoader
from rag_eval.ingestion.schemas import Document, Qrel, Query


def load_dataset(
    processed_dir: Path,
) -> tuple[list[Document], list[Query], list[Qrel]]:
    """
    Load normalized documents, queries, and qrels from processed JSONL files,
    falling back to live PubMedQALoader if processed artifacts do not exist.
    """
    docs_file = processed_dir / "pubmedqa_documents.jsonl"
    queries_file = processed_dir / "pubmedqa_queries.jsonl"
    qrels_file = processed_dir / "pubmedqa_qrels.jsonl"

    if docs_file.exists() and queries_file.exists() and qrels_file.exists():
        print(f"[Dataset Loader] Loading pre-processed dataset from {processed_dir}...")
        documents: list[Document] = []
        with open(docs_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    documents.append(Document(**json.loads(line)))

        queries: list[Query] = []
        with open(queries_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    queries.append(Query(**json.loads(line)))

        qrels: list[Qrel] = []
        with open(qrels_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    qrels.append(Qrel(**json.loads(line)))

        return documents, queries, qrels

    print("[Dataset Loader] Processed JSONL not found. Ingesting from HuggingFace...")
    loader = PubMedQALoader()
    return loader.process()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Full Medical RAG Evaluation Benchmark across hundreds of documents."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/experiment.yaml",
        help="Path to experiment matrix YAML configuration file (default: config/experiment.yaml)",
    )
    parser.add_argument(
        "--num-docs",
        type=int,
        default=250,
        help="Number of documents to index into corpus for competition (default: 250)",
    )
    parser.add_argument(
        "--num-queries",
        type=int,
        default=25,
        help="Number of evaluation queries to benchmark (default: 25)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Benchmark across the entire dataset (3,358 documents and 1,000 queries)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Directory to save the markdown comparison report (default: reports)",
    )
    args = parser.parse_args()

    print("===================================================================")
    print("   MEDICAL RAG PIPELINE BENCHMARK SWEEP (M0 -> M8)")
    print("===================================================================")
    print(f"Environment: {settings.ENV}")
    print(f"MLflow Server: {settings.MLFLOW_TRACKING_URI}")
    print(f"AWS Bedrock Region: {settings.AWS_REGION}")
    print(f"Bedrock LLM Model: {settings.BEDROCK_LLM_MODEL_ID}")
    print(f"Bedrock Embedding Model: {settings.DEFAULT_EMBEDDING_MODEL}")

    # 1. Load Dataset
    repo_root = Path(__file__).resolve().parent.parent
    processed_dir = repo_root / "data" / "processed"
    docs, queries, qrels = load_dataset(processed_dir)
    print(f"[Dataset] Total Available: {len(docs)} documents | {len(queries)} queries")

    # Map queries to gold document IDs
    query_to_gold_doc: dict[str, str] = {q.query_id: q.document_id for q in qrels}

    # 2. Select benchmark subset
    if args.full:
        selected_queries = queries
        selected_docs = docs
    else:
        selected_queries = queries[: args.num_queries]
        # Guarantee ground truth documents for all selected queries are in the corpus
        gold_doc_ids = {
            query_to_gold_doc.get(q.id) for q in selected_queries if q.id in query_to_gold_doc
        }
        needed_docs = [d for d in docs if d.id in gold_doc_ids]
        distractor_docs = [d for d in docs if d.id not in gold_doc_ids]
        target_count = max(args.num_docs, len(needed_docs))
        selected_docs = needed_docs + distractor_docs[: target_count - len(needed_docs)]

    test_cases = [
        {"query": q.text, "doc_id": query_to_gold_doc.get(q.id, "")} for q in selected_queries
    ]

    print("\n-------------------------------------------------------------------")
    print(f"  Benchmark Corpus Size: {len(selected_docs)} medical documents (competing chunks)")
    print(f"  Benchmark Query Suite: {len(test_cases)} evaluation test cases")
    print("-------------------------------------------------------------------")

    # 3. Expand Matrix
    exp_config = Path(args.config)
    if not exp_config.is_absolute():
        exp_config = repo_root / exp_config

    print(f"\n[Matrix Expander] Reading experiment config: {exp_config}")
    expander = MatrixExpander(config_path=exp_config)
    expanded_runs = expander.expand()

    print(f"[Matrix Expander] Generated {len(expanded_runs)} experiment combinations:")
    for idx, r in enumerate(expanded_runs, start=1):
        vdb = r.get("vectorstore")
        emb = r.get("embedding_model")
        strat = r.get("retrieval_strategy")
        orch = r.get("orchestration")
        print(f"  Run {idx}: DB={vdb} | Model={emb} | Strategy={strat} | Orchestration={orch}")

    exp_name = expander.config.get("experiment", {}).get("name", "linkedin_post_benchmark")

    # 4. Execute Sweep
    runner = ExperimentRunner()
    results = runner.run_sweep(
        expanded_runs=expanded_runs,
        sample_docs=selected_docs,
        test_cases=test_cases,
        experiment_name=exp_name,
    )

    # 5. Generate Production Report
    print(f"\n[Comparison Reporter] Generating report in '{args.output_dir}'...")
    reporter = ComparisonReporter(output_dir=args.output_dir)
    report_file = reporter.generate_report(results)
    print(f"[Comparison Reporter] Benchmark Report saved to: {report_file}")

    print("\n===================================================================")
    print("   BENCHMARK EXPERIMENT COMPLETED SUCCESSFULLY!")
    print(f"   View live charts in MLflow UI: {settings.MLFLOW_TRACKING_URI}")
    print("===================================================================\n")


if __name__ == "__main__":
    main()
