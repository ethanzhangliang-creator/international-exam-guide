from intl_exam_guide.models import SourceSnippet, Topic
from intl_exam_guide.planning.practice_generator import (
    build_practice_item,
    choose_command_word,
    choose_difficulty,
    concrete_example,
    concrete_example_zh,
)


def combined_text(parts: tuple[str, list[str], list[str], list[str]]) -> str:
    question, frame, steps, checkpoints = parts
    return " ".join([question, *frame, *steps, *checkpoints]).lower()


def test_build_practice_item_uses_requested_style_and_source_snippets():
    topic = Topic(
        title="3.1.2 - Sources and recording of data",
        points=["Source documents are purchase invoices and sales invoices."],
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Source documents include purchase invoices and sales invoices.",
                matched_term="Source documents",
            )
        ],
    )

    item = build_practice_item(
        topic,
        topic.points,
        number=0,
        qualification_type="international_gcse",
        explanation_style="detective",
        output_language="en",
        subject_area="Accounting",
    )

    combined = " ".join([item.question, *item.public_solution_steps]).lower()
    assert item.command_word == "state"
    assert item.source_snippets == topic.source_snippets
    assert item.question.startswith("Case file:")
    assert "purchase invoice" in combined or "sales invoice" in combined
    assert "ledger" in combined


def test_accounting_and_chemistry_examples_route_to_subject_specific_branches():
    accounting_question, _, accounting_steps, _ = concrete_example(
        Topic(
            title="3.1.2 - Sources and recording of data",
            points=["Source documents are purchase invoices and sales invoices."],
        ),
        "Source documents are purchase invoices and sales invoices.",
        0,
        "Accounting",
    )
    accounting_text = " ".join([accounting_question, *accounting_steps]).lower()

    chemistry_question, _, chemistry_steps, _ = concrete_example(
        Topic(
            title="3.6.4 - Molar concentrations",
            points=["Concentration is related to number of moles and volume of solution."],
        ),
        "Concentration is related to number of moles and volume of solution.",
        0,
        "Chemistry",
    )
    chemistry_text = " ".join([chemistry_question, *chemistry_steps]).lower()

    assert "ledger" in accounting_text
    assert "ratio 2:5" not in accounting_text
    assert "concentration" in chemistry_text
    assert "mol/dm3" in chemistry_text
    assert "ledger" not in chemistry_text


def test_mathematics_algebra_example_is_not_generic():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="A2 - Algebra and equations", points=["Solve linear equations."]),
        "Solve linear equations.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "solve 3(x - 2) + 5 = 20" in combined
    assert "x = 7" in combined
    assert "memorised phrase" not in combined


def test_biology_example_is_subject_specific():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="Cell membranes", points=["Osmosis across cell membranes."]),
        "Osmosis across cell membranes.",
        0,
        "Biology",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "water moves out" in combined
    assert "osmosis" in combined
    assert "ledger" not in combined


def test_economics_example_is_subject_specific():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="Basic economic problem", points=["Scarcity creates economic choices."]),
        "Scarcity creates economic choices.",
        0,
        "Economics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "scarce" in combined
    assert "choose" in combined or "choice" in combined
    assert "ledger" not in combined


def test_generic_example_fallback_remains_exam_focused():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="Unmapped topic", points=["Use the named concept accurately."]),
        "Use the named concept accurately.",
        0,
        "Unmapped Subject",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "memorised phrase" in combined
    assert "command word" in combined
    assert "evidence from the question" in combined


def test_mathematics_examples_cover_major_strands():
    cases = [
        ("N1 - Number", "Ratio and percentage calculations.", 1, ["scale 1:25,000", "1.5 km"]),
        ("N2 - Bounds", "Rounding and bounds.", 1, ["lower bound", "12.35 kg"]),
        ("A3 - Functions", "Functions and graphs.", 1, ["gradient", "y-intercept"]),
        ("A4 - Sequences", "Sequences and nth term.", 0, ["4n + 1", "20th term"]),
        ("G1 - Angles", "Angles around a point.", 1, ["360 degrees", "135 degrees"]),
        ("S1 - Probability", "Probability of outcomes.", 1, ["even outcomes", "1/2"]),
        ("S2 - Statistics", "Mean and range.", 0, ["mean", "range"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Mathematics"))
        for expected in expected_terms:
            assert expected in text


def test_chemistry_examples_cover_visual_and_calculation_branches():
    cases = [
        ("Nanoparticles", "Nanoparticles and surface area.", 0, ["surface area to volume ratio", "catalyst"]),
        ("Carbon structures", "Diamond graphite graphene structure and bonding of carbon.", 1, ["graphite", "conduct electricity"]),
        ("States", "States of matter and diffusion.", 1, ["melting", "liquid water"]),
        ("Atomic particles", "Atomic proton neutron electron.", 1, ["2+ charge", "electrons"]),
        ("Moles", "Moles mass conservation.", 0, ["magnesium oxide", "4.0 g"]),
        ("Analysis", "Gas tests.", 1, ["limewater", "carbon dioxide"]),
        ("Acids", "Acid base alkali salt pH.", 1, ["neutralises", "pH rises"]),
        ("Rates", "Rate equilibrium reversible reaction.", 0, ["collision theory", "reaction rate"]),
        ("Energy", "Exothermic endothermic energy.", 1, ["endothermic", "absorbed"]),
        ("Carbonates", "Carbonates decompose.", 1, ["thermal decomposition", "copper oxide"]),
        ("Organic", "Hydrocarbon polymer crude.", 1, ["poly(ethene)", "polymerisation"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Chemistry"))
        for expected in expected_terms:
            assert expected.lower() in text


def test_accounting_examples_cover_statement_and_verification_branches():
    cases = [
        ("Verification", "Trial balance and bank reconciliation.", 1, ["bank reconciliation", "external bank evidence"]),
        ("Errors", "Trial balance correction of errors.", 0, ["trial balance", "error of principle"]),
        ("Adjustments", "Depreciation and irrecoverable receivables.", 1, ["annual depreciation", "$1,000"]),
        ("Statements", "Financial statements income statement.", 1, ["gross profit", "$3,800"]),
        ("Partnership", "Partnership financial statements.", 0, ["appropriation account", "profit sharing"]),
        ("Ratios", "Ratio profitability liquidity.", 1, ["current ratio", "1.5 : 1"]),
        ("Fallback", "Accounting ethics note.", 0, ["accounting idea", "business scenario"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Accounting"))
        for expected in expected_terms:
            assert expected.lower() in text


def test_economics_examples_cover_core_topic_branches():
    cases = [
        ("Specialisation", "Specialisation and division of labour.", 1, ["specialisation", "factory"]),
        ("Factors", "Factors of production land capital enterprise.", 1, ["vans are capital", "founder is enterprise"]),
        ("Opportunity cost", "Opportunity cost and resource allocation.", 1, ["clinic", "sports centre"]),
        ("Sectors", "Primary secondary tertiary sectors.", 0, ["wheat farm", "service"]),
        ("Market", "Demand supply price equilibrium.", 1, ["supply curve shifts left", "quantity is likely to fall"]),
        ("Elasticity", "Elasticity calculation.", 1, ["ped = 40% / -20%", "price elastic"]),
        ("Costs", "Cost revenue profit production.", 0, ["total revenue = $8 x 200", "profit = $500"]),
        ("Policy", "Government inflation growth employment.", 1, ["taxes", "inflationary pressure"]),
        ("International trade", "Import export globalisation.", 0, ["appreciation", "imports become cheaper"]),
        ("Banking", "Money bank financial interest.", 1, ["interest rates", "borrowing becomes more expensive"]),
        ("Fallback", "Consumer behaviour.", 0, ["economic agent", "likely outcome"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Economics"))
        for expected in expected_terms:
            assert expected.lower() in text


def test_biology_examples_cover_molecule_and_genetics_branches():
    cases = [
        ("Water", "Water solvent dipole transport.", 0, ["polar solvent", "transport"]),
        ("Carbohydrate", "Carbohydrate starch glucose.", 0, ["glucose is a monosaccharide", "starch is a polysaccharide"]),
        ("Lipid", "Lipid triglyceride ester fatty acid glycerol.", 0, ["triglyceride", "ester bonds"]),
        ("DNA", "DNA RNA replication nucleotide gene genetic.", 0, ["complementary base", "genetic information"]),
        ("Fallback", "Ecology adaptation.", 0, ["cause-and-effect", "biological structure"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Biology"))
        for expected in expected_terms:
            assert expected.lower() in text


def test_chinese_examples_cover_subject_specific_branches():
    cases = [
        ("Chemistry", Topic(title="Atomic structure", points=["atomic proton neutron electron"]), "atomic proton neutron electron", ["原子序数", "质量数"]),
        ("Chemistry", Topic(title="Acid base", points=["acid base alkali salt pH"]), "acid base alkali salt pH", ["化学解释题", "结论"]),
        ("Economics", Topic(title="Demand and supply", points=["demand supply market price"]), "demand supply market price", ["需求曲线", "均衡"]),
        ("Accounting", Topic(title="Bank reconciliation", points=["trial balance bank reconciliation"]), "trial balance bank reconciliation", ["银行调节表", "现金簿"]),
        ("Mathematics", Topic(title="G1 - Geometry", points=["triangle geometry"]), "triangle geometry", ["直角三角形", "斜边"]),
        ("Unmapped", Topic(title="Unknown", points=["source detail"]), "source detail", ["原创练习", "最终答案"]),
    ]

    for subject, topic, focus, expected_terms in cases:
        text = combined_text(concrete_example_zh(topic, focus, 0, subject))
        for expected in expected_terms:
            assert expected in text


def test_command_words_and_difficulty_rotate_by_level_and_language():
    assert [choose_command_word(i, "international_gcse") for i in range(4)] == [
        "state",
        "describe",
        "explain",
        "suggest",
    ]
    assert [choose_command_word(i, "international_as_a_level") for i in range(4)] == [
        "explain",
        "analyse",
        "compare",
        "evaluate",
    ]
    assert [choose_command_word(i, "international_gcse", "zh-CN") for i in range(4)] == [
        "写出",
        "描述",
        "解释",
        "提出",
    ]
    assert [choose_difficulty(i) for i in range(3)] == ["core", "standard", "stretch"]
    assert [choose_difficulty(i, "zh-CN") for i in range(3)] == ["基础", "标准", "挑战"]


def test_major_example_branches_have_distinct_even_and_odd_variants():
    cases = [
        ("Mathematics", Topic(title="N1 - Ratio", points=["Ratio and percentage calculations."]), "ratio", ["350 ml", "1.5 km"]),
        ("Mathematics", Topic(title="A3 - Functions", points=["Functions and graphs."]), "function graph", ["x = -3 or x = 3", "y = 11"]),
        ("Mathematics", Topic(title="A4 - Sequences", points=["Sequences and nth term."]), "sequence nth term", ["4n + 1", "31 is in the sequence"]),
        ("Mathematics", Topic(title="G1 - Angles", points=["Angles around a point."]), "angles", ["112 degrees", "135 degrees"]),
        ("Mathematics", Topic(title="S1 - Probability", points=["Probability outcomes."]), "probability", ["blue counters", "even outcomes"]),
        ("Chemistry", Topic(title="Organic", points=["Hydrocarbon polymer crude."]), "hydrocarbon polymer crude", ["co2 and h2o", "poly(ethene)"]),
        ("Accounting", Topic(title="Ratios", points=["Ratio profitability liquidity."]), "ratio profitability liquidity", ["gross profit margin", "current ratio"]),
        ("Economics", Topic(title="Market", points=["Demand supply price equilibrium."]), "demand supply price equilibrium", ["demand shifts to the right", "supply curve shifts left"]),
    ]

    for subject, topic, focus, expected_terms in cases:
        even_text = combined_text(concrete_example(topic, focus, 0, subject))
        odd_text = combined_text(concrete_example(topic, focus, 1, subject))

        assert even_text != odd_text
        assert expected_terms[0].lower() in even_text
        assert expected_terms[1].lower() in odd_text


def test_chinese_practice_example_keeps_student_facing_text_chinese():
    question, frame, steps, checkpoints = concrete_example_zh(
        Topic(
            title="3.1.2 - Sources and recording of data",
            points=["Source documents are purchase invoices and sales invoices."],
        ),
        "Source documents are purchase invoices and sales invoices.",
        0,
        "Accounting",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints])

    assert "原始凭证" in combined
    assert "购货发票" in combined
    assert "source document" not in combined.lower()
    assert "purchase invoice" not in combined.lower()
