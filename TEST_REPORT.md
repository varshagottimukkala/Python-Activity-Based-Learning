# Verification report

- Python: 3.11.2
- Studies: 10
- Executed fixtures: 60
- Passed: 60
- Failed: 0
- Syllabus issues: 0

The fixtures exercise normal input, invalid input, exact thresholds, ties, empty accepted-record sets where applicable, and arithmetic edge cases. These results cover the declared test cases; they do not claim exhaustive verification of every possible input.

| Case | Fixture | Result | Evidence |
|---|---|---|---|
| 02_electricity_billing | `01_normal` | PASS | [Actual stdout](02_electricity_billing/test_outputs/01_normal.txt) |
| 02_electricity_billing | `02_slab_boundaries` | PASS | [Actual stdout](02_electricity_billing/test_outputs/02_slab_boundaries.txt) |
| 02_electricity_billing | `03_exact_alert_boundary` | PASS | [Actual stdout](02_electricity_billing/test_outputs/03_exact_alert_boundary.txt) |
| 02_electricity_billing | `04_decrease` | PASS | [Actual stdout](02_electricity_billing/test_outputs/04_decrease.txt) |
| 02_electricity_billing | `05_invalid_inputs` | PASS | [Actual stdout](02_electricity_billing/test_outputs/05_invalid_inputs.txt) |
| 02_electricity_billing | `06_rebate_cutoff` | PASS | [Actual stdout](02_electricity_billing/test_outputs/06_rebate_cutoff.txt) |
| 13_atm_transactions | `01_normal` | PASS | [Actual stdout](13_atm_transactions/test_outputs/01_normal.txt) |
| 13_atm_transactions | `02_withdrawal_limits` | PASS | [Actual stdout](13_atm_transactions/test_outputs/02_withdrawal_limits.txt) |
| 13_atm_transactions | `03_minimum_balance` | PASS | [Actual stdout](13_atm_transactions/test_outputs/03_minimum_balance.txt) |
| 13_atm_transactions | `04_invalid_values` | PASS | [Actual stdout](13_atm_transactions/test_outputs/04_invalid_values.txt) |
| 13_atm_transactions | `05_ids_and_format` | PASS | [Actual stdout](13_atm_transactions/test_outputs/05_ids_and_format.txt) |
| 13_atm_transactions | `06_deposit_does_not_reset_limit` | PASS | [Actual stdout](13_atm_transactions/test_outputs/06_deposit_does_not_reset_limit.txt) |
| 14_warehouse_reconciliation | `01_normal` | PASS | [Actual stdout](14_warehouse_reconciliation/test_outputs/01_normal.txt) |
| 14_warehouse_reconciliation | `02_zero_and_full_dispatch` | PASS | [Actual stdout](14_warehouse_reconciliation/test_outputs/02_zero_and_full_dispatch.txt) |
| 14_warehouse_reconciliation | `03_observed_stock_basis` | PASS | [Actual stdout](14_warehouse_reconciliation/test_outputs/03_observed_stock_basis.txt) |
| 14_warehouse_reconciliation | `04_duplicates_and_impossible_movement` | PASS | [Actual stdout](14_warehouse_reconciliation/test_outputs/04_duplicates_and_impossible_movement.txt) |
| 14_warehouse_reconciliation | `05_no_valid_records` | PASS | [Actual stdout](14_warehouse_reconciliation/test_outputs/05_no_valid_records.txt) |
| 14_warehouse_reconciliation | `06_count_retry` | PASS | [Actual stdout](14_warehouse_reconciliation/test_outputs/06_count_retry.txt) |
| 16_water_tank | `01_normal` | PASS | [Actual stdout](16_water_tank/test_outputs/01_normal.txt) |
| 16_water_tank | `02_initial_threshold` | PASS | [Actual stdout](16_water_tank/test_outputs/02_initial_threshold.txt) |
| 16_water_tank | `03_threshold_never_reached` | PASS | [Actual stdout](16_water_tank/test_outputs/03_threshold_never_reached.txt) |
| 16_water_tank | `04_overflow_before_demand` | PASS | [Actual stdout](16_water_tank/test_outputs/04_overflow_before_demand.txt) |
| 16_water_tank | `05_zero_flows` | PASS | [Actual stdout](16_water_tank/test_outputs/05_zero_flows.txt) |
| 16_water_tank | `06_invalid_inputs` | PASS | [Actual stdout](16_water_tank/test_outputs/06_invalid_inputs.txt) |
| 23_timetable_conflicts | `01_normal` | PASS | [Actual stdout](23_timetable_conflicts/test_outputs/01_normal.txt) |
| 23_timetable_conflicts | `02_adjacent_sessions` | PASS | [Actual stdout](23_timetable_conflicts/test_outputs/02_adjacent_sessions.txt) |
| 23_timetable_conflicts | `03_different_rooms` | PASS | [Actual stdout](23_timetable_conflicts/test_outputs/03_different_rooms.txt) |
| 23_timetable_conflicts | `04_closure_edges` | PASS | [Actual stdout](23_timetable_conflicts/test_outputs/04_closure_edges.txt) |
| 23_timetable_conflicts | `05_invalid_sessions` | PASS | [Actual stdout](23_timetable_conflicts/test_outputs/05_invalid_sessions.txt) |
| 23_timetable_conflicts | `06_duplicate_session` | PASS | [Actual stdout](23_timetable_conflicts/test_outputs/06_duplicate_session.txt) |
| 27_numeric_diamond | `01_normal` | PASS | [Actual stdout](27_numeric_diamond/test_outputs/01_normal.txt) |
| 27_numeric_diamond | `02_minimum_size` | PASS | [Actual stdout](27_numeric_diamond/test_outputs/02_minimum_size.txt) |
| 27_numeric_diamond | `03_size_two` | PASS | [Actual stdout](27_numeric_diamond/test_outputs/03_size_two.txt) |
| 27_numeric_diamond | `04_maximum_size` | PASS | [Actual stdout](27_numeric_diamond/test_outputs/04_maximum_size.txt) |
| 27_numeric_diamond | `05_invalid_sizes` | PASS | [Actual stdout](27_numeric_diamond/test_outputs/05_invalid_sizes.txt) |
| 27_numeric_diamond | `06_symmetry` | PASS | [Actual stdout](27_numeric_diamond/test_outputs/06_symmetry.txt) |
| 29_password_validation | `01_normal` | PASS | [Actual stdout](29_password_validation/test_outputs/01_normal.txt) |
| 29_password_validation | `02_minimum_length` | PASS | [Actual stdout](29_password_validation/test_outputs/02_minimum_length.txt) |
| 29_password_validation | `03_repetition_limit` | PASS | [Actual stdout](29_password_validation/test_outputs/03_repetition_limit.txt) |
| 29_password_validation | `04_case_insensitive_substrings` | PASS | [Actual stdout](29_password_validation/test_outputs/04_case_insensitive_substrings.txt) |
| 29_password_validation | `05_invalid_format_and_characters` | PASS | [Actual stdout](29_password_validation/test_outputs/05_invalid_format_and_characters.txt) |
| 29_password_validation | `06_maximum_length` | PASS | [Actual stdout](29_password_validation/test_outputs/06_maximum_length.txt) |
| 31_answer_evaluation | `01_normal` | PASS | [Actual stdout](31_answer_evaluation/test_outputs/01_normal.txt) |
| 31_answer_evaluation | `02_ties_and_normalization` | PASS | [Actual stdout](31_answer_evaluation/test_outputs/02_ties_and_normalization.txt) |
| 31_answer_evaluation | `03_all_incorrect` | PASS | [Actual stdout](31_answer_evaluation/test_outputs/03_all_incorrect.txt) |
| 31_answer_evaluation | `04_no_valid_students` | PASS | [Actual stdout](31_answer_evaluation/test_outputs/04_no_valid_students.txt) |
| 31_answer_evaluation | `05_invalid_setup` | PASS | [Actual stdout](31_answer_evaluation/test_outputs/05_invalid_setup.txt) |
| 31_answer_evaluation | `06_classification_cutoffs` | PASS | [Actual stdout](31_answer_evaluation/test_outputs/06_classification_cutoffs.txt) |
| 42_marks_matrix | `01_normal` | PASS | [Actual stdout](42_marks_matrix/test_outputs/01_normal.txt) |
| 42_marks_matrix | `02_one_zero_mark` | PASS | [Actual stdout](42_marks_matrix/test_outputs/02_one_zero_mark.txt) |
| 42_marks_matrix | `03_one_maximum_mark` | PASS | [Actual stdout](42_marks_matrix/test_outputs/03_one_maximum_mark.txt) |
| 42_marks_matrix | `04_classification_cutoffs` | PASS | [Actual stdout](42_marks_matrix/test_outputs/04_classification_cutoffs.txt) |
| 42_marks_matrix | `05_input_retries` | PASS | [Actual stdout](42_marks_matrix/test_outputs/05_input_retries.txt) |
| 42_marks_matrix | `06_subject_and_total_ties` | PASS | [Actual stdout](42_marks_matrix/test_outputs/06_subject_and_total_ties.txt) |
| 49_product_catalogue | `01_normal` | PASS | [Actual stdout](49_product_catalogue/test_outputs/01_normal.txt) |
| 49_product_catalogue | `02_exact_decimal_arithmetic` | PASS | [Actual stdout](49_product_catalogue/test_outputs/02_exact_decimal_arithmetic.txt) |
| 49_product_catalogue | `03_invalid_prices` | PASS | [Actual stdout](49_product_catalogue/test_outputs/03_invalid_prices.txt) |
| 49_product_catalogue | `04_ids_and_quantities` | PASS | [Actual stdout](49_product_catalogue/test_outputs/04_ids_and_quantities.txt) |
| 49_product_catalogue | `05_reorder_boundary` | PASS | [Actual stdout](49_product_catalogue/test_outputs/05_reorder_boundary.txt) |
| 49_product_catalogue | `06_malformed_and_count_retry` | PASS | [Actual stdout](49_product_catalogue/test_outputs/06_malformed_and_count_retry.txt) |
