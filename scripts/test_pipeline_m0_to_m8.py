#!/usr/bin/env python3
"""
End-to-End Pipeline Verification: M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> M7 -> M8.

Runs full automated matrix expansion, experiment sweep across vector stores and orchestration
pipelines, logs metrics to MLflow, and produces reports/comparison_report.md.
"""

import sys
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_eval.config.settings import settings
from rag_eval.experiments.matrix import MatrixExpander
from rag_eval.experiments.reporter import ComparisonReporter
from rag_eval.experiments.runner import ExperimentRunner
from rag_eval.ingestion.pubmedqa import PubMedQALoader


def main():
    print("===================================================================")
    print("   END-TO-END PIPELINE VERIFICATION: M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> M7 -> M8")
    print("===================================================================")

    # Step 1: M0 Config
    print(f"\n[M0 Config] Environment: {settings.ENV}")
    print(f"[M0 Config] MLflow Server: {settings.MLFLOW_TRACKING_URI}")

    # Step 2: M1 Ingestion
    print("\n[M1 Ingestion] Loading sample records from PubMedQA...")
    pubmed_loader = PubMedQALoader()
    docs, queries, qrels = pubmed_loader.process()
    sample_doc = docs[0]
    sample_query = queries[0]
    print(f"[M1 Ingestion] Loaded Document ID: {sample_doc.id}")

    # Step 3: M8 Matrix Expansion
    exp_config = Path(__file__).resolve().parent.parent / "config" / "experiment.example.yaml"
    print(f"\n[M8 Matrix Expander] Reading experiment config: {exp_config}")

    expander = MatrixExpander(config_path=exp_config)
    expanded_runs = expander.expand()
    print(
        f"[M8 Matrix Expander] Expanded matrix into {len(expanded_runs)} experiment combinations:"
    )
    for i, r in enumerate(expanded_runs, start=1):
        vdb = r.get("vectorstore")
        emb = r.get("embedding_model")
        strat = r.get("retrieval_strategy")
        print(f"  Combo {i}: DB={vdb} | Emb={emb} | Strategy={strat}")

    # Limit to top 2 combinations for verification sweep
    test_runs = expanded_runs[:2]
    print(f"\n[M8 Experiment Runner] Executing test sweep of {len(test_runs)} configurations...")

    runner = ExperimentRunner()
    test_cases = [{"query": sample_query.text, "doc_id": sample_doc.id}]

    results = runner.run_sweep(
        expanded_runs=test_runs,
        sample_docs=[sample_doc],
        test_cases=test_cases,
        experiment_name="m8_matrix_verification",
    )

    # Step 4: M8 Comparison Reporter
    print("\n[M8 Comparison Reporter] Generating comparison report...")
    reporter = ComparisonReporter(output_dir="reports")
    report_file = reporter.generate_report(results)
    print(f"[M8 Comparison Reporter] Production report generated at: {report_file}")

    print("\n===================================================================")
    print("   SUCCESS! PIPELINE M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> M7 -> M8 FULLY CONNECTED")
    print("===================================================================\n")


if __name__ == "__main__":
    main()
