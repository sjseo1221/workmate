import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_eval import cosine_similarity, matches_filters, percentile, rank_documents, validate_inputs
from run_postgres_eval import answerability_metrics, configure_hnsw, expand_query_terms, mode_metrics, ndcg_at_10, normalize_keyword_text, rrf_rank
from run_reranker_eval import answerability_metrics as reranker_answerability_metrics, first_relevant_rank, rank_changes, validate_decision


class EmbeddingRunnerTests(unittest.TestCase):
    def test_cosine_similarity(self):
        self.assertAlmostEqual(1.0, cosine_similarity([1.0, 0.0], [1.0, 0.0]))
        self.assertAlmostEqual(0.0, cosine_similarity([1.0, 0.0], [0.0, 1.0]))

    def test_metadata_filters(self):
        document = {"meeting_id": "m1", "meeting_date": "2026-08-08", "participant_user_ids": ["u1"]}
        self.assertTrue(matches_filters(document, {"meeting_ids": ["m1"], "participant_user_ids": ["u1"]}))
        self.assertFalse(matches_filters(document, {"date_from": "2026-08-09"}))

    def test_rank_documents(self):
        corpus = [
            {"meeting_chunk_id": "c1", "meeting_id": "m1", "meeting_date": "2026-08-08", "participant_user_ids": []},
            {"meeting_chunk_id": "c2", "meeting_id": "m2", "meeting_date": "2026-08-08", "participant_user_ids": []},
        ]
        ranked = rank_documents([1.0, 0.0], corpus, [[0.0, 1.0], [1.0, 0.0]], {})
        self.assertEqual("c2", ranked[0]["meeting_chunk_id"])

    def test_validate_inputs_rejects_unknown_chunk(self):
        corpus = [{"meeting_chunk_id": "c1"}]
        cases = [{"case_id": "q1", "relevant_chunk_ids": ["missing"], "answerable": True}]
        with self.assertRaises(ValueError):
            validate_inputs(corpus, cases)

    def test_percentile_uses_nearest_rank(self):
        self.assertEqual(2, percentile([1, 2, 3, 4], 0.50))
        self.assertEqual(4, percentile([1, 2, 3, 4], 0.95))

    def test_rrf_combines_two_rankings(self):
        vector = [{"meeting_chunk_id": "a", "score": 1}, {"meeting_chunk_id": "b", "score": 0.5}]
        keyword = [{"meeting_chunk_id": "b", "score": 1}, {"meeting_chunk_id": "a", "score": 0.5}]
        ranked = rrf_rank(vector, keyword)
        self.assertEqual(["a", "b"], [row["meeting_chunk_id"] for row in ranked[:2]])

    def test_keyword_normalization(self):
        self.assertEqual("qa 빌드 v1 2", normalize_keyword_text("  QA 빌드: v1.2  "))

    def test_ndcg_rewards_higher_relevant_result(self):
        relevant = {"answer"}
        first = [{"meeting_chunk_id": "answer"}, {"meeting_chunk_id": "other"}]
        second = list(reversed(first))
        self.assertGreater(ndcg_at_10(first, relevant), ndcg_at_10(second, relevant))

    def test_answerability_counts_false_positive_and_negative(self):
        rows = [
            {"answerable": True, "top_dense_score": 0.4},
            {"answerable": False, "top_dense_score": 0.5},
        ]
        metrics = answerability_metrics(rows, 0.45)
        self.assertEqual(1, metrics["false_negative_count"])
        self.assertEqual(1, metrics["false_positive_count"])

    def test_hnsw_rejects_invalid_ef_search(self):
        with self.assertRaises(ValueError):
            configure_hnsw(None, 0)

    def test_ranking_metrics_exclude_unanswerable_cases(self):
        rows = [
            {"answerable": True, "dense_rank": 1, "dense_ndcg_at_10": 1.0, "dense_top_5": ["answer"]},
            {"answerable": False, "dense_rank": None, "dense_ndcg_at_10": 0.0, "dense_top_5": ["noise"]},
        ]
        self.assertEqual(1.0, mode_metrics(rows, "dense")["hit_at_1"])

    def test_query_term_expansion(self):
        expanded = expand_query_terms("Low-end device shadow quality")
        self.assertIn("저사양", expanded)
        self.assertIn("그림자 품질", expanded)

    def test_reranker_decision_rejects_unknown_candidate(self):
        errors = validate_decision(
            {"answerable": True, "ranked_chunk_ids": ["unknown"]},
            ["candidate-1"],
        )
        self.assertTrue(errors)

    def test_first_relevant_rank(self):
        self.assertEqual(2, first_relevant_rank(["wrong", "answer"], {"answer"}))

    def test_reranker_metrics_can_exclude_retrieval_miss(self):
        rows = [
            {"answerable": True, "candidate_has_relevant": False, "predicted_answerable": False, "provider_error": None},
            {"answerable": False, "candidate_has_relevant": False, "predicted_answerable": False, "provider_error": None},
        ]
        metrics = reranker_answerability_metrics(rows, exclude_retrieval_misses=True)
        self.assertEqual(1, metrics["case_count"])
        self.assertEqual(1.0, metrics["accuracy"])

    def test_rank_changes_separates_retrieval_miss(self):
        rows = [
            {"answerable": True, "candidate_has_relevant": False, "baseline_rank": None, "reranker_rank": None},
            {"answerable": True, "candidate_has_relevant": True, "baseline_rank": 2, "reranker_rank": 1},
        ]
        self.assertEqual({"improved": 1, "unchanged": 0, "worsened": 0, "retrieval_miss": 1}, rank_changes(rows))


if __name__ == "__main__":
    unittest.main()
