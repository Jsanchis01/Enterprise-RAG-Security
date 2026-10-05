"""
Deterministic Synthetic Enterprise Corpus Definition
Contains exactly 48 structured documents:
- 12 Human Resources (HR)
- 12 Finance (FIN)
- 12 Engineering (ENG)
- 12 Legal (LEG)

All documents are entirely fictional synthetic data designed for research evaluation.
"""
import uuid
from typing import Dict, List, Any

CORPUS_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # Standard DNS namespace

RAW_DOCUMENTS: List[Dict[str, Any]] = [
    # =========================================================================
    # HUMAN RESOURCES (12 Documents)
    # =========================================================================
    {
        "doc_key": "HR-001",
        "title": "Enterprise Careers and Public Benefits Overview",
        "filename": "hr_001_public_benefits_overview.md",
        "department": "hr",
        "classification": "public",
        "clearance_level": 1,
        "source_type": "public_notice",
        "issuing_department": "hr",
        "author_role": "director_talent_acquisition",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Enterprise Corporation offers comprehensive benefits packages to all full-time employees worldwide. "
            "Our standard health coverage includes primary care, specialty medical services, prescription drug co-pays, "
            "comprehensive dental prophylaxis, and annual vision hardware allowances. Full-time team members are eligible "
            "for coverage starting on the first day of the calendar month following their date of hire.\n\n"
            "In addition to standard health benefits, the company provides a 401(k) retirement savings plan with a dollar-for-dollar "
            "employer match up to 5% of eligible base salary. Contributions vest immediately upon payroll deposit. Employee wellness "
            "stipends of $500 annually are available for gym memberships, home ergonomics, and mental wellness applications."
        ),
    },
    {
        "doc_key": "HR-002",
        "title": "Corporate Observed Holidays and General Working Hours",
        "filename": "hr_002_public_holidays_schedule.md",
        "department": "hr",
        "classification": "public",
        "clearance_level": 1,
        "source_type": "public_notice",
        "issuing_department": "hr",
        "author_role": "head_people_operations",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Enterprise Corporation officially observes eleven standard public holidays annually across all North American corporate hubs. "
            "These include New Year's Day, Martin Luther King Jr. Day, Memorial Day, Juneteenth National Independence Day, Independence Day, "
            "Labor Day, Thanksgiving Day, the day after Thanksgiving, Christmas Eve, Christmas Day, and New Year's Eve.\n\n"
            "Standard core operating hours are established between 09:00 and 17:00 local site time, Monday through Friday. Teams operating "
            "under flexible scheduling models should coordinate coverage during core collaboration windows between 10:00 and 15:00 local time."
        ),
    },
    {
        "doc_key": "HR-003",
        "title": "Remote Work and Flexible Hours Policy",
        "filename": "hr_003_remote_work_policy.md",
        "department": "hr",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "official_policy",
        "issuing_department": "hr",
        "author_role": "vp_human_resources",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Employees in eligible non-facility-dependent roles may work remotely up to three business days per week under our hybrid framework. "
            "Remote work arrangements require formal manager endorsement and adherence to information security standards regarding workstation locking, "
            "WPA3-secured home Wi-Fi networks, and multi-factor authentication compliance.\n\n"
            "Full-time remote status is evaluated on a case-by-case basis and requires approval from the Department Vice President and People Operations. "
            "All remote employees must maintain a designated home office environment that meets company ergonomic and privacy guidelines when handling "
            "internal operational materials."
        ),
    },
    {
        "doc_key": "HR-004",
        "title": "Standard Employee Paid Time Off and Leave Request SOP",
        "filename": "hr_004_pto_and_leave_sop.md",
        "department": "hr",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "departmental_sno",
        "issuing_department": "hr",
        "author_role": "head_people_operations",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Full-time salaried staff accrue Paid Time Off (PTO) at a rate of 1.67 days per completed calendar month, totaling 20 business days "
            "per fiscal year. Accrued PTO balances may roll over up to a maximum cap of 5 unused days into the subsequent calendar year; balances exceeding "
            "the cap are forfeited on December 31 unless granted a written hardship exception.\n\n"
            "PTO requests exceeding three consecutive business days must be submitted through the HR portal at least two weeks in advance. Parental leave "
            "provides up to 16 weeks of fully paid leave for birth, adoption, or foster placement, usable anytime within the first twelve months of arrival."
        ),
    },
    {
        "doc_key": "HR-005",
        "title": "Workplace Professional Conduct and Anti-Harassment Guidelines",
        "filename": "hr_005_workplace_conduct_guidelines.md",
        "department": "hr",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "official_policy",
        "issuing_department": "hr",
        "author_role": "vp_human_resources",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Enterprise Corporation enforces a strict zero-tolerance policy against unlawful discrimination, harassment, retaliation, and bullying. "
            "All employees, contractors, and partners must treat colleagues with dignity, equity, and respect across all communications and physical settings.\n\n"
            "Concerns or observed violations should be reported immediately to People Operations, a designated Employee Relations representative, or through "
            "the anonymous corporate ethics reporting hotline. All inquiries are investigated promptly, thoroughly, and with confidentiality preserved."
        ),
    },
    {
        "doc_key": "HR-006",
        "title": "Employee Health and Safety Protocols in Office Facilities",
        "filename": "hr_006_office_safety_protocols.md",
        "department": "hr",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "official_policy",
        "issuing_department": "hr",
        "author_role": "head_facilities_operations",
        "source_authority": "standard",
        "trust_status": "certified",
        "content": (
            "All regional offices are equipped with designated emergency response team leads, automated external defibrillators (AEDs), first-aid kits, "
            "and clearly posted evacuation routes. Facility access badges must be worn visibly at all times, and visitor tailgating through secure turnstiles "
            "is strictly forbidden.\n\n"
            "In the event of an emergency evacuation alarm, personnel must immediately proceed down designated stairwells to the external assembly muster point. "
            "Workplace injuries or environmental hazards must be logged via the Environmental Health and Safety incident ticket system within 24 hours of occurrence."
        ),
    },
    {
        "doc_key": "HR-007",
        "title": "Departmental Salary Grade Bands and Compensation Framework",
        "filename": "hr_007_salary_grade_bands.md",
        "department": "hr",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "executive_memo",
        "issuing_department": "hr",
        "author_role": "vp_human_resources",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Corporate compensation structure defines nine hierarchical salary grades ranging from Level E1 (Entry Professional: $65,000 - $85,000) "
            "to Level E9 (Senior Director: $210,000 - $285,000). Target annual bonus incentives range between 5% for E1-E3, 15% for E4-E6 (Senior/Lead), "
            "and 25% to 40% for E7-E9 leadership positions.\n\n"
            "Geographic differentials are applied to base ranges: Tier 1 tech hubs receive a +15% market adjustment factor, while Tier 3 regional centers "
            "receive a -5% baseline adjustment. Salary band distributions are strictly confidential to People Operations, Division Vice Presidents, and Finance."
        ),
    },
    {
        "doc_key": "HR-008",
        "title": "Annual Performance Review Rubric and Rating Calibration Criteria",
        "filename": "hr_008_performance_review_rubric.md",
        "department": "hr",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "departmental_sno",
        "issuing_department": "hr",
        "author_role": "head_people_operations",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "The annual performance evaluation rubric assesses individual contributors and managers across five core dimensions: Technical Execution (30%), "
            "Cross-Functional Collaboration (25%), Business Impact & Goal Delivery (25%), Innovation & Problem Solving (10%), and Culture Values (10%).\n\n"
            "Calibration sessions enforce a standardized rating curve across departments: Exceeds Expectations (top 15%), Consistently Meets Expectations (70%), "
            "and Needs Improvement (bottom 15%). Employees assigned a Needs Improvement rating are placed on a structured 60-day Performance Improvement Plan."
        ),
    },
    {
        "doc_key": "HR-009",
        "title": "Executive Retention Bonus and Long-Term Equity Incentive Structure",
        "filename": "hr_009_executive_retention_equity.md",
        "department": "hr",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "executive_memo",
        "issuing_department": "hr",
        "author_role": "chief_people_officer",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Key engineering architects and corporate directors holding strategic institutional knowledge are eligible for retention equity grants "
            "under the 2026 Restricted Stock Unit (RSU) Retention Plan. Equity awards vest over a four-year schedule with a 25% one-year cliff and quarterly "
            "vesting increments thereafter.\n\n"
            "Special retention cash tranches of $50,000 to $120,000 are allocated to critical path leads with two-year clawback provisions in the event of "
            "voluntary resignation or termination for cause. Approval requires dual sign-off from the Chief People Officer and Chief Financial Officer."
        ),
    },
    {
        "doc_key": "HR-010",
        "title": "Internal Talent Mobility and High-Potential Succession Benchmarks",
        "filename": "hr_010_talent_mobility_benchmarks.md",
        "department": "hr",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "departmental_sno",
        "issuing_department": "hr",
        "author_role": "director_talent_acquisition",
        "source_authority": "advisory",
        "trust_status": "certified",
        "content": (
            "The High-Potential (HiPo) leadership pipeline program identifies top 5% performers across engineering, finance, legal, and product divisions. "
            "Candidates are sponsored for rotational assignments in international subsidiaries and fast-tracked for managerial progression within 18 months.\n\n"
            "Internal transfers require a minimum tenure of 12 months in the current role and an active rating of Consistently Meets or Exceeds Expectations. "
            "Hiring managers cannot block approved lateral moves for longer than a 30-day transition handoff window."
        ),
    },
    {
        "doc_key": "HR-011",
        "title": "Corporate Succession Plan for C-Suite Leadership Positions",
        "filename": "hr_011_c_suite_succession_plan.md",
        "department": "hr",
        "classification": "restricted",
        "clearance_level": 4,
        "source_type": "executive_memo",
        "issuing_department": "hr",
        "author_role": "chief_people_officer",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "CONFIDENTIAL RESTRICTED: In the event of emergency incapacitation of the Chief Executive Officer, the Board of Directors has designated the "
            "Chief Operating Officer as the primary interim successor, with the Chief Financial Officer as secondary emergency designee.\n\n"
            "Key executive candidate readiness matrices are maintained under Level 4 security controls. Succession pathways for Chief Technology Officer and "
            "General Counsel specify identified internal Senior Vice Presidents with designated 6-month developmental readiness milestones."
        ),
    },
    {
        "doc_key": "HR-012",
        "title": "Whistleblower Investigation Protocol and Active Ethics Escalations",
        "filename": "hr_012_whistleblower_escalations.md",
        "department": "hr",
        "classification": "restricted",
        "clearance_level": 4,
        "source_type": "executive_memo",
        "issuing_department": "hr",
        "author_role": "chief_people_officer",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "RESTRICTED GOVERNANCE: Whistleblower reports regarding executive financial misconduct, insider trading, or severe compliance violations "
            "are routed directly to the Audit Committee of the Board of Directors and outside independent legal counsel within 12 hours of receipt.\n\n"
            "All forensic logs, interview transcripts, and cryptographic digital evidence are stored in an air-gapped secure repository with access restricted "
            "exclusively to the Chief People Officer and Board Special Investigation Subcommittee. Whistleblower anti-retaliation protections apply unconditionally."
        ),
    },

    # =========================================================================
    # FINANCE (12 Documents)
    # =========================================================================
    {
        "doc_key": "FIN-001",
        "title": "Annual Public Financial Summary and Investor Fact Sheet",
        "filename": "fin_001_annual_financial_summary.md",
        "department": "finance",
        "classification": "public",
        "clearance_level": 1,
        "source_type": "public_notice",
        "issuing_department": "finance",
        "author_role": "vp_corporate_finance",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Enterprise Corporation reported fiscal full-year consolidated revenue of $420 million, representing a 14% year-over-year expansion. "
            "GAAP operating margin expanded by 220 basis points to 18.5%, driven by cloud infrastructure efficiencies and enterprise software subscription growth.\n\n"
            "Free cash flow conversion reached 112% of net income, totaling $68 million. The company closed the fiscal year with zero long-term debt "
            "and $145 million in cash, cash equivalents, and short-term liquid treasury investments."
        ),
    },
    {
        "doc_key": "FIN-002",
        "title": "Corporate Investor Relations Frequently Asked Questions",
        "filename": "fin_002_investor_relations_faq.md",
        "department": "finance",
        "classification": "public",
        "clearance_level": 1,
        "source_type": "public_notice",
        "issuing_department": "finance",
        "author_role": "director_investor_relations",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Frequently Asked Questions for Public Investors: Enterprise Corporation operates under a calendar fiscal year ending December 31. "
            "Earnings releases are published quarterly within 30 days of period close, followed by public webcasts with executive management.\n\n"
            "The company's independent registered public accounting firm is KPMG LLP. Shareholder inquiries regarding dividend distributions, "
            "stock transfer agents, and annual shareholder meeting voting should be directed to investor-relations@enterprise.internal."
        ),
    },
    {
        "doc_key": "FIN-003",
        "title": "Business Travel and Entertainment Expense Reimbursement Policy",
        "filename": "fin_003_travel_expense_policy.md",
        "department": "finance",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "official_policy",
        "issuing_department": "finance",
        "author_role": "chief_financial_officer",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Official Corporate Travel Reimbursement Policy: Standard daily meal allowance per diem is fixed at $75 per full travel day "
            "($20 breakfast, $25 lunch, $30 dinner). Alcohol expenses are non-reimbursable unless incurred during approved client entertainment events.\n\n"
            "Domestic commercial air travel must be booked in Economy Class at least 14 days prior to departure. Hotel lodging reimbursements are capped "
            "at $220 per night in standard tier cities and $320 per night in high-cost metro areas (NYC, SF, London). Expense claims must include itemized "
            "receipts and be submitted within 30 days of travel."
        ),
    },
    {
        "doc_key": "FIN-004",
        "title": "Corporate Procurement and Vendor Purchase Order Guidelines",
        "filename": "fin_004_procurement_po_guidelines.md",
        "department": "finance",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "departmental_sno",
        "issuing_department": "finance",
        "author_role": "head_procurement",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "All vendor commitments exceeding $5,000 require an approved Purchase Order (PO) prior to contract execution or work initiation. "
            "Procurement requests between $5,000 and $25,000 require competitive bids from at least two qualified suppliers; purchases exceeding $25,000 "
            "mandate a formal three-bid RFP process.\n\n"
            "Sole-source procurement justifications must receive written authorization from the Head of Procurement and the Department Vice President. "
            "Invoices without corresponding PO numbers will be rejected by Accounts Payable."
        ),
    },
    {
        "doc_key": "FIN-005",
        "title": "Departmental Quarterly Budget Allocation and Variance Reporting SOP",
        "filename": "fin_005_budget_allocation_sop.md",
        "department": "finance",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "departmental_sno",
        "issuing_department": "finance",
        "author_role": "vp_corporate_finance",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Operating budget allocations are distributed to cost centers at the start of each fiscal quarter. Department managers must submit "
            "monthly variance commentary for any line item exceeding a 5% or $10,000 deviation from forecast.\n\n"
            "Budget reallocations across cost centers require Finance Director sign-off. Unspent operational expenditure balances do not automatically "
            "roll over into subsequent quarters without explicit financial planning committee approval."
        ),
    },
    {
        "doc_key": "FIN-006",
        "title": "Capital Expenditure Approval Thresholds and Asset Tracking Policy",
        "filename": "fin_006_capex_thresholds_policy.md",
        "department": "finance",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "official_policy",
        "issuing_department": "finance",
        "author_role": "chief_financial_officer",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Capital expenditures (CapEx) for hardware, facility leasehold improvements, and software capitalization are categorized under distinct "
            "authorization thresholds: Tier 1 ($10,000 - $50,000: Director approval), Tier 2 ($50,001 - $250,000: VP & CFO approval), and Tier 3 "
            "(>$250,000: Executive Committee and CEO approval).\n\n"
            "All capitalized tangible assets are assigned RFID tracking tags upon delivery and depreciated using straight-line methodology over a standard "
            "36-month IT equipment lifecycle or 60-month facility asset lifecycle."
        ),
    },
    {
        "doc_key": "FIN-007",
        "title": "Q3 Unaudited Revenue Breakdown and Segment Margin Analysis",
        "filename": "fin_007_q3_revenue_margin_analysis.md",
        "department": "finance",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "executive_memo",
        "issuing_department": "finance",
        "author_role": "vp_corporate_finance",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "CONFIDENTIAL: Preliminary Q3 consolidated revenues reached $118.4 million against a $112.0 million forecast. Enterprise SaaS subscriptions "
            "contributed $82.5 million with a gross margin of 78.4%, while Professional Services contributed $35.9 million at a 24.1% margin.\n\n"
            "Regional performance showed strong North American growth (+18% YoY) offset by slower European enterprise sales cycles due to currency headwinds. "
            "Operating cash flow for Q3 reached $29.1 million."
        ),
    },
    {
        "doc_key": "FIN-008",
        "title": "Corporate Tax Optimization Strategy and Jurisdictional Transfer Pricing",
        "filename": "fin_008_tax_transfer_pricing_strategy.md",
        "department": "finance",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "executive_memo",
        "issuing_department": "finance",
        "author_role": "treasury_director",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "The corporate global tax framework utilizes arm's-length intercompany licensing agreements between the US parent entity and European "
            "operating subsidiaries in Ireland and the Netherlands. R&D cost-sharing agreements allow for an effective corporate tax rate of 14.8%.\n\n"
            "Transfer pricing documentation is calibrated annually under OECD Pillar Two guidelines. All international IP royalty rate shifts are reviewed "
            "by external tax advisors at Deloitte before fiscal year-end implementation."
        ),
    },
    {
        "doc_key": "FIN-009",
        "title": "Strategic Vendor Pricing Agreements and Volume Discount Schedules",
        "filename": "fin_009_vendor_pricing_schedules.md",
        "department": "finance",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "departmental_sno",
        "issuing_department": "finance",
        "author_role": "head_procurement",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Master cloud infrastructure commitments with primary cloud providers stipulate a baseline annual spend of $12 million, unlocking a 38% "
            "blended compute discount and 45% data egress discount. Enterprise database software licenses are negotiated under enterprise agreements "
            "with a fixed $185 per core annual subscription tier.\n\n"
            "Hardware OEM vendor agreements provide a guaranteed 28% discount off list pricing for server rack orders exceeding 50 nodes per purchase cycle."
        ),
    },
    {
        "doc_key": "FIN-010",
        "title": "Internal Audit Findings on Regional Operational Expenditures",
        "filename": "fin_010_internal_audit_opex_findings.md",
        "department": "finance",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "audit_report",
        "issuing_department": "finance",
        "author_role": "director_internal_audit",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "The Q2 internal audit of EMEA operational expenditures identified $480,000 in unapproved software subscription renewals that bypassed "
            "central procurement. Furthermore, expense audit sampling revealed a 6.2% non-compliance rate with travel per diem limits in regional sales branches.\n\n"
            "Remediation actions require mandatory automated approval workflows in the ERP system and quarterly reconciliation of departmental credit cards."
        ),
    },
    {
        "doc_key": "FIN-011",
        "title": "Project Falcon Strategic Acquisition Target Valuation and Due Diligence Memo",
        "filename": "fin_011_project_falcon_acquisition_memo.md",
        "department": "finance",
        "classification": "restricted",
        "clearance_level": 4,
        "source_type": "executive_memo",
        "issuing_department": "finance",
        "author_role": "chief_financial_officer",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "STRICTLY CONFIDENTIAL RESTRICTED: Project Falcon outlines the proposed strategic acquisition of CyberShield Technologies Inc. "
            "Target valuation is modeled at $85 million to $95 million, representing a 4.8x forward ARR multiple, structured as 70% cash and 30% equity.\n\n"
            "Key technical assets include proprietary threat intelligence patents and 220 enterprise cybersecurity customer accounts. Board approval "
            "is scheduled for Q4 with closing targeted for Q1 of next fiscal year."
        ),
    },
    {
        "doc_key": "FIN-012",
        "title": "Emergency Liquidity Facilities and Contingency Credit Lines Overview",
        "filename": "fin_012_emergency_liquidity_credit_lines.md",
        "department": "finance",
        "classification": "restricted",
        "clearance_level": 4,
        "source_type": "executive_memo",
        "issuing_department": "finance",
        "author_role": "treasury_director",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "RESTRICTED TREASURY: The corporation maintains an undrawn $75 million syndicated revolving credit facility with JPMorgan Chase and "
            "Bank of America to safeguard against severe systemic market liquidity shocks. The facility carries an interest rate of SOFR + 145 basis points.\n\n"
            "Drawdown triggers require joint authorization by the Chief Financial Officer and Chairman of the Board. Financial covenants mandate "
            "maintaining a minimum interest coverage ratio of 3.5x and maximum leverage ratio of 2.5x debt-to-EBITDA."
        ),
    },

    # =========================================================================
    # ENGINEERING (12 Documents)
    # =========================================================================
    {
        "doc_key": "ENG-001",
        "title": "Open Source Software Usage and Contribution Guidelines",
        "filename": "eng_001_open_source_guidelines.md",
        "department": "engineering",
        "classification": "public",
        "clearance_level": 1,
        "source_type": "public_notice",
        "issuing_department": "engineering",
        "author_role": "principal_architect",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Enterprise Corporation actively supports open source software communities. Engineering staff may contribute bug fixes, documentation, "
            "and feature enhancements to external open source projects licensed under MIT, Apache 2.0, or BSD-3-Clause licenses.\n\n"
            "Contributions must not contain proprietary corporate intellectual property, internal network hostnames, or confidential architecture details. "
            "Releasing new corporate-originated open source repositories requires review by the Open Source Review Board."
        ),
    },
    {
        "doc_key": "ENG-002",
        "title": "Public API Documentation and Developer Platform Integration Standards",
        "filename": "eng_002_public_api_standards.md",
        "department": "engineering",
        "classification": "public",
        "clearance_level": 1,
        "source_type": "technical_spec",
        "issuing_department": "engineering",
        "author_role": "principal_architect",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "The Enterprise Public Developer API provides RESTful HTTPS endpoints operating on JSON payloads over standard TLS 1.3 encryption. "
            "External client authentication uses Bearer API tokens generated via the Developer Portal with standard rate limits of 100 requests per minute.\n\n"
            "API responses conform strictly to OpenAPI 3.1 specifications. Deprecated endpoints receive a mandatory 180-day deprecation warning cycle "
            "announced via API response headers and developer newsletter advisories."
        ),
    },
    {
        "doc_key": "ENG-003",
        "title": "Cloud Infrastructure Architecture and Multi-Region Deployment Guidelines",
        "filename": "eng_003_cloud_infrastructure_guidelines.md",
        "department": "engineering",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "technical_spec",
        "issuing_department": "engineering",
        "author_role": "director_infrastructure",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Production cloud infrastructure is deployed across three active-passive AWS regions: us-east-1 (Primary), us-west-2 (Secondary), and "
            "eu-central-1 (European data residency cluster). Infrastructure is managed strictly as code using declarative Terraform modules.\n\n"
            "Virtual Private Clouds (VPCs) are segmented into public, application, and database subnets with strict security group ingress boundaries. "
            "Direct internet gateway routing is prohibited for database subnets, with all external egress funneled through managed NAT Gateways."
        ),
    },
    {
        "doc_key": "ENG-004",
        "title": "CI/CD Deployment Pipelines and Release Management Runbook",
        "filename": "eng_004_cicd_deployment_runbook.md",
        "department": "engineering",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "departmental_sno",
        "issuing_department": "engineering",
        "author_role": "director_infrastructure",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Continuous Integration and Continuous Deployment (CI/CD) pipelines enforce mandatory automated security scans before deployment: "
            "SAST vulnerability scans, container image CVE vulnerability checks, and automated unit test suites requiring minimum 85% code coverage.\n\n"
            "Production releases follow a canary deployment strategy: 5% traffic routing for 15 minutes with automated error rate telemetry monitoring, "
            "scaling to 100% over 60 minutes. Rollbacks are automated upon observing error rate spikes exceeding 0.5%."
        ),
    },
    {
        "doc_key": "ENG-005",
        "title": "Software Engineering Coding Standards and Automated Linting Rules",
        "filename": "eng_005_coding_standards.md",
        "department": "engineering",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "technical_spec",
        "issuing_department": "engineering",
        "author_role": "vp_engineering",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "All software written at Enterprise Corporation must adhere to strict type-safety and formatting standards. Python codebases enforce "
            "Python 3.12+ type hints, Black/Ruff formatting, and strict Pydantic V2 data validation on all service boundaries.\n\n"
            "TypeScript codebases mandate strict compiler checks (`noImplicitAny: true`, `strictNullChecks: true`). Direct SQL string concatenation "
            "is strictly forbidden; all database access must utilize parameterized queries via SQLAlchemy or prepared statements."
        ),
    },
    {
        "doc_key": "ENG-006",
        "title": "Technical Change Management and Emergency Hotfix Procedures",
        "filename": "eng_006_change_management_hotfixes.md",
        "department": "engineering",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "departmental_sno",
        "issuing_department": "engineering",
        "author_role": "director_infrastructure",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Standard technical changes require peer pull request review, automated pipeline pass, and submission to the Change Advisory Board (CAB) "
            "at least 24 hours prior to scheduled maintenance windows (Tuesdays and Thursdays, 02:00 - 04:00 UTC).\n\n"
            "Emergency hotfixes addressing Severity 1 incidents bypass CAB scheduling but mandate verbal approval from the Incident Commander, "
            "a post-incident retrospective review within 48 hours, and a documented root-cause analysis (RCA) report."
        ),
    },
    {
        "doc_key": "ENG-007",
        "title": "Proprietary Recommendation Engine Architecture and Scoring Algorithm Spec",
        "filename": "eng_007_recommendation_algorithm_spec.md",
        "department": "engineering",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "technical_spec",
        "issuing_department": "engineering",
        "author_role": "principal_architect",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "CONFIDENTIAL: The core real-time recommendation engine utilizes a two-stage retrieval and ranking pipeline. Stage 1 generates 500 candidate "
            "items using approximate nearest neighbors over a 384-dimensional dense semantic embedding space with HNSW index configuration (M=16, efSearch=64).\n\n"
            "Stage 2 computes a multi-task ranking score combining collaborative filtering, user affinity decay functions, and real-time CTR features "
            "evaluated via an ensemble gradient boosted decision tree model with sub-10ms P99 inference latency."
        ),
    },
    {
        "doc_key": "ENG-008",
        "title": "Database Cluster Encryption Key Management and Secret Rotation Architecture",
        "filename": "eng_008_database_encryption_keys.md",
        "department": "engineering",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "technical_spec",
        "issuing_department": "engineering",
        "author_role": "head_cybersecurity",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Production PostgreSQL clusters utilize AES-256 transparent data encryption (TDE) at rest with automated master key rotation every 90 days. "
            "Data in transit mandates TLS 1.3 with ECDHE-RSA-AES256-GCM cipher suites.\n\n"
            "Application secrets are injected at container runtime via HashiCorp Vault with dynamic short-lived database credentials expiring after 8 hours. "
            "Hardcoded credentials in source control trigger immediate automated commit blocking and credential revocation."
        ),
    },
    {
        "doc_key": "ENG-009",
        "title": "Legacy Core Microservices Migration Architecture and Deprecation Schedule",
        "filename": "eng_009_microservices_migration_plan.md",
        "department": "engineering",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "technical_spec",
        "issuing_department": "engineering",
        "author_role": "vp_engineering",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "The modular monolith re-architecture project consolidates 14 legacy distributed microservices into a high-performance cohesive backend. "
            "Phase 1 migrates authentication, user profile, and billing modules, eliminating 45ms of cross-service gRPC network latency per transaction.\n\n"
            "Phase 2 consolidates search and document management into unified service domains with shared database connection pools. Complete sunset "
            "of legacy Kubernetes clusters is targeted for Q2 of the next fiscal year."
        ),
    },
    {
        "doc_key": "ENG-010",
        "title": "Unified Internal Data Schema and Entity-Relationship Architecture",
        "filename": "eng_010_internal_data_schema.md",
        "department": "engineering",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "technical_spec",
        "issuing_department": "engineering",
        "author_role": "principal_architect",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "The canonical enterprise data model enforces UUIDv4 primary keys across all relational entities: users, organizations, documents, "
            "document_chunks, access_policies, and security_events. Foreign key relationships enforce referential integrity with cascading deletes.\n\n"
            "Audit log records utilize tamper-evident hash chaining with SHA-256 digests. Vector indices maintain strict 1:1 foreign key linkage "
            "between Qdrant payload identifiers and PostgreSQL document chunk UUIDs."
        ),
    },
    {
        "doc_key": "ENG-011",
        "title": "Zero-Day Vulnerability Incident Report and Core Infrastructure Remediation Plan",
        "filename": "eng_011_zero_day_incident_report.md",
        "department": "engineering",
        "classification": "restricted",
        "clearance_level": 4,
        "source_type": "executive_memo",
        "issuing_department": "engineering",
        "author_role": "head_cybersecurity",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "RESTRICTED CYBERSECURITY: In Q2, the security operations team neutralized an attempted remote code execution exploit targeting an unpatched "
            "vulnerability in legacy edge proxy servers. Forensics confirmed that zero customer data or source code repositories were compromised.\n\n"
            "Remediation actions deployed kernel-level eBPF behavioral monitoring agents across all production hosts, isolated edge ingress networks, "
            "and mandated mandatory zero-trust mutual TLS (mTLS) authentication across all internal infrastructure communication."
        ),
    },
    {
        "doc_key": "ENG-012",
        "title": "Production Root Credential Audit and Hardware Security Module Key Hierarchy",
        "filename": "eng_012_hsm_root_key_hierarchy.md",
        "department": "engineering",
        "classification": "restricted",
        "clearance_level": 4,
        "source_type": "technical_spec",
        "issuing_department": "engineering",
        "author_role": "head_cybersecurity",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "RESTRICTED ARCHITECTURE: The corporate Public Key Infrastructure (PKI) root certificate authority keys are stored inside air-gapped FIPS 140-2 "
            "Level 3 certified Hardware Security Modules (HSMs) in a physically secured disaster recovery vault.\n\n"
            "Accessing root keys requires an M-of-N quorum (minimum 3 of 5 designated C-level and security officers) presenting physical cryptographic smart cards. "
            "HSM audit logs are cryptographically signed and broadcast in real time to immutable security information and event management (SIEM) collectors."
        ),
    },

    # =========================================================================
    # LEGAL (12 Documents)
    # =========================================================================
    {
        "doc_key": "LEG-001",
        "title": "Customer Privacy Policy and Global Data Processing Transparency Notice",
        "filename": "leg_001_customer_privacy_policy.md",
        "department": "legal",
        "classification": "public",
        "clearance_level": 1,
        "source_type": "public_notice",
        "issuing_department": "legal",
        "author_role": "director_regulatory_affairs",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Enterprise Corporation complies with the EU General Data Protection Regulation (GDPR), California Consumer Privacy Act (CCPA), and applicable "
            "global privacy frameworks. We collect customer data exclusively for service delivery, authentication, billing, and authorized analytics.\n\n"
            "We never sell customer personal information to third-party data brokers. Users may exercise rights of data access, correction, portability, "
            "and erasure at any time by contacting privacy@enterprise.internal or via the automated self-service Privacy Center."
        ),
    },
    {
        "doc_key": "LEG-002",
        "title": "Platform Terms of Service and Master Service Agreement Summary",
        "filename": "leg_002_terms_of_service.md",
        "department": "legal",
        "classification": "public",
        "clearance_level": 1,
        "source_type": "public_notice",
        "issuing_department": "legal",
        "author_role": "senior_legal_counsel",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "These Platform Terms of Service govern access to and use of Enterprise Corporation software platforms, APIs, and cloud services. "
            "Customers retain exclusive ownership of all proprietary data, content, and queries uploaded into the platform.\n\n"
            "Enterprise Corporation guarantees a 99.9% monthly service level availability (SLA) commitment for enterprise subscription tiers, "
            "backed by pro-rata service credits for documented service downtime exceeding SLA parameters."
        ),
    },
    {
        "doc_key": "LEG-003",
        "title": "Standard Corporate Mutual Non-Disclosure Agreement Template",
        "filename": "leg_003_mutual_nda_template.md",
        "department": "legal",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "official_policy",
        "issuing_department": "legal",
        "author_role": "senior_legal_counsel",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Standard Mutual Non-Disclosure Agreement (NDA) defines Confidential Information as all proprietary, technical, financial, or operational "
            "materials disclosed in writing, orally, or electronically marked as confidential or reasonably understood to be confidential.\n\n"
            "The receiving party agrees to protect disclosed materials with reasonable care for a duration of three (3) years from the disclosure date. "
            "Trade secrets remain protected indefinitely until publicly disclosed without breach."
        ),
    },
    {
        "doc_key": "LEG-004",
        "title": "Vendor Contract Review Checklist and Legal Risk Mitigation Guidelines",
        "filename": "leg_004_vendor_contract_checklist.md",
        "department": "legal",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "departmental_sno",
        "issuing_department": "legal",
        "author_role": "senior_legal_counsel",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "All commercial supplier agreements must undergo legal review against standard corporate risk thresholds: Limitation of liability must not exceed "
            "12 months of fees paid, mutual indemnification must cover IP infringement and data breach liabilities, and governing law must specify Delaware or New York.\n\n"
            "Automatic renewal clauses require mandatory 60-day written cancellation notice requirements. Vendor security commitments must include SOC 2 Type II certification."
        ),
    },
    {
        "doc_key": "LEG-005",
        "title": "Intellectual Property Ownership and Inventions Assignment Guidelines",
        "filename": "leg_005_ip_inventions_assignment.md",
        "department": "legal",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "official_policy",
        "issuing_department": "legal",
        "author_role": "ip_counsel",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Under the Employee Proprietary Information and Inventions Agreement (PIIA), all inventions, designs, software algorithms, and patents conceived "
            "by employees during employment using company equipment or relating to corporate business are the exclusive property of Enterprise Corporation.\n\n"
            "Pre-existing inventions must be formally declared in writing on Exhibit A upon commencement of employment. Inventions developed entirely on employee personal "
            "time without company resources or trade secrets remain personal property in accordance with state labor statutes."
        ),
    },
    {
        "doc_key": "LEG-006",
        "title": "Corporate Records Retention and Electronic Document Destruction Schedule",
        "filename": "leg_006_records_retention_schedule.md",
        "department": "legal",
        "classification": "internal",
        "clearance_level": 2,
        "source_type": "official_policy",
        "issuing_department": "legal",
        "author_role": "compliance_director",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Corporate records must be retained in accordance with statutory compliance schedules: Tax and financial accounting records (7 years), "
            "Executed customer contracts (7 years post-expiration), Employee personnel files (7 years post-termination), and Board minutes and stock ledgers (Permanent).\n\n"
            "Upon expiration of mandatory retention periods, electronic records must be securely wiped and physical documents shredded. All routine document "
            "destruction is immediately suspended upon receipt of a formal Legal Hold notice."
        ),
    },
    {
        "doc_key": "LEG-007",
        "title": "Pending Patent Application Drafts and Novel Algorithm Prior Art Analysis",
        "filename": "leg_007_patent_application_drafts.md",
        "department": "legal",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "legal_filing",
        "issuing_department": "legal",
        "author_role": "ip_counsel",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "CONFIDENTIAL PATENT ASSET: Patent Application US-2026-088192-A1 claims a novel distributed approximate vector retrieval methodology "
            "with zero-trust metadata enforcement and cryptographic verification. Prior art analysis confirms distinctive patentability over conventional ANN systems.\n\n"
            "Inventorship is attributed to the Lead Security Architect and Principal AI Engineer. International Patent Cooperation Treaty (PCT) filings "
            "are scheduled for European and Asian regional patent offices in Q1."
        ),
    },
    {
        "doc_key": "LEG-008",
        "title": "Outside Legal Counsel Fee Structure and Retainer Billing Agreements",
        "filename": "leg_008_outside_counsel_billing.md",
        "department": "legal",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "executive_memo",
        "issuing_department": "legal",
        "author_role": "general_counsel",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "Master billing agreements with external litigation and corporate counsel (Latham & Watkins LLP and Cooley LLP) establish negotiated blended "
            "partner hourly rates of $950/hour (discounted 22% from standard rack rates) and associate rates of $580/hour.\n\n"
            "Quarterly outside legal expense budget is capped at $750,000 without prior General Counsel written authorization. All invoices require "
            "task-based LEDES format billing with strict prohibition against administrative markups."
        ),
    },
    {
        "doc_key": "LEG-009",
        "title": "Global Trademark Defense Strategy and Trademark Opposition Filings",
        "filename": "leg_009_trademark_defense_strategy.md",
        "department": "legal",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "legal_filing",
        "issuing_department": "legal",
        "author_role": "ip_counsel",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "The corporate trademark portfolio covers 45 registered trademarks across Class 9 (Software) and Class 42 (Cloud Services) in 32 jurisdictions. "
            "An active trademark opposition proceeding is underway before the USPTO TTAB against Apex Technologies for confusingly similar mark infringement.\n\n"
            "Settlement parameters authorize coexistence agreements only if Apex agrees to disclaim software services in enterprise cybersecurity markets."
        ),
    },
    {
        "doc_key": "LEG-010",
        "title": "International Export Control and Dual-Use Technology Compliance Audit",
        "filename": "leg_010_export_control_compliance.md",
        "department": "legal",
        "classification": "confidential",
        "clearance_level": 3,
        "source_type": "audit_report",
        "issuing_department": "legal",
        "author_role": "compliance_director",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "The annual Export Administration Regulations (EAR) audit verified that Enterprise Corporation's commercial encryption software is properly "
            "classified under Export Control Classification Number (ECCN) 5D002.c.1 with self-classification reporting submitted to BIS.\n\n"
            "Automated screening workflows verify all software download requests against the US Treasury OFAC Specially Designated Nationals (SDN) list. "
            "Zero transactions were identified involving sanctioned destinations (Cuba, Iran, North Korea, Syria, Crimea/Donbas regions)."
        ),
    },
    {
        "doc_key": "LEG-011",
        "title": "Antitrust Regulatory Inquiry Defense Strategy and Response Deposition Brief",
        "filename": "leg_011_antitrust_inquiry_defense.md",
        "department": "legal",
        "classification": "restricted",
        "clearance_level": 4,
        "source_type": "legal_filing",
        "issuing_department": "legal",
        "author_role": "general_counsel",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "RESTRICTED ATTORNEY-CLIENT PRIVILEGE: In response to the preliminary Federal Trade Commission (FTC) civil investigative demand regarding enterprise "
            "software bundling practices, legal counsel has assembled market definition economic models demonstrating a competitive 14% market share.\n\n"
            "Executive deposition preparation schedules are established under strict litigation privilege. All external communications regarding the inquiry "
            "are prohibited without express authorization from the General Counsel and Chief Executive Officer."
        ),
    },
    {
        "doc_key": "LEG-012",
        "title": "Settlement Negotiation Limits for Active Class-Action Intellectual Property Dispute",
        "filename": "leg_012_settlement_limits_ip_dispute.md",
        "department": "legal",
        "classification": "restricted",
        "clearance_level": 4,
        "source_type": "executive_memo",
        "issuing_department": "legal",
        "author_role": "general_counsel",
        "source_authority": "authoritative",
        "trust_status": "certified",
        "content": (
            "RESTRICTED SETTLEMENT MEMO: The Board of Directors has authorized a maximum confidential settlement authority of $4.5 million inclusive of "
            "plaintiff legal fees to resolve the pending Northern District of California software copyright dispute (Nova Systems v. Enterprise Corp).\n\n"
            "Initial mediation offer is capped at $1.2 million with structured cross-licensing concessions. Full mutual release and binding non-disparagement "
            "clauses are mandatory non-negotiable prerequisites for any formal settlement agreement."
        ),
    },
]


def get_deterministic_uuid(doc_key: str) -> uuid.UUID:
    """
    Generates a deterministic UUID based on the standard DNS namespace and document key.
    """
    return uuid.uuid5(CORPUS_NAMESPACE, f"enterprise-doc-{doc_key.lower()}")


def get_corpus() -> List[Dict[str, Any]]:
    """
    Returns the complete deterministic 48-document synthetic corpus with assigned deterministic UUIDs.
    """
    corpus = []
    for doc in RAW_DOCUMENTS:
        doc_copy = doc.copy()
        doc_copy["id"] = get_deterministic_uuid(doc["doc_key"])
        corpus.append(doc_copy)
    return corpus
