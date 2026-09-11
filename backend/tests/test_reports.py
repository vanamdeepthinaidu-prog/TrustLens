"""
Unit Tests for Reports & Honest Coverage (Section 31 & Section 32)
"""

import json
from pathlib import Path
from reports.json_report import JsonReportGenerator
from reports.pdf_report import PdfReportGenerator
from app.risk.trust_engine import TrustEngine
from app.risk.schemas import EvidenceObject, Severity
from app.governance.coverage import DetectionCoverageMatrix, CoverageCategory


def test_coverage_matrix_honesty():
    summary = DetectionCoverageMatrix.get_coverage_summary()
    assert summary["supported_count"] >= 5
    assert summary["partially_supported_count"] >= 3
    assert summary["unsupported_count"] >= 3

    # Ensure unsupported items explicitly mention limitations
    unsupported = DetectionCoverageMatrix.get_capabilities_by_category(CoverageCategory.UNSUPPORTED)
    assert any("FGSM" in u.limitations or "adversarial" in u.name.lower() for u in unsupported)
    assert any("pre-sensor" in u.name.lower() or "physical" in u.name.lower() for u in unsupported)


def test_reports_generation_all_13_sections(tmp_path):
    trust_res = TrustEngine.calculate(evidence_list=[], distribution_shift_score=0.20)
    ev = EvidenceObject(
        finding_type="Potential duplicate flooding indicator",
        what_happened="Detected 5 identical copies",
        why_flagged="SHA-256 byte match",
        severity=Severity.HIGH,
        confidence=0.98,
        affected_asset="image_cluster_01",
        recommended_action="Deduplicate",
        limitations="Does not verify intent",
    )

    # 1. JSON Report
    json_path = tmp_path / "test_report.json"
    data = JsonReportGenerator.generate(
        output_path=json_path,
        trust_score=trust_res,
        evidence_list=[ev],
    )
    assert json_path.exists()

    # Verify all 13 sections exist in JSON
    for sec_num in range(1, 14):
        key_matches = [k for k in data.keys() if f"section_{sec_num}_" in k]
        assert len(key_matches) == 1, f"Missing section_{sec_num} in JSON report!"

    # 2. PDF Report
    pdf_path = tmp_path / "test_report.pdf"
    PdfReportGenerator.generate(
        output_path=pdf_path,
        trust_score=trust_res,
        evidence_list=[ev],
    )
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 500

    # Ensure valid PDF header
    with open(pdf_path, "rb") as f:
        header = f.read(10)
        assert b"%PDF" in header
