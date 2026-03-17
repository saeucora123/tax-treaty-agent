from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "slice3.v1"
NORMAL_CONFIDENCE_THRESHOLD = 0.95
AUTO_CONCLUSION_CONFIDENCE_THRESHOLD = 0.80
SUPPORTED_SCOPE_EXAMPLES_BY_PAIR = {
    ("CN", "NL"): [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
        "中国居民企业向荷兰公司支付特许权使用费",
    ],
    ("CN", "SG"): [
        "中国居民企业向新加坡公司支付股息",
        "中国居民企业向新加坡银行支付利息",
        "中国居民企业向新加坡公司支付特许权使用费",
    ],
}
TREATY_DISPLAY_NAMES_ZH = {
    ("CN", "NL"): "中国-荷兰税收协定",
    ("CN", "SG"): "中国-新加坡税收协定",
}
PAIR_LABELS_EN = {
    ("CN", "NL"): "China-Netherlands",
    ("CN", "SG"): "China-Singapore",
}
REVIEW_CHECKLISTS = {
    "royalties": [
        "Confirm the payment is actually for the use of, or right to use, qualifying intellectual property.",
        "Confirm the recipient is the beneficial owner of the royalty income.",
        "Check the underlying contract, invoice, and payment flow for factual consistency.",
    ],
    "dividends": [
        "Confirm the payment is legally characterized as a dividend rather than another return.",
        "Confirm the recipient is the beneficial owner of the dividend income.",
        "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
    ],
    "interest": [
        "Confirm the payment is legally characterized as interest under the financing arrangement.",
        "Confirm the recipient is the beneficial owner of the interest income.",
        "Check the loan agreement, interest calculation, and payment records for consistency.",
    ],
}
KEY_MISSING_FACTS = {
    "royalties": [
        "Whether the payment is truly for qualifying intellectual property use.",
        "Whether the recipient is the beneficial owner of the royalty income.",
        "Whether the contract and payment flow support treaty characterization.",
    ],
    "dividends": [
        "Whether the payment is legally a dividend rather than another type of return.",
        "Whether the recipient is the beneficial owner of the dividend income.",
        "Whether shareholding facts support relying on the treaty position.",
    ],
    "interest": [
        "Whether the payment is legally characterized as interest under the financing arrangement.",
        "Whether the recipient is the beneficial owner of the interest income.",
        "Whether the lending documents and payment records support the treaty characterization.",
    ],
}
TRANSACTION_KEYWORDS = {
    "royalties": [
        "特许权使用费",
        "软件许可费",
        "软件授权费",
        "技术授权费",
        "品牌费",
    ],
    "dividends": ["股息"],
    "interest": ["利息"],
}
TRANSACTION_LABELS_ZH = {
    "dividends": "股息",
    "interest": "利息",
    "royalties": "特许权使用费",
}
COUNTRY_FOOTPRINTS = {
    "CN": [
        "中国",
        "中国居民企业",
        "中国公司",
        "China",
        "Chinese",
        "PRC",
        "People's Republic of China",
        "Peoples Republic of China",
        "北京",
        "Beijing",
    ],
    "NL": [
        "荷兰",
        "荷兰公司",
        "Netherlands",
        "The Netherlands",
        "Holland",
        "Dutch",
        "阿姆斯特丹",
        "Amsterdam",
    ],
    "SG": [
        "新加坡",
        "新加坡公司",
        "Singapore",
        "Singaporean",
        "新加坡银行",
        "Singapore bank",
        "Singapore company",
    ],
    "US": ["美国", "美国公司", "United States", "USA", "Washington", "华盛顿"],
}
BOUNDARY_NOTE = (
    "This is a first-pass treaty pre-review based on limited scenario facts. "
    "Final eligibility still depends on additional facts, documents, and analysis "
    "outside the current review scope."
)
STATE_LABELS_ZH = {
    "pre_review_complete": "预审完成",
    "can_be_completed": "可补全",
    "partial_review": "预审部分完成",
    "needs_human_intervention": "需要人工介入",
    "out_of_scope": "不在支持范围",
}
FACT_VALUE_LABELS = {
    "direct_holding_confirmed": "Direct holding confirmed",
    "direct_holding_threshold_met": "Direct holding is at least 25%",
    "direct_holding_percentage": "Direct holding percentage (as of payment date)",
    "payment_date": "Dividend payment date",
    "holding_period_months": "Continuous holding period (months)",
    "pe_effectively_connected": "Dividend effectively connected with a China PE / fixed base",
    "beneficial_owner_confirmed": "Beneficial owner status separately confirmed",
    "holding_structure_is_direct": "Holding structure is direct (no intermediate entity)",
    "mli_ppt_risk_flag": "MLI PPT risk assessment performed",
    "interest_character_confirmed": "Interest characterization separately confirmed",
    "beneficial_owner_status": "Beneficial owner status separately confirmed",
    "lending_documents_consistent": "Loan documents and payment records support the interest characterization",
    "royalty_character_confirmed": "Qualifying IP royalty characterization separately confirmed",
    "contract_payment_flow_consistent": "Contract, invoice, and payment flow support the royalty characterization",
}
HANDOFF_RECOMMENDED_ROUTE_BY_STATE = {
    "pre_review_complete": "standard_review",
    "can_be_completed": "complete_facts_then_rerun",
    "partial_review": "manual_review",
    "needs_human_intervention": "manual_review",
    "out_of_scope": "out_of_scope_rewrite",
}
HANDOFF_NOTE = "This is a bounded pre-review output, not a final tax opinion."
