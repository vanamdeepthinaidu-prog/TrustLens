"""
Unit Tests for Demo Mode Orchestrator (Section 34)
"""

from pathlib import Path
from simulator.demo_orchestrator import DemoOrchestrator, DemoStepStatus


def test_demo_orchestrator_full_run(tmp_path):
    progress_updates = []

    def on_progress(state):
        progress_updates.append(state.overall_progress)

    orchestrator = DemoOrchestrator(base_dir=str(tmp_path / "demo_run"), progress_callback=on_progress)
    assert orchestrator.state.total_steps == 18
    assert orchestrator.state.status == "IDLE"

    final_state = orchestrator.run_all()
    assert final_state.status == "COMPLETED"
    assert final_state.overall_progress == 100.0
    assert len(final_state.steps) == 18
    for step in final_state.steps:
        assert step.status == DemoStepStatus.COMPLETED
        assert step.progress_percent == 100.0

    # Assert TrustScoreResult generated
    assert final_state.trust_score_result is not None
    assert 0.0 <= final_state.trust_score_result.overall_score <= 100.0

    # Assert reports generated
    assert "json" in final_state.generated_reports
    assert "pdf" in final_state.generated_reports
    assert Path(final_state.generated_reports["json"]).exists()
    assert Path(final_state.generated_reports["pdf"]).exists()

    # Assert callback received progress updates
    assert len(progress_updates) > 0
    assert progress_updates[-1] == 100.0
