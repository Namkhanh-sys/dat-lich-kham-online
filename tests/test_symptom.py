import pytest
from src.symptom_matcher import SymptomMatcher

def test_clean_text():
    raw = "Tôi Bị Ho, Đau Họng!?"
    cleaned = SymptomMatcher.clean_text(raw)
    assert cleaned == "tôi bị ho  đau họng"

def test_match_doctors_by_symptom():
    # Symptoms in doctor d1: đau họng;ho;sổ mũi
    # Query contains "ho"
    results = SymptomMatcher.match_doctors_by_symptom("tôi bị ho kéo dài")
    assert len(results) >= 1
    # Check that doctor d1 (who has "ho") is matched with positive score
    matched_d1 = [r for r in results if r['id'] == 'd1']
    assert len(matched_d1) == 1
    assert matched_d1[0]['match_score'] > 0
    assert 'ho' in matched_d1[0]['matched_symptoms']

    # Query matching specialty directly ("nội khoa")
    results_spec = SymptomMatcher.match_doctors_by_symptom("phòng khám nội khoa ở đâu")
    matched_d2 = [r for r in results_spec if r['id'] == 'd2']
    assert len(matched_d2) == 1
    assert matched_d2[0]['match_score'] >= 2 # specialty direct match gets score 2

    # Query with no match should return all doctors with match_score = 0
    results_empty = SymptomMatcher.match_doctors_by_symptom("tôi muốn xem thông tin")
    assert len(results_empty) >= 2
    assert all(r['match_score'] == 0 for r in results_empty)
