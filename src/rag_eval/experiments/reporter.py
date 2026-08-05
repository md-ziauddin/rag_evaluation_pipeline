"""
Comparison Reporter Implementation.

Formats matrix sweep metrics into markdown tables and writes production recommendation reports.
"""

from pathlib import Path
from typing import Any


class ComparisonReporter:
    """
    Formats evaluation experiment metrics into markdown reports.
    """

    def __init__(self, output_dir: str | Path = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, run_results: list[dict[str, Any]]) -> str:
        """
        Generate markdown comparison report from experiment sweep results.
        """
        if not run_results:
            return "# Medical RAG Experiment Comparison Report\n\nNo runs recorded."

        # Sort runs by NDCG@10 + Faithfulness combined score
        sorted_runs = sorted(
            run_results,
            key=lambda r: (
                r["metrics"].get("ndcg_at_10", 0.0) + r["metrics"].get("faithfulness", 0.0)
            ),
            reverse=True,
        )

        top_run = sorted_runs[0]

        report_lines = [
            "# Medical RAG Experiment Comparison Report",
            "",
            "## Executive Summary & Production Recommendation",
            "",
            f"**Recommended Production Configuration**: `{top_run['run_name']}`",
            f"- **Vector Store**: `{top_run['params'].get('vectorstore', 'N/A')}`",
            f"- **Embedding Model**: `{top_run['params'].get('embedding_model', 'N/A')}`",
            f"- **Orchestration**: `{top_run['params'].get('orchestration', 'N/A')}`",
            f"- **NDCG@10**: `{top_run['metrics'].get('ndcg_at_10', 0.0)}`",
            f"- **Faithfulness**: `{top_run['metrics'].get('faithfulness', 0.0)}`",
            f"- **Avg Latency**: `{top_run['metrics'].get('avg_latency_ms', 0.0)} ms`",
            "",
            "## Matrix Benchmark Comparison Table",
            "",
            "| Run Name | Vector Store | Embedding | Orchestration | MRR@10 | NDCG@10 | Faithfulness | Latency (ms) |",  # noqa: E501
            "|---|---|---|---|---|---|---|---|",
        ]

        for r in sorted_runs:
            name = r["run_name"]
            vdb = r["params"].get("vectorstore", "N/A")
            emb = r["params"].get("embedding_model", "N/A").split("/")[-1]
            orch = r["params"].get("orchestration", "N/A")
            mrr = r["metrics"].get("mrr_at_10", 0.0)
            ndcg = r["metrics"].get("ndcg_at_10", 0.0)
            faith = r["metrics"].get("faithfulness", 0.0)
            lat = r["metrics"].get("avg_latency_ms", 0.0)

            row = f"| `{name}` | `{vdb}` | `{emb}` | `{orch}` | `{mrr}` | `{ndcg}` | `{faith}` | `{lat}` |"  # noqa: E501
            report_lines.append(row)

        report_content = "\n".join(report_lines) + "\n"

        report_file = self.output_dir / "comparison_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        return str(report_file)
