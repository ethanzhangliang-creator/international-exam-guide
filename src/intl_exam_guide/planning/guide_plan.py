from __future__ import annotations

import os
import re

from intl_exam_guide.models import (
    GuidePlan,
    GuideRunOptions,
    PracticeItem,
    Qualification,
    Topic,
    TopicGuide,
    VisualBrief,
)
from intl_exam_guide.planning.subject_profiles import (
    resolve_subject_profile,
)


STYLE_LABELS = {
    "formal": "formal exam-focused",
    "friendly": "friendly",
    "life": "real-life context",
    "story": "story-driven",
    "detective": "detective reasoning",
    "adventure": "original adventure mode",
}

IMAGE_PROVIDERS = {
    "prompt-queue",
    "deterministic-svg",
    "custom",
}
RECOMMENDED_IMAGE_MODEL_LABELS = {
    "gpt-image-2",
    "qwen-image-pro",
    "sensenova-u1-fast",
}

LANGUAGE_CHOICES = {"en", "zh-CN"}

ZH_POINT_KEYWORDS = [
    (("si units", "standard prefixes"), "SI 单位与词头"),
    (("record measurements", "precision"), "测量记录精度"),
    (("mean values", "anomalous"), "平均值与异常值"),
    (("tables and graphs", "represent data"), "表格与图像表示数据"),
    (("speed", "distance travelled", "per unit time"), "速度概念"),
    (("distance-time",), "距离-时间图像"),
    (("balanced and unbalanced forces",), "平衡力与非平衡力"),
    (("force and motion relationships",), "力与运动关系"),
    (("observable properties",), "可观察性质"),
    (("physical changes", "chemical changes"), "物理变化与化学变化"),
    (("conservation of mass",), "质量守恒"),
    (("source document", "purchase invoice", "sales invoice", "invoice"), "原始凭证与发票"),
    (("prime entry", "purchases journal", "sales journal"), "初始记录账簿"),
    (("ledger", "double entry"), "分类账与复式记账"),
    (("trial balance",), "试算平衡"),
    (("bank reconciliation", "unpresented cheque", "outstanding banking"), "银行对账"),
    (("control account", "suspense account", "correction of errors"), "账户核对与错误更正"),
    (("depreciation", "non-current asset"), "折旧与非流动资产"),
    (("irrecoverable", "receivables", "payables"), "应收应付与坏账处理"),
    (("accrual", "prudence", "going concern", "accounting concepts"), "会计概念应用"),
    (("financial statements", "income statement", "statement of financial position"), "财务报表"),
    (("profitability", "liquidity", "ratio"), "比率分析"),
    (("demand", "supply", "market"), "市场需求与供给"),
    (("production", "land", "labour", "capital", "enterprise"), "生产要素"),
    (("opportunity cost", "choice", "scarcity"), "选择与机会成本"),
    (("set", "venn"), "集合与韦恩图"),
    (("triangle", "geometry", "bearing", "construction"), "几何图形与标注"),
    (("statistics", "probability", "data"), "统计与概率"),
    (("bond", "structure"), "结构与性质"),
    (("chromatography",), "色谱与分离"),
    (("gas test", "gas tests"), "气体检验"),
    (("particle", "states of matter", "diffusion"), "粒子模型"),
    (("acid", "alkali", "pH", "neutralisation"), "酸碱与 pH"),
]


def zh_topic_reference(topic: Topic) -> str:
    match = re.match(r"^\s*([A-Z]\d+[A-Z]?|\d+(?:\.\d+)+)\b", topic.title)
    if match:
        return f"大纲点 {match.group(1)}"
    return "本知识单元"


def zh_point_label(point: str, index: int = 0) -> str:
    text = re.sub(r"\s+", " ", point.strip())
    lowered = text.lower()
    for keywords, label in ZH_POINT_KEYWORDS:
        if any(keyword.lower() in lowered for keyword in keywords):
            return label
    if re.search(r"[\u4e00-\u9fff]", text):
        return text[:24]
    return f"考点要求 {index + 1}"


def zh_point_labels(points: list[str]) -> list[str]:
    return [zh_point_label(point, index) for index, point in enumerate(points)]


def build_guide_plan(
    qualification: Qualification,
    questions_per_topic: int = 2,
    image_provider: str | None = None,
    explanation_style: str = "friendly",
    output_language: str = "en",
    requested_subject: str | None = None,
    exam_year: str | None = None,
    image_model: str | None = None,
    image_endpoint_url: str | None = None,
    image_api_key_env: str | None = None,
) -> GuidePlan:
    run_options = build_run_options(
        qualification=qualification,
        requested_subject=requested_subject,
        image_provider=image_provider,
        explanation_style=explanation_style,
        output_language=output_language,
        exam_year=exam_year,
        image_model=image_model,
        image_endpoint_url=image_endpoint_url,
        image_api_key_env=image_api_key_env,
    )
    topic_guides: list[TopicGuide] = []
    practice_items: list[PracticeItem] = []
    visual_briefs: list[VisualBrief] = []
    diagram_briefs: list[str] = []

    for topic in qualification.topics:
        points = topic.points[:4]
        if not points:
            points = [topic.title]
        guide = build_topic_guide(
            topic,
            qualification.qualification_type,
            run_options.explanation_style,
            run_options.output_language,
        )
        topic_guides.append(guide)
        visual = build_visual_brief(topic, guide, run_options, qualification.subject_area)
        if visual:
            visual_briefs.append(visual)
        diagram_briefs.append(guide.diagram_brief)
        for number in range(questions_per_topic):
            practice_items.append(
                build_practice_item(
                    topic,
                    points,
                    number,
                    qualification.qualification_type,
                    run_options.explanation_style,
                    run_options.output_language,
                    qualification.subject_area,
                )
            )

    revision_stages = build_revision_stages(
        qualification.qualification_type,
        run_options.output_language,
    )
    return GuidePlan(
        qualification=qualification,
        run_options=run_options,
        topic_guides=topic_guides,
        practice_items=practice_items,
        visual_briefs=visual_briefs,
        diagram_briefs=diagram_briefs,
        revision_stages=revision_stages,
    )


def build_run_options(
    qualification: Qualification,
    requested_subject: str | None,
    image_provider: str | None,
    explanation_style: str,
    output_language: str,
    exam_year: str | None,
    image_model: str | None,
    image_endpoint_url: str | None,
    image_api_key_env: str | None,
) -> GuideRunOptions:
    provider = normalize_image_provider(image_provider, image_model, image_endpoint_url, image_api_key_env)
    style = explanation_style if explanation_style in STYLE_LABELS else "friendly"
    language = output_language if output_language in LANGUAGE_CHOICES else "en"
    return GuideRunOptions(
        requested_subject=requested_subject or qualification.title,
        image_provider=provider,
        explanation_style=style,
        output_language=language,
        exam_year=exam_year or qualification.selected_exam_year,
        image_model=image_model,
        image_endpoint_url=image_endpoint_url,
        image_api_key_env=image_api_key_env,
    )


def normalize_image_provider(
    image_provider: str | None,
    image_model: str | None,
    image_endpoint_url: str | None,
    image_api_key_env: str | None,
) -> str:
    provider = (image_provider or "prompt-queue").strip()
    if provider in RECOMMENDED_IMAGE_MODEL_LABELS:
        # Recommended model names are not proof of a callable provider. Keep the
        # base handbook honest and queue complex visuals for external generation.
        return "prompt-queue"
    if provider == "custom":
        if (
            image_model
            and image_endpoint_url
            and image_api_key_env
            and os.environ.get(image_api_key_env)
        ):
            return "custom"
        return "prompt-queue"
    if provider in IMAGE_PROVIDERS:
        return provider
    return "prompt-queue"


def build_topic_guide(
    topic: Topic,
    qualification_type: str,
    explanation_style: str,
    output_language: str,
) -> TopicGuide:
    points = topic.points[:5] or [topic.title]
    visible_points = points if output_language == "en" else zh_point_labels(points)
    primary = visible_points[0]
    if output_language == "en":
        level_hint = "AS-A-level unit" if qualification_type == "international_as_a_level" else "GCSE topic"
    else:
        level_hint = "AS-A-level 单元" if qualification_type == "international_as_a_level" else "GCSE 知识点"
    essence, analogy, mini_worked_example, pitfall = styled_explanation(
        topic=topic,
        primary=primary,
        level_hint=level_hint,
        explanation_style=explanation_style,
        output_language=output_language,
    )
    worked_solution_steps = (
        [
            "Read the command word and circle the data or conditions in the question.",
            f"Match the question to this syllabus point: {points[0]}.",
            "Write the formula, definition, diagram relationship, or judgement rule you need.",
            "Check the unit, precision, symbols, and final sentence against the question.",
        ]
        if output_language == "en"
        else [
            "读题：圈出指令词和题目给出的数据/条件。",
            f"定位：把题目匹配到{primary}。",
            "作答：写出公式、定义、图形关系或判断过程。",
            "检查：单位、精度、符号和最终句子是否回答了题问。",
        ]
    )
    return TopicGuide(
        topic_title=topic.title,
        essence=essence,
        analogy=analogy,
        mini_worked_example=mini_worked_example,
        worked_solution_steps=worked_solution_steps,
        pitfall=pitfall,
        checklist=build_checklist(visible_points, output_language),
        diagram_brief=(
            (
                f"Draw a clean concept map for '{topic.title}' with the central title in the middle, "
                f"branches for {', '.join(points[:4])}, and one short exam-action label on each branch."
            )
            if output_language == "en"
            else (
                f"为“{zh_topic_reference(topic)}”绘制清晰概念图：中心放主题，分支覆盖 "
                f"{'、'.join(visible_points[:4])}，每个分支加一个简短做题动作标签。"
            )
        ),
        source_snippets=topic.source_snippets[:3],
    )


def build_checklist(points: list[str], output_language: str) -> list[str]:
    if output_language == "en":
        return [
            *[f"Can explain: {point}" for point in points[:4]],
            "Can answer at least one original exam-style prompt without looking at notes.",
            "Can name one common mistake and how to avoid it.",
        ]
    return [
        *[f"能解释：{point}" for point in points[:4]],
        "不看笔记也能完成至少一道原创考试风格练习。",
        "能说出一个常见错误，并知道如何避开。",
    ]


def styled_explanation(
    topic: Topic,
    primary: str,
    level_hint: str,
    explanation_style: str,
    output_language: str,
) -> tuple[str, str, str, str]:
    if output_language == "en":
        return styled_explanation_en(topic, primary, level_hint, explanation_style)
    unit = zh_topic_reference(topic)
    if explanation_style == "formal":
        return (
            f"本 {level_hint} 的目标是准确掌握“{primary}”，并能在题目中按指令词完成计算、解释或判断。",
            f"把“{unit}”看成考试说明中的一个能力模块：每个官方大纲点都对应一种可检查的作答动作。",
            f"例题处理顺序：定位 '{primary}'，列出已知条件，选择公式、定义或判断规则，再写出可复核的结论。",
            "常见失分点是结论正确但过程不足，或没有回应题目指定的指令词。",
        )
    if explanation_style == "life":
        return (
            f"这一节要把 '{primary}' 变成生活中看得见、说得清、用得上的判断动作。",
            f"把“{unit}”放进真实场景：先观察发生了什么，再用官方大纲点解释为什么。",
            "例题先找生活场景里的数据或现象，再把它翻译成公式、定义、图像或因果关系。",
            "常见失分点是只写课本词，没有把它和题目里的真实情境连起来。",
        )
    if explanation_style == "story":
        return (
            f"这一节像一段小故事：'{primary}' 是主线，题目给出的条件是推动故事往前走的线索。",
            f"把“{unit}”拆成开头、冲突和解决：看懂概念，遇到题目障碍，再用正确方法收束答案。",
            "例题先讲清楚题目场景，再一步步把线索收集成答案。",
            "常见失分点是跳过中间推理，让答案像突然出现的结尾。",
        )
    if explanation_style == "detective":
        return (
            f"这一节的核心是用“{primary}”破案：题干是现场，数据是线索，指令词是结案要求。",
            f"把“{unit}”当成一宗小案子：先锁定证据，再判断哪条大纲规则能解释它。",
            "例题按侦探流程走：圈线索，选证据，排除误解，最后写出能回到题问的结论。",
            "常见失分点是看到熟悉词就急着下结论，没有把证据链写完整。",
        )
    if explanation_style == "adventure":
        return (
            f"这一节是一关学习任务：先解锁 '{primary}'，再用它通过计算、解释或判断挑战。",
            f"把“{unit}”看成原创闯关地图：术语是装备，例题是关卡，检查句是通关确认。",
            "例题先确认本关目标，再选择工具，最后用一条检查句确认答案没有跑偏。",
            "常见失分点是装备拿对了但用错地方，也就是知道词却没有按题目要求行动。",
        )
    return (
        f"这一节的核心任务是把 '{primary}' 变成能做题的动作：先看懂关键词，再把它用于计算、解释、比较或判断。",
        f"把“{unit}”当成一个小工具箱：每个官方大纲点是一件工具，题目真正考的是你能不能选对工具并说清楚为什么。",
        f"小例题思路：如果题目围绕 '{primary}' 出题，先圈出数据或关键词，再写出对应公式、定义或判断规则，最后检查单位和答案是否回应题问。",
        "常见失分点是只背关键词，却没有按题目的指令词行动。看到题目先问自己：它要我算、解释、比较，还是证明？",
    )


def styled_explanation_en(
    topic: Topic,
    primary: str,
    level_hint: str,
    explanation_style: str,
) -> tuple[str, str, str, str]:
    if explanation_style == "formal":
        return (
            f"This {level_hint} asks the student to master '{primary}' accurately and apply it under the command word.",
            f"Treat '{topic.title}' as one exam skill block: each syllabus point should map to a checkable answer action.",
            f"Worked-example route: locate '{primary}', list the given conditions, choose the formula, definition, or judgement rule, then write a verifiable conclusion.",
            "A common mark loss is giving the right conclusion without enough method, or missing the command word.",
        )
    if explanation_style == "life":
        return (
            f"Turn '{primary}' into something visible in a real situation, then explain the situation using the syllabus idea.",
            f"Place '{topic.title}' in a real-life scene: observe what happens, then use the syllabus point to explain why.",
            "For examples, first find the data or event in the scene, then translate it into a formula, definition, graph, or cause-effect link.",
            "A common mark loss is writing a memorised phrase without linking it to the context in the question.",
        )
    if explanation_style == "story":
        return (
            f"This topic works like a short story: '{primary}' is the plot line and the question data moves the story forward.",
            f"Break '{topic.title}' into setup, conflict, and resolution: understand the idea, meet the exam obstacle, then close the answer clearly.",
            "For examples, state the scenario first, then collect each clue into a final answer step by step.",
            "A common mark loss is skipping the middle reasoning, so the answer appears without evidence.",
        )
    if explanation_style == "detective":
        return (
            f"Use '{primary}' like a case-solving tool: the question is the scene, the data are clues, and the command word is the case brief.",
            f"Treat '{topic.title}' as a small investigation: lock onto the evidence, then decide which syllabus rule explains it.",
            "For examples, circle clues, choose evidence, rule out the wrong reading, then write a conclusion that answers the question.",
            "A common mark loss is jumping to a familiar conclusion before finishing the evidence chain.",
        )
    if explanation_style == "adventure":
        return (
            f"This topic is a learning mission: unlock '{primary}', then use it to pass a calculation, explanation, or judgement challenge.",
            f"Think of '{topic.title}' as an original quest map: terms are tools, examples are checkpoints, and final checks confirm the route.",
            "For examples, identify the checkpoint goal, choose the right tool, then use one final check sentence to confirm the answer.",
            "A common mark loss is using the right tool in the wrong place: knowing the term but not answering the question.",
        )
    return (
        f"The core task is to turn '{primary}' into an answer action: calculate, explain, compare, or judge using the question wording.",
        f"Treat '{topic.title}' as a small toolkit. Each syllabus point is one tool, and the exam checks whether the student can choose it correctly.",
        f"Example route: circle the data or key terms around '{primary}', choose the matching formula, definition, or judgement rule, then check the unit and final sentence.",
        "A common mark loss is memorising key words without acting on the command word.",
    )


def build_practice_item(
    topic: Topic,
    points: list[str],
    number: int,
    qualification_type: str,
    explanation_style: str = "friendly",
    output_language: str = "en",
    subject_area: str | None = None,
) -> PracticeItem:
    focus = points[number % len(points)]
    visible_focus = focus if output_language == "en" else zh_point_label(focus, number)
    command_word = choose_command_word(number, qualification_type, output_language)
    difficulty = choose_difficulty(number, output_language)
    if output_language == "zh-CN":
        question, frame, steps, checkpoints = concrete_example_zh(topic, focus, number, subject_area)
    else:
        question, frame, steps, checkpoints = concrete_example(topic, focus, number, subject_area)
    question = add_question_variant_marker(question, number, output_language)
    while len(steps) < 4:
        steps.append(
            "Check the final answer against the wording of the question."
            if output_language == "en"
            else "检查最终答案是否回应题目要求。"
        )
    return PracticeItem(
        topic_title=topic.title,
        command_word=command_word,
        difficulty=difficulty,
        focus_point=visible_focus,
        question=decorate_question(question, explanation_style, output_language),
        answer_frame=frame,
        public_solution_steps=steps,
        answer_checkpoints=checkpoints,
        source_points=points,
        source_snippets=topic.source_snippets[:2],
    )


def add_question_variant_marker(question: str, number: int, output_language: str) -> str:
    if number == 0:
        return question
    if output_language == "zh-CN":
        return f"变式 {number + 1}：换一个证据点再做一遍。{question}"
    return f"Variant {number + 1}: use a different source detail. {question}"


def decorate_question(question: str, explanation_style: str, output_language: str = "en") -> str:
    if output_language == "zh-CN":
        prefixes = {
            "formal": "考试题：",
            "friendly": "热身题：",
            "life": "生活场景题：",
            "story": "故事题：",
            "detective": "案件线索：",
            "adventure": "闯关挑战：",
        }
        return f"{prefixes.get(explanation_style, prefixes['friendly'])}{question}"
    prefixes = {
        "formal": "Exam-style prompt: ",
        "friendly": "Warm-up prompt: ",
        "life": "Real-life prompt: ",
        "story": "Story prompt: ",
        "detective": "Case file: ",
        "adventure": "Checkpoint challenge: ",
    }
    return f"{prefixes.get(explanation_style, prefixes['friendly'])}{question}"


def concrete_example(
    topic: Topic,
    focus: str,
    number: int,
    subject_area: str | None = None,
) -> tuple[str, list[str], list[str], list[str]]:
    code = topic.title.split(" ", 1)[0]
    prefix = code[:1]
    text = f"{topic.title} {focus}".lower()
    profile = resolve_subject_profile(subject_area, topic, text)
    if profile.example_domain == "chemistry":
        return chemistry_example(text, focus, number)
    if profile.example_domain == "biology":
        return biology_example(text, focus, number)
    if profile.example_domain == "economics":
        return economics_example(text, focus, number)
    if profile.example_domain == "accounting":
        return accounting_example(text, focus, number)
    if profile.example_domain == "generic":
        return generic_example(focus)
    if prefix == "N" or any(word in text for word in ["number", "ratio", "fraction", "percentage"]):
        if "ratio" in text or number % 3 == 0:
            if number % 2:
                return (
                    "A map uses the scale 1:25,000. Two towns are 6 cm apart on the map. Find the real distance in kilometres.",
                    ["Use the scale to convert map distance to real distance.", "Change centimetres to kilometres.", "Check the size is reasonable."],
                    ["1 cm on the map represents 25,000 cm in real life.", "6 cm represents 150,000 cm.", "150,000 cm = 1,500 m = 1.5 km.", "Answer: 1.5 km."],
                    ["The scale is multiplied by 6.", "The unit conversion is correct.", "A map distance becomes a larger real distance."],
                )
            return (
                "A drink is mixed using juice and water in the ratio 2:5. If 140 ml of juice is used, find the amount of water needed.",
                ["Write juice:water = 2:5.", "Find the value of 1 part.", "Multiply by the water parts."],
                ["2 parts = 140 ml.", "1 part = 140 / 2 = 70 ml.", "Water = 5 parts = 5 x 70 = 350 ml.", "Answer: 350 ml."],
                ["Ratio order is not swapped.", "The answer has ml.", "Water should be more than juice because 5 parts > 2 parts."],
            )
        if "round" in text or "bounds" in text:
            return (
                "A mass is recorded as 12.4 kg to the nearest 0.1 kg. Write the lower and upper bounds.",
                ["Half of 0.1 kg is 0.05 kg.", "Subtract and add 0.05 kg.", "Use the upper-bound inequality correctly."],
                ["Lower bound = 12.4 - 0.05 = 12.35 kg.", "Upper bound = 12.4 + 0.05 = 12.45 kg.", "Answer: 12.35 kg <= mass < 12.45 kg."],
                ["Upper bound uses <.", "Both bounds have kg.", "The interval is centred on 12.4."],
            )
        return (
            "Calculate 3/4 of 280, then write the answer as a percentage of 350.",
            ["Find 3/4 of 280.", "Put that value over 350.", "Convert to a percentage."],
            ["3/4 of 280 = 210.", "210/350 = 0.6.", "0.6 = 60%.", "Answer: 60%."],
            ["Fraction operation is done before percentage conversion.", "The denominator for the percentage is 350.", "Answer is between 0% and 100%."],
        )
    if prefix == "A" or any(word in text for word in ["algebra", "equation", "function", "sequence"]):
        if "function" in text or "graph" in text:
            if number % 2:
                return (
                    "The straight line y = 3x - 4 is drawn on a graph. Find the gradient, the y-intercept, and the value of y when x = 5.",
                    ["Read the coefficient of x as the gradient.", "Read the constant as the y-intercept.", "Substitute x = 5."],
                    ["The gradient is 3.", "The y-intercept is -4.", "When x = 5, y = 3 x 5 - 4 = 11.", "Answer: gradient 3, y-intercept -4, y = 11."],
                    ["Gradient and intercept are not swapped.", "The negative intercept is kept.", "Substitution uses the given x-value."],
                )
            return (
                "For f(x) = 2x^2 - 3, find f(-2), then solve f(x) = 15.",
                ["Substitute -2 carefully.", "Set 2x^2 - 3 equal to 15.", "Remember both square-root solutions."],
                ["f(-2) = 2(-2)^2 - 3 = 5.", "2x^2 - 3 = 15.", "2x^2 = 18, so x^2 = 9.", "Answer: x = -3 or x = 3."],
                ["The negative input is squared correctly.", "Both roots are included.", "Substitution checks the answer."],
            )
        if "sequence" in text:
            if number % 2:
                return (
                    "The nth term of a sequence is 3n - 2. Write the first four terms and decide whether 31 is in the sequence.",
                    ["Substitute n = 1, 2, 3 and 4.", "Set 3n - 2 equal to 31.", "Check whether n is a whole number."],
                    ["The first four terms are 1, 4, 7 and 10.", "3n - 2 = 31.", "3n = 33, so n = 11.", "Answer: 31 is in the sequence because it is the 11th term."],
                    ["Term numbers start at n=1.", "A valid position must be a whole number.", "The conclusion names the term position."],
                )
            return (
                "The sequence is 5, 9, 13, 17, ... Find the nth term and the 20th term.",
                ["Find the common difference.", "Use dn + c.", "Substitute n = 20."],
                ["The common difference is 4.", "Start with 4n: 4, 8, 12, 16, ...", "Add 1 to match the sequence, so nth term = 4n + 1.", "20th term = 4 x 20 + 1 = 81."],
                ["The nth term gives 5 when n=1.", "The 20th term uses n=20.", "Do not confuse term number with term value."],
            )
        if number % 2:
            return (
                "Expand and simplify 2(x + 5) - 3(x - 1).",
                ["Expand both brackets.", "Collect x terms.", "Collect number terms."],
                ["2(x + 5) = 2x + 10.", "-3(x - 1) = -3x + 3.", "2x + 10 - 3x + 3 = -x + 13.", "Answer: -x + 13."],
                ["The minus sign before 3 is applied to both terms.", "Like terms are collected.", "The final expression is simplified."],
            )
        return (
            "Solve 3(x - 2) + 5 = 20.",
            ["Expand the bracket.", "Collect constants.", "Divide by the coefficient of x."],
            ["3(x - 2) + 5 = 3x - 6 + 5.", "3x - 1 = 20.", "3x = 21.", "Answer: x = 7."],
            ["The bracket is expanded correctly.", "The same operation is applied to both sides.", "x=7 checks in the original equation."],
        )
    if prefix == "G" or any(word in text for word in ["geometry", "triangle", "angle", "area", "volume"]):
        if "angle" in text:
            if number % 2:
                return (
                    "Angles around a point are 95 degrees, 130 degrees and x degrees. Find x.",
                    ["Angles around a point add to 360 degrees.", "Add the known angles.", "Subtract from 360 degrees."],
                    ["95 + 130 = 225.", "x = 360 - 225.", "x = 135 degrees.", "Answer: 135 degrees."],
                    ["Uses 360 degrees for a point.", "Known angles are added first.", "The answer is in degrees."],
                )
            return (
                "Two angles on a straight line are x and 68 degrees. Find x.",
                ["Angles on a straight line add to 180 degrees.", "Write the equation.", "Solve for x."],
                ["x + 68 = 180.", "x = 180 - 68.", "Answer: x = 112 degrees."],
                ["The angle fact is correct.", "The answer is in degrees.", "112 + 68 = 180."],
            )
        if number % 2:
            return (
                "A circle has radius 4 cm. Calculate its circumference in terms of pi.",
                ["Use C = 2 pi r.", "Substitute r = 4.", "Leave the answer in terms of pi."],
                ["C = 2 pi r.", "C = 2 pi x 4.", "C = 8 pi.", "Answer: 8 pi cm."],
                ["Radius, not diameter, is substituted.", "The unit is cm.", "The answer is left in terms of pi."],
            )
        return (
            "A right-angled triangle has shorter sides 5 cm and 12 cm. Calculate the hypotenuse.",
            ["Identify the hypotenuse.", "Use c^2 = a^2 + b^2.", "Square-root the result."],
            ["c^2 = 5^2 + 12^2.", "c^2 = 25 + 144 = 169.", "c = sqrt(169) = 13.", "Answer: 13 cm."],
            ["Only perpendicular sides are added.", "Final answer is longer than 12 cm.", "The unit is cm."],
        )
    if prefix == "S" or any(word in text for word in ["probability", "statistics", "data", "mean"]):
        if "probability" in text:
            if number % 2:
                return (
                    "A fair six-sided dice is rolled once. Find the probability of rolling an even number.",
                    ["List the even outcomes.", "Count the total outcomes.", "Write favourable outcomes over total outcomes."],
                    ["The even outcomes are 2, 4 and 6.", "There are 6 possible outcomes.", "P(even) = 3/6.", "Answer: 1/2."],
                    ["Only even outcomes are counted.", "The denominator is 6.", "The fraction is simplified."],
                )
            return (
                "A bag contains 3 red counters, 5 blue counters and 2 green counters. One counter is chosen. Find P(blue).",
                ["Find the total number of counters.", "Put blue counters over total counters.", "Simplify."],
                ["Total = 3 + 5 + 2 = 10.", "Blue counters = 5.", "P(blue) = 5/10 = 1/2.", "Answer: 1/2."],
                ["Denominator is total outcomes.", "Numerator is only blue outcomes.", "Probability is between 0 and 1."],
            )
        if number % 2:
            return (
                "The scores are 4, 7, 9, 9, 11 and 14. Find the median and range.",
                ["Check the data are in order.", "Find the middle of six values.", "Range = largest - smallest."],
                ["The data are already in order.", "The median is the mean of the 3rd and 4th values: (9 + 9) / 2 = 9.", "Range = 14 - 4 = 10.", "Answer: median 9, range 10."],
                ["For an even number of values, two middle values are used.", "Range uses largest minus smallest.", "The repeated 9 is handled correctly."],
            )
        return (
            "The scores are 2, 5, 5, 8 and 10. Find the mean and range.",
            ["Add all values.", "Divide by how many values there are.", "Range = largest - smallest."],
            ["Total = 2 + 5 + 5 + 8 + 10 = 30.", "Mean = 30 / 5 = 6.", "Range = 10 - 2 = 8.", "Answer: mean 6, range 8."],
            ["The repeated 5 is counted twice.", "There are five values.", "Range uses largest minus smallest."],
        )
    return (
        f"Using the idea '{focus}', answer a short exam-style question that asks for one definition, one application, and one check.",
        ["Identify the command word.", "Choose the matching syllabus term.", "Apply it to the given context."],
        [f"Name the focus point: {focus}.", "Apply the idea to the context using one precise sentence.", "Check that the final answer directly answers the question."],
        ["Uses a precise syllabus term.", "Links the idea to the context.", "Does not add unsupported facts."],
    )


def concrete_example_zh(
    topic: Topic,
    focus: str,
    number: int,
    subject_area: str | None = None,
) -> tuple[str, list[str], list[str], list[str]]:
    text = f"{topic.title} {focus}".lower()
    prefix = topic.title.split(" ", 1)[0][:1]
    visible_focus = zh_point_label(focus, number)
    profile = resolve_subject_profile(subject_area, topic, text)
    if profile.example_domain == "chemistry":
        if any(word in text for word in ["solid", "liquid", "states of matter", "diffusion"]):
            return (
                "一名学生几分钟后在房间另一端闻到香水味。用粒子模型解释扩散。",
                ["说出过程名称。", "描述粒子的运动方式。", "把运动和气味扩散联系起来。"],
                ["香水粒子离开液体并与空气混合。", "气体粒子会随机运动，并从高浓度区域向低浓度区域扩散。", "这种过程叫扩散。", "所以学生能闻到气味，是因为香水粒子在空气中扩散。"],
                ["答案必须提到粒子。", "要说明随机运动或扩散方向。", "观察现象要和扩散联系起来。"],
            )
        if any(word in text for word in ["atom", "atomic", "proton", "neutron", "electron"]):
            return (
                "一个原子有 11 个质子、12 个中子和 11 个电子。写出它的原子序数、质量数，并判断它是否呈电中性。",
                ["原子序数等于质子数。", "质量数等于质子数加中子数。", "比较质子数和电子数判断电荷。"],
                ["原子序数 = 11。", "质量数 = 11 + 12 = 23。", "质子数等于电子数，所以整体不带电。", "答案：原子序数 11，质量数 23，电中性。"],
                ["不要用中子数决定原子序数。", "质量数要包含质子和中子。", "电中性意味着质子数等于电子数。"],
            )
        if any(word in text for word in ["bond", "ionic", "covalent", "metallic", "structure"]):
            return (
                "氯化钠熔点很高。用离子键和结构解释原因。",
                ["说出结构类型。", "描述需要克服的作用力。", "把作用力和高熔点联系起来。"],
                ["氯化钠形成巨型离子晶格。", "带相反电荷的离子之间有很强的静电吸引。", "克服这些吸引力需要大量能量。", "因此氯化钠具有很高的熔点。"],
                ["要说离子，而不是分子。", "结构必须和性质相连。", "要解释为什么需要能量。"],
            )
        if has_any_word_or_phrase(text, ["molar", "concentration"]):
            return (
                "某溶液在 0.25 dm3 体积中含有 0.50 mol 溶质。计算浓度，单位用 mol/dm3。",
                ["使用浓度 = 物质的量 / 体积。", "代入数值。", "写出单位。"],
                ["浓度 = 0.50 / 0.25。", "0.50 / 0.25 = 2.0。", "单位是 mol/dm3。", "答案：2.0 mol/dm3。"],
                ["体积单位是 dm3。", "物质的量要除以体积。", "答案要带单位。"],
            )
        return (
            f"围绕“{visible_focus}”完成一道化学解释题：说出现象，指出相关粒子、结构或反应规则，并写出结论。",
            ["找出题目中的现象或数据。", "匹配对应的化学概念。", "用因果关系写出解释。"],
            [f"本题考查“{visible_focus}”。", "先把现象转化为粒子、结构、能量或反应速率语言。", "再写出关键原因。", "最后用一句话回应题目要求。"],
            ["解释必须对应题目情境。", "不要只背关键词。", "结论要和证据一致。"],
        )
    if profile.example_domain == "economics":
        if any(word in text for word in ["opportunity cost", "resource allocation", "making choices"]):
            return (
                "学校有一间教室，可以办经济社团，也可以办复习课。若选择经济社团，解释机会成本是什么。",
                ["确定被选择的方案。", "找出放弃的次优选择。", "清楚写出机会成本。"],
                ["学校选择了经济社团。", "被放弃的次优选择是复习课。", "机会成本就是这间教室无法举办的复习课。", "答案：机会成本是被放弃的次优选择的价值。"],
                ["机会成本不是所有备选方案。", "必须点名被放弃的方案。", "答案要贴合情境。"],
            )
        if any(word in text for word in ["demand", "supply", "market", "price", "equilibrium"]):
            return (
                "一款新手机更受欢迎。假设供给不变，用需求和供给解释市场价格可能如何变化。",
                ["判断哪条曲线变化。", "说明移动方向。", "解释均衡价格变化。"],
                ["受欢迎程度影响需求，而不是供给。", "需求曲线向右移动。", "在原价格下会出现超额需求。", "市场价格可能上升到新的均衡。"],
                ["要用需求变化解释。", "供给保持不变。", "价格上升要通过超额需求说明。"],
            )
        return (
            f"用“{visible_focus}”分析一个生活经济场景：指出经济主体、激励或约束，并说明可能结果。",
            ["说出经济主体。", "找出激励或约束。", "解释结果。"],
            [f"本题聚焦“{visible_focus}”。", "把它应用到消费者、生产者或政府决策中。", "说明稀缺性、激励或成本如何影响选择。", "最后写出可能的经济结果。"],
            ["必须有经济主体。", "要写出因果关系。", "不要加入无依据的现实断言。"],
        )
    if profile.example_domain == "accounting":
        return accounting_example_zh(text, visible_focus, number)
    if profile.example_domain == "generic":
        return generic_example_zh(visible_focus)
    if prefix == "N" or any(word in text for word in ["number", "ratio", "fraction", "percentage"]):
        return (
            "一杯饮料中果汁和水的比例是 2:5。若用了 140 ml 果汁，需要多少水？",
            ["写出果汁:水 = 2:5。", "求出 1 份是多少。", "乘以水对应的份数。"],
            ["2 份 = 140 ml。", "1 份 = 140 / 2 = 70 ml。", "水 = 5 份 = 5 x 70 = 350 ml。", "答案：350 ml。"],
            ["比例顺序不能颠倒。", "答案要带 ml。", "水应比果汁多，因为 5 份大于 2 份。"],
        )
    if prefix == "A" or any(word in text for word in ["algebra", "equation", "function", "sequence"]):
        return (
            "解方程 3(x - 2) + 5 = 20。",
            ["先展开括号。", "合并常数项。", "再除以 x 的系数。"],
            ["3(x - 2) + 5 = 3x - 6 + 5。", "3x - 1 = 20。", "3x = 21。", "答案：x = 7。"],
            ["括号要展开正确。", "等式两边要做同样操作。", "把 x=7 代回去能成立。"],
        )
    if any(word in text for word in ["triangle", "angle", "pythagoras", "trigonometry", "geometry"]):
        return (
            "一个直角三角形两条直角边分别为 5 cm 和 12 cm。求斜边长度。",
            ["确认这是直角三角形。", "使用勾股定理。", "开平方得到长度。"],
            ["c^2 = 5^2 + 12^2。", "c^2 = 25 + 144 = 169。", "c = 13。", "答案：斜边为 13 cm。"],
            ["斜边是最长边。", "平方后再相加。", "答案要带 cm。"],
        )
    return generic_example_zh(visible_focus)


def biology_example(text: str, focus: str, number: int) -> tuple[str, list[str], list[str], list[str]]:
    if any(word in text for word in ["water", "solvent", "dipole", "transport"]):
        return (
            "A red dye dissolves in water and is carried through a plant stem. Explain one property of water that makes this transport possible.",
            ["Identify the useful property of water.", "Link the property to dissolving or movement.", "Finish with the transport role."],
            ["Water is a polar solvent.", "Many substances can dissolve in it because water molecules interact with charged or polar particles.", "Once dissolved, the substance can be carried in solution through the plant.", "So water helps transport dissolved substances such as the dye."],
            ["Names a property of water.", "Connects the property to dissolving.", "Links dissolving to transport, not just storage."],
        )
    if any(word in text for word in ["carbohydrate", "monosaccharide", "disaccharide", "polysaccharide", "starch", "glycogen", "glucose"]):
        return (
            "A student says starch and glucose are both carbohydrates, so they must be the same size molecule. Explain why this is wrong.",
            ["State what glucose is.", "State what starch is.", "Compare the molecule size or structure."],
            ["Glucose is a monosaccharide, a single sugar unit.", "Starch is a polysaccharide made from many glucose units joined together.", "They are both carbohydrates but they are not the same size.", "Therefore the student's statement is wrong."],
            ["Uses mono- and polysaccharide correctly.", "Explains the structural difference.", "Does not say all carbohydrates are identical."],
        )
    if any(word in text for word in ["lipid", "triglyceride", "ester", "fatty acid", "glycerol"]):
        return (
            "A diagram shows glycerol joining to three fatty acids. Name the biological molecule formed and the type of bond made.",
            ["Identify the product.", "Name the bond.", "Link the bond to the joining reaction."],
            ["The molecule formed is a triglyceride.", "The bonds formed are ester bonds.", "Each fatty acid joins to glycerol by a condensation reaction.", "A triglyceride therefore contains glycerol joined to three fatty acids."],
            ["Names triglyceride.", "Names ester bonds.", "Links the answer to the glycerol and fatty acids in the question."],
        )
    if any(word in text for word in ["dna", "rna", "replication", "nucleotide", "gene", "genetic"]):
        return (
            "During DNA replication, one original strand is used to build a new complementary strand. Explain why this helps copy genetic information accurately.",
            ["Mention complementary base pairing.", "Explain how the new strand is built.", "Link the process to accurate copying."],
            ["Each base on the original strand pairs with a complementary base.", "This pairing guides the order of bases in the new strand.", "The base sequence is therefore copied into a new DNA molecule.", "This helps preserve the genetic information."],
            ["Uses complementary pairing.", "Explains the copying mechanism.", "Connects base order to genetic information."],
        )
    if any(word in text for word in ["cell", "membrane", "osmosis", "diffusion", "transport"]):
        return (
            "A cell is placed in a solution with a lower water concentration than the cytoplasm. Predict the direction of water movement and explain why.",
            ["Compare water concentrations.", "State the direction of movement.", "Name the process if relevant."],
            ["The solution has a lower water concentration than the cytoplasm.", "Water moves out of the cell down the water concentration gradient.", "This movement across the partially permeable membrane is osmosis.", "The cell may lose water and shrink."],
            ["Compares water concentration correctly.", "States water moves out.", "Uses osmosis only for water across a membrane."],
        )
    return (
        f"A student is revising '{focus}'. Write one cause-and-effect explanation that links the biological structure or process to its function.",
        ["Identify the structure or process.", "State the function or result.", "Link them with because/therefore."],
        [f"The focus point is {focus}.", "First identify the biological structure, molecule, or process named in the question.", "Then explain how its feature causes the observed function or result.", "Finish with a direct answer to the command word."],
        ["Uses biology cause-and-effect language.", "Links structure/process to function.", "Keeps the answer inside the syllabus point."],
    )


def generic_example(focus: str) -> tuple[str, list[str], list[str], list[str]]:
    return (
        f"A student revises the syllabus point '{focus}' but writes only a memorised phrase. Improve the answer by adding a clear command-word action and one piece of evidence from the question.",
        ["Identify the command word.", "Choose one relevant evidence phrase.", "Connect the evidence to the syllabus point."],
        [f"The answer must use the syllabus point: {focus}.", "A memorised phrase is not enough because exam answers must respond to the question context.", "Add the evidence or condition given in the question.", "Finish with a sentence that directly answers the command word."],
        ["Mentions the syllabus point.", "Adds evidence from the question.", "Answers the command word instead of copying notes."],
    )


def generic_example_zh(visible_focus: str) -> tuple[str, list[str], list[str], list[str]]:
    return (
        f"围绕“{visible_focus}”完成一道原创练习：先找关键信息，再选择方法，最后写出可检查的答案。",
        ["圈出题目给出的数据或关键词。", "选择对应的公式、定义或判断规则。", "写出步骤并检查单位。"],
        [f"本题考查“{visible_focus}”。", "先把题目信息整理成可用条件。", "再按对应方法完成计算或解释。", "最后检查答案是否回应题问。"],
        ["使用了正确知识点。", "步骤能被复核。", "最终答案回应题目要求。"],
    )


def accounting_example(
    text: str,
    focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if has_any_word_or_phrase(text, ["source document", "source documents", "prime entry", "ledger", "double entry", "recording of transactions"]):
        if number % 2:
            return (
                "A business receives a purchase invoice for goods bought on credit. State one source document, name the book of prime entry, and explain why the transaction is later posted to ledger accounts.",
                ["Identify the evidence document.", "Choose the correct book of prime entry.", "Link prime entry to ledger posting."],
                ["The source document is the purchase invoice.", "The transaction is first recorded in the purchases journal.", "It is later posted to ledger accounts so the double entry records are updated.", "This keeps a trace from source document to book of prime entry to ledger."],
                ["Uses an accounting source document.", "Names a book of prime entry.", "Does not treat the journal and ledger as the same record."],
            )
        return (
            "A trader sells goods on credit and issues a sales invoice. Explain how this source document starts the accounting record.",
            ["Name the source document.", "Name the first accounting book used.", "Explain the link to ledger accounts."],
            ["The sales invoice is the source document.", "The sale is first recorded in the sales journal.", "The amount is then posted to the receivables ledger and general ledger as part of the double entry system.", "So the original business event is supported by a document and recorded systematically."],
            ["The answer starts with a source document.", "Credit sale is not treated as immediate cash.", "Ledger posting follows the book of prime entry."],
        )
    if has_any_word_or_phrase(text, ["trial balance", "control account", "bank reconciliation", "suspense account", "correction of errors", "verification"]):
        if number % 2:
            return (
                "A cash book shows a different balance from the bank statement. Explain two reasons why the balances may differ and name the statement used to compare them.",
                ["Identify timing differences or errors.", "Name the reconciliation document.", "Keep cash book and bank statement separate."],
                ["One reason is unpresented cheques: payments recorded in the cash book but not yet processed by the bank.", "Another reason is outstanding bankings: receipts recorded by the business but not yet shown by the bank.", "A bank reconciliation statement is prepared to compare and explain the difference.", "This verifies the cash book against external bank evidence."],
                ["Uses bank reconciliation language.", "Gives reasons for disagreement.", "Does not say one balance is automatically wrong."],
            )
        return (
            "A trial balance does not agree. State one error that could cause this and one error that a trial balance may not reveal.",
            ["Separate revealed and unrevealed errors.", "Name specific error types.", "Explain the limitation."],
            ["A partial omission can cause the trial balance not to agree because only one side of the double entry is recorded.", "An error of principle may not be revealed if equal debit and credit amounts were still posted.", "Therefore the trial balance checks arithmetic equality, not every accounting error.", "It is a verification tool with limitations."],
            ["Mentions double entry equality.", "Includes one revealed and one unrevealed error.", "Explains the limitation, not just the name."],
        )
    if has_any_word_or_phrase(text, ["depreciation", "non-current asset", "irrecoverable", "receivables", "payables", "accrual", "prudence", "going concern", "accounting concepts"]):
        if number % 2:
            return (
                "A machine costing $5,000 is depreciated by 20% per year using the straight-line method. Calculate the annual depreciation and explain why depreciation is recorded.",
                ["Use cost x rate.", "State the annual depreciation.", "Link the charge to asset use over time."],
                ["Annual depreciation = $5,000 x 20%.", "Annual depreciation = $1,000.", "Depreciation records part of the asset's cost as an expense for the period it helps generate revenue.", "This avoids treating a long-term asset as if it were used up immediately."],
                ["Uses the stated method.", "Keeps depreciation separate from cash payment.", "Explains the accounting purpose."],
            )
        return (
            "A customer debt of $300 is judged irrecoverable. Explain the accounting treatment and its effect on profit.",
            ["Identify the debt.", "Record the expense effect.", "Link it to profit."],
            ["The irrecoverable debt is removed from trade receivables.", "It is recorded as an expense in the income statement.", "Expenses increase by $300, so profit decreases by $300.", "This applies prudence by not overstating receivables."],
            ["Receivables and expense are both mentioned.", "Profit effect direction is correct.", "The answer links to an accounting concept."],
        )
    if has_any_word_or_phrase(text, ["financial statements", "income statement", "statement of financial position", "partnership", "sole trader", "limited company", "manufacturing account", "non-profit", "incomplete records"]):
        if number % 2:
            return (
                "A sole trader has sales of $18,000, cost of sales of $11,000 and expenses of $3,200. Calculate gross profit and profit for the year.",
                ["Calculate gross profit first.", "Subtract expenses after gross profit.", "Keep the currency."],
                ["Gross profit = sales - cost of sales.", "Gross profit = $18,000 - $11,000 = $7,000.", "Profit for the year = $7,000 - $3,200 = $3,800.", "Answer: gross profit $7,000; profit for the year $3,800."],
                ["Cost of sales is subtracted from sales.", "Expenses are subtracted after gross profit.", "Currency is shown."],
            )
        return (
            "A partnership agreement gives a partner a salary of $2,000 and interest on capital of $500. Explain where these items are shown in the partnership financial statements.",
            ["Identify the organisation type.", "Name the relevant statement/account.", "Explain the purpose."],
            ["The business is a partnership.", "Partner salary and interest on capital are recorded in the appropriation account.", "They show how profit is shared between partners after the income statement profit is calculated.", "They are not ordinary business expenses in the same way as rent or wages."],
            ["Names the appropriation account.", "Separates profit sharing from normal expenses.", "Uses partnership context."],
        )
    if has_any_word_or_phrase(text, ["ratio", "profitability", "liquidity", "trade receivable days", "trade payable days", "appraising business performance"]):
        if number % 2:
            return (
                "A business has current assets of $12,000 and current liabilities of $8,000. Calculate the current ratio and comment briefly on liquidity.",
                ["Use current assets divided by current liabilities.", "Simplify the ratio.", "Comment on ability to meet short-term debts."],
                ["Current ratio = 12,000 : 8,000.", "Simplified current ratio = 1.5 : 1.", "This means the business has $1.50 of current assets for each $1 of current liabilities.", "It suggests some ability to meet short-term debts, but more evidence is needed for a full judgement."],
                ["Uses current assets and liabilities.", "Ratio is simplified.", "Comment is cautious and evidence-based."],
            )
        return (
            "A business has gross profit of $9,000 and sales revenue of $30,000. Calculate the gross profit margin.",
            ["Use gross profit / sales revenue x 100.", "Substitute the figures.", "Add the percentage sign."],
            ["Gross profit margin = 9,000 / 30,000 x 100.", "9,000 / 30,000 = 0.3.", "0.3 x 100 = 30%.", "Answer: gross profit margin is 30%."],
            ["Gross profit is the numerator.", "Sales revenue is the denominator.", "Answer is a percentage."],
        )
    return (
        f"Use the accounting idea '{focus}' in a short business scenario: identify the document, account, statement, or calculation involved, then explain the effect on the records.",
        ["Identify the accounting evidence or record.", "Apply the named accounting rule.", "State the effect on the accounts or statement."],
        [f"The focus idea is {focus}.", "First connect the business event to the correct accounting record.", "Then apply the calculation, classification, or double entry logic required.", "Finish by stating the effect on profit, assets, liabilities, equity, or control of records."],
        ["Uses accounting records or statements.", "Explains the effect, not just the term.", "Does not borrow a question from another subject."],
    )


def accounting_example_zh(
    text: str,
    visible_focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if has_any_word_or_phrase(text, ["source document", "prime entry", "ledger", "double entry", "recording"]):
        return (
            "一家企业赊购商品并收到购货发票。说明这张原始凭证如何进入会计记录。",
            ["先指出原始凭证。", "再指出首次记录的账簿。", "最后说明如何进入分类账。"],
            ["购货发票是原始凭证。", "赊购交易先记录在购货日记账。", "之后再过账到相关分类账账户。", "这样交易就能从凭证追踪到初始记录和分类账。"],
            ["要有原始凭证。", "要区分初始记录账簿和分类账。", "不能把赊购当作现金交易。"],
        )
    if has_any_word_or_phrase(text, ["trial balance", "bank reconciliation", "control account", "verification", "error"]):
        return (
            "现金簿余额和银行对账单余额不同。说明两个可能原因，并说出用于核对的报表。",
            ["找出时间差或错误。", "说出银行调节表。", "区分现金簿和银行对账单。"],
            ["可能原因之一是未兑现支票。", "另一个可能原因是在途存款。", "企业会编制银行调节表来解释差异。", "这可以用外部银行资料核对现金簿。"],
            ["原因要具体。", "要说出银行调节。", "不能默认某一方一定错。"],
        )
    if has_any_word_or_phrase(text, ["financial statements", "income statement", "profit", "ratio", "liquidity"]):
        return (
            "某企业销售收入为 $18,000，销售成本为 $11,000，费用为 $3,200。计算毛利和本年利润。",
            ["先算毛利。", "再扣除费用。", "保留货币单位。"],
            ["毛利 = 销售收入 - 销售成本。", "$18,000 - $11,000 = $7,000。", "本年利润 = $7,000 - $3,200 = $3,800。", "答案：毛利为 $7,000，本年利润为 $3,800。"],
            ["不要先扣费用。", "货币单位要保留。", "毛利和本年利润要区分。"],
        )
    return (
        f"围绕“{visible_focus}”完成一道会计情境题：判断相关凭证、账户、报表或计算，并说明对会计记录的影响。",
        ["找出业务事件。", "匹配对应会计记录或规则。", "说明对账户或报表的影响。"],
        [f"本题考查“{visible_focus}”。", "先把业务事件转成会计语言。", "再应用分类、计算或复式记账逻辑。", "最后说明对利润、资产、负债、权益或记录核对的影响。"],
        ["使用会计记录或报表。", "说明影响，而不是只背词。", "没有借用其他科目的题型。"],
    )


def has_any_word_or_phrase(text: str, terms: list[str]) -> bool:
    tokens = set(re.findall(r"[a-z0-9]+", text))
    for term in terms:
        if " " in term or "-" in term:
            if term in text:
                return True
        elif term in tokens:
            return True
    return False


def chemistry_example(
    text: str,
    focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if any(word in text for word in ["nano", "surface area"]):
        if number % 2:
            return (
                "A medicine is delivered using nanoparticles. Explain one possible benefit and one safety concern linked to their small size.",
                ["Link small size to surface area or movement.", "Give a clear benefit.", "Give a cautious safety concern."],
                ["Nanoparticles are very small and have a large surface area to volume ratio.", "This can help them interact strongly with target surfaces or carry substances efficiently.", "A safety concern is that very small particles may enter parts of the body where their effects must be tested.", "So nanoparticles can be useful, but their risks need careful evaluation."],
                ["Mentions small size or surface area.", "Includes both benefit and concern.", "Does not claim all nanoparticles are automatically safe or unsafe."],
            )
        return (
            "A catalyst is made from nanoparticles instead of larger pieces of the same material. Explain how surface area to volume ratio can make the catalyst more effective.",
            ["Compare particle size.", "Link small size to surface area.", "Explain the effect on reactions."],
            ["Nanoparticles are very small pieces of material.", "For the same amount of material, they have a larger surface area to volume ratio.", "More surface is available for reacting particles to contact.", "So the catalyst can provide more active surface for the reaction."],
            ["Mentions surface area to volume ratio.", "Does not claim the substance becomes a different element.", "Links structure to reaction usefulness."],
        )
    if "structure and bonding of carbon" in text or has_any_word_or_phrase(text, ["diamond", "graphite", "graphene"]):
        if number % 2:
            return (
                "Graphite can conduct electricity but diamond cannot. Explain this difference using the arrangement of electrons in their structures.",
                ["Describe electron bonding in graphite.", "Describe electron bonding in diamond.", "Link electron movement to conductivity."],
                ["In graphite, each carbon atom bonds to three others, leaving one delocalised electron per carbon atom.", "These delocalised electrons can move through the layers.", "In diamond, each carbon atom uses its four outer electrons in covalent bonds.", "So graphite conducts electricity, while diamond does not."],
                ["Mentions delocalised electrons for graphite.", "Explains why diamond lacks mobile electrons.", "Links structure to conductivity."],
            )
        return (
            "Diamond is very hard, while graphite is soft and slippery. Explain the difference using carbon bonding and structure.",
            ["Describe the bonding in diamond.", "Describe the layered structure in graphite.", "Link each structure to its property."],
            ["In diamond, each carbon atom forms four covalent bonds in a giant covalent structure.", "This makes diamond very hard because many strong covalent bonds must be broken.", "In graphite, carbon atoms form layers with weak forces between layers.", "The layers can slide, so graphite is soft and slippery."],
            ["Uses carbon atoms and covalent bonds.", "Explains both diamond and graphite.", "Links structure to property, not just appearance."],
        )
    if any(word in text for word in ["solid", "liquid", "states of matter", "diffusion"]):
        if number % 2:
            return (
                "Ice melts on a warm day. Describe what happens to the arrangement and movement of water particles during melting.",
                ["Name the change of state.", "Compare particle arrangement before and after.", "Describe the energy and movement change."],
                ["Melting is the change from solid to liquid.", "In ice, particles are held in fixed positions and only vibrate.", "As energy is transferred, particles can move past each other.", "In liquid water, particles are still close together but arranged less regularly and can flow."],
                ["Uses particle arrangement and movement.", "Names the change of state.", "Does not say particles disappear or become larger."],
            )
        return (
            "A student smells perfume from across a room after a few minutes. Use the particle model to explain diffusion.",
            ["Name the process.", "Describe particle movement.", "Link movement to spreading through the air."],
            ["Perfume particles leave the liquid and mix with the air.", "Gas particles move randomly and spread out from a high concentration to a lower concentration.", "This spreading is diffusion.", "Answer: the smell reaches the student because perfume particles diffuse through the air."],
            ["Uses particles, not just 'the smell moves'.", "Mentions random movement or spreading.", "Links the observation to diffusion."],
        )
    if any(word in text for word in ["bond", "ionic", "covalent", "metallic", "structure"]):
        if number % 2:
            return (
                "Explain why metals can conduct electricity when solid but ionic compounds usually conduct only when molten or dissolved.",
                ["Compare mobile charged particles.", "Explain metals first.", "Explain ionic compounds second."],
                ["Metals contain delocalised electrons that can move through the solid structure.", "These moving electrons carry charge, so solid metals conduct electricity.", "In solid ionic compounds, ions are fixed in a lattice and cannot move.", "When molten or dissolved, ions can move and carry charge."],
                ["Uses mobile charged particles.", "Separates metal and ionic cases.", "Links movement to conductivity."],
            )
        return (
            "Sodium chloride has a high melting point. Explain this using ideas about ionic bonding and structure.",
            ["Name the structure.", "Describe the force that must be overcome.", "Link the force to the high melting point."],
            ["Sodium chloride forms a giant ionic lattice.", "There are strong electrostatic attractions between oppositely charged ions.", "A lot of energy is needed to overcome these attractions.", "Therefore sodium chloride has a high melting point."],
            ["Uses 'ions', not molecules.", "Links structure to property.", "Explains why energy is needed."],
        )
    if any(word in text for word in ["atom", "atomic", "periodic", "proton", "neutron", "electron"]):
        if number % 2:
            return (
                "An ion has 12 protons and 10 electrons. State its charge and explain how you know.",
                ["Compare protons and electrons.", "Find the difference in charge.", "Write the ion charge correctly."],
                ["There are 12 positive protons and 10 negative electrons.", "There are two more protons than electrons.", "The ion has an overall 2+ charge.", "Answer: 2+ because it has lost two electrons compared with a neutral atom."],
                ["Protons are positive.", "Electron loss gives a positive ion.", "The charge size matches the difference."],
            )
        return (
            "An atom has 11 protons, 12 neutrons and 11 electrons. State its atomic number, mass number, and whether it is neutral.",
            ["Atomic number = number of protons.", "Mass number = protons + neutrons.", "Compare protons and electrons for charge."],
            ["Atomic number = 11.", "Mass number = 11 + 12 = 23.", "Protons = electrons, so the atom has no overall charge.", "Answer: atomic number 11, mass number 23, neutral atom."],
            ["Protons, not neutrons, decide atomic number.", "Mass number includes protons and neutrons.", "Neutral means proton count equals electron count."],
        )
    if has_any_word_or_phrase(text, ["molar", "concentration"]):
        if number % 2:
            return (
                "A 0.20 mol/dm3 solution has a volume of 0.15 dm3. Calculate the amount of solute in moles.",
                ["Rearrange concentration = moles / volume.", "Use moles = concentration x volume.", "Substitute the values."],
                ["Moles = concentration x volume.", "Moles = 0.20 x 0.15.", "Moles = 0.030.", "Answer: 0.030 mol."],
                ["Volume is in dm3.", "Concentration is multiplied by volume.", "The answer has mol."],
            )
        return (
            "A solution contains 0.50 mol of solute in 0.25 dm3 of solution. Calculate its concentration in mol/dm3.",
            ["Use concentration = moles / volume.", "Substitute the values.", "Give the unit."],
            ["Concentration = 0.50 / 0.25.", "0.50 / 0.25 = 2.0.", "The unit is mol/dm3.", "Answer: 2.0 mol/dm3."],
            ["Volume is in dm3.", "Moles are divided by volume, not multiplied.", "The answer includes mol/dm3."],
        )
    if has_any_word_or_phrase(text, ["mole", "moles", "quantitative", "mass", "conservation"]):
        if number % 2:
            return (
                "Calcium carbonate thermally decomposes to make 5.6 g of calcium oxide and 4.4 g of carbon dioxide. Calculate the mass of calcium carbonate that decomposed.",
                ["Use conservation of mass.", "Add the product masses.", "Give the mass of the original reactant."],
                ["Total mass of products = 5.6 g + 4.4 g.", "Total mass of products = 10.0 g.", "By conservation of mass, the reactant mass was 10.0 g.", "Answer: 10.0 g of calcium carbonate."],
                ["Both products are included.", "The unit is grams.", "Mass is conserved for the reaction."],
            )
        return (
            "Magnesium reacts with oxygen to form magnesium oxide. If 2.4 g of magnesium reacts with 1.6 g of oxygen, calculate the mass of magnesium oxide formed.",
            ["Use conservation of mass.", "Add the mass of reactants that become the product.", "Give the unit."],
            ["In a closed reaction, total mass is conserved.", "Mass of magnesium oxide = 2.4 g + 1.6 g.", "Mass of magnesium oxide = 4.0 g.", "Answer: 4.0 g."],
            ["Only reacting masses are added.", "The answer keeps grams.", "The calculation uses conservation of mass."],
        )
    if has_any_word_or_phrase(text, ["chromatography", "analysis", "purity", "identification", "ion", "ions", "gas", "gases"]):
        if has_any_word_or_phrase(text, ["gas", "gases"]) and not has_any_word_or_phrase(text, ["chromatography", "purity"]):
            if number % 2:
                return (
                    "A gas turns limewater milky. Identify the gas and state the positive test result.",
                    ["Name the test reagent.", "State the observation.", "Identify the gas."],
                    ["The reagent is limewater.", "The positive observation is that limewater turns milky.", "This is the test for carbon dioxide.", "Answer: the gas is carbon dioxide."],
                    ["Observation and gas are both stated.", "Limewater is named.", "The result is not confused with oxygen or hydrogen."],
                )
            return (
                "A gas relights a glowing splint. Identify the gas and write the positive test observation.",
                ["Recall the splint test.", "Match the observation to the gas.", "State the observation clearly."],
                ["A glowing splint is used to test for oxygen.", "If the splint relights, oxygen is present.", "The positive observation is relighting of the glowing splint.", "Answer: the gas is oxygen."],
                ["Uses a glowing, not lighted, splint.", "Names oxygen.", "Observation and conclusion are linked."],
            )
        if number % 2:
            return (
                "A chromatogram shows two spots for an ink sample. Explain what this suggests about the purity of the ink.",
                ["Connect number of spots to number of substances.", "Explain purity.", "Keep the conclusion cautious."],
                ["In chromatography, different substances can produce different spots.", "Two spots suggest the ink contains more than one substance.", "A pure substance would usually produce one spot under the same conditions.", "So the ink is likely to be a mixture."],
                ["Uses spots as evidence.", "Links mixture to purity.", "Does not overclaim without reference values."],
            )
        return (
            "In chromatography, a spot moves 4.2 cm while the solvent front moves 6.0 cm. Calculate the Rf value.",
            ["Use Rf = distance moved by spot / distance moved by solvent front.", "Substitute both distances in the same units.", "Check that Rf is between 0 and 1."],
            ["Rf = 4.2 / 6.0.", "Rf = 0.70.", "The value is below 1, so it is physically possible.", "Answer: Rf = 0.70."],
            ["Spot distance is the numerator.", "Solvent-front distance is the denominator.", "Rf has no unit."],
        )
    if any(word in text for word in ["acid", "base", "alkali", "salt", "ph"]):
        if number % 2:
            return (
                "A solution has pH 2 before sodium hydroxide is added slowly. Describe what happens to the pH as neutralisation takes place.",
                ["Identify the starting solution as acidic.", "Explain the effect of adding alkali.", "Describe movement toward neutral."],
                ["pH 2 is acidic.", "Sodium hydroxide is an alkali, so it neutralises the acid.", "As more alkali is added, the pH rises toward 7.", "If excess alkali is added, the pH can go above 7."],
                ["pH direction is correct.", "Neutralisation is named.", "Excess alkali is handled carefully."],
            )
        return (
            "A student reacts hydrochloric acid with sodium hydroxide. Name the salt formed and describe how the pH changes during neutralisation.",
            ["Identify the acid and alkali ions.", "Combine the metal ion with the acid's negative ion.", "Describe movement toward pH 7."],
            ["Hydrochloric acid provides chloride ions.", "Sodium hydroxide provides sodium ions.", "The salt is sodium chloride.", "As neutralisation happens, the pH moves toward 7."],
            ["The salt name comes from sodium + chloride.", "Neutral does not mean strongly acidic or alkaline.", "pH change is linked to neutralisation."],
        )
    if any(word in text for word in ["rate", "equilibrium", "reversible"]):
        if number % 2:
            return (
                "A reversible reaction reaches equilibrium in a closed container. Explain what is true about the forward and reverse reactions at equilibrium.",
                ["State that both reactions continue.", "Compare their rates.", "Explain why concentrations stay constant."],
                ["At equilibrium, the forward and reverse reactions are still happening.", "The forward and reverse reaction rates are equal.", "Because the rates are equal, amounts of reactants and products do not change overall.", "This is dynamic equilibrium in a closed system."],
                ["Uses a closed system.", "Says rates are equal, not reactions stopped.", "Explains constant amounts."],
            )
        return (
            "A reaction is repeated at a higher temperature. Explain why the rate increases using collision theory.",
            ["State what happens to particle energy.", "Link energy to collision frequency.", "Mention successful collisions."],
            ["At higher temperature, particles have more kinetic energy.", "They move faster and collide more often.", "A greater proportion of collisions have enough energy to react.", "So the reaction rate increases."],
            ["Mentions particles, not just 'heat'.", "Uses successful collisions.", "Explains why rate changes."],
        )
    if any(word in text for word in ["energy", "exothermic", "endothermic", "cell", "fuel"]):
        if any(word in text for word in ["cell", "fuel"]) and number % 2:
            return (
                "A chemical cell produces a voltage when two different metals are connected through an electrolyte. Explain why the metals and electrolyte are needed.",
                ["Identify the two electrodes.", "Explain the role of the electrolyte.", "Link the chemical reaction to voltage."],
                ["The two different metals act as electrodes.", "The electrolyte allows ions to move and completes the circuit inside the cell.", "Chemical reactions at the electrodes transfer energy electrically.", "So the cell can produce a potential difference."],
                ["Mentions two different metals.", "Explains the electrolyte role.", "Links chemical change to electrical energy."],
            )
        if number % 2:
            return (
                "A reaction mixture becomes colder during a reaction. State whether the reaction is exothermic or endothermic and explain the evidence.",
                ["Use the temperature change as evidence.", "Identify the direction of energy transfer.", "Name the reaction type."],
                ["The temperature of the surroundings or mixture falls.", "Energy is taken in from the surroundings.", "This means the reaction is endothermic.", "Answer: endothermic because energy is absorbed."],
                ["Temperature decrease is used as evidence.", "Direction of energy transfer is correct.", "The final reaction type is endothermic."],
            )
        return (
            "A reaction transfers energy to the surroundings and the temperature rises. State whether it is exothermic or endothermic and explain why.",
            ["Identify direction of energy transfer.", "Link energy transfer to temperature change.", "Name the reaction type."],
            ["Energy is transferred from the reaction to the surroundings.", "The surroundings get warmer, so the temperature rises.", "This is exothermic.", "Answer: exothermic because energy is released to the surroundings."],
            ["Direction of transfer is correct.", "Temperature change is used as evidence.", "The final word is exothermic."],
        )
    if any(word in text for word in ["carbonate", "carbonates"]):
        if number % 2:
            return (
                "Copper carbonate is heated and forms a black solid and carbon dioxide. Name the type of reaction and the black solid.",
                ["Identify what heating does to the carbonate.", "Name the reaction type.", "Name the metal oxide."],
                ["Heating breaks down the carbonate.", "This is thermal decomposition.", "Copper carbonate forms copper oxide and carbon dioxide.", "The black solid is copper oxide."],
                ["Uses thermal decomposition.", "Names carbon dioxide as a product.", "Identifies the metal oxide correctly."],
            )
        return (
            "Calcium carbonate is heated strongly. State the products and name the type of reaction.",
            ["Recall the carbonate decomposition pattern.", "Name the metal oxide.", "Name the gas."],
            ["Metal carbonates break down on heating.", "Calcium carbonate forms calcium oxide.", "The gas produced is carbon dioxide.", "Answer: calcium oxide and carbon dioxide; thermal decomposition."],
            ["Both products are named.", "The reaction type is thermal decomposition.", "The gas is carbon dioxide."],
        )
    if any(word in text for word in ["organic", "hydrocarbon", "hydrocarbons", "polymer", "polymers", "crude"]):
        if number % 2:
            return (
                "Ethene can form poly(ethene). Describe what happens to the double bonds during polymerisation.",
                ["Identify the monomer.", "Explain what happens to the double bond.", "Describe formation of the polymer chain."],
                ["Ethene molecules are the monomers.", "The carbon-carbon double bonds open during addition polymerisation.", "Many ethene molecules join together in a long chain.", "The product is poly(ethene)."],
                ["Mentions monomers joining.", "Double bonds open, not disappear without explanation.", "Names the polymer product."],
            )
        return (
            "A hydrocarbon contains only carbon and hydrogen. Explain why complete combustion produces carbon dioxide and water.",
            ["Identify the elements in the fuel.", "Add oxygen from the air.", "Link products to the elements present."],
            ["The hydrocarbon contains carbon and hydrogen.", "During complete combustion it reacts with oxygen.", "Carbon forms carbon dioxide and hydrogen forms water.", "Answer: complete combustion produces CO2 and H2O."],
            ["Only carbon and hydrogen are named in the fuel.", "Oxygen is a reactant from the air.", "Products match the elements."],
        )
    return (
        f"A student is revising '{focus}'. Write one observation, one explanation, and one exam-safe conclusion for this chemistry idea.",
        ["Name the chemical idea.", "Link it to an observation or property.", "Finish with a source-safe conclusion."],
        [f"The focus idea is {focus}.", "Use the observed change or property as evidence.", "Explain the evidence using particles, structure, energy, or ions where relevant.", "Finish with a conclusion that directly answers the question."],
        ["Uses a chemistry term accurately.", "Connects evidence to explanation.", "Does not add unsupported reaction details."],
    )


def economics_example(
    text: str,
    focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if any(word in text for word in ["need", "want", "economic activity", "basic economic problem", "scarcity"]):
        if number % 2:
            return (
                "A family wants a larger apartment, a holiday and extra tutoring, but its monthly income is limited. Explain the basic economic problem in this situation.",
                ["Identify unlimited wants.", "Identify the limited resource.", "Explain why choices must be made."],
                ["The family's wants include housing, a holiday and tutoring.", "The limited resource is monthly income.", "Because income is scarce, the family cannot satisfy every want at once.", "This is the basic economic problem: limited resources but unlimited wants."],
                ["Uses wants and scarce resources.", "Explains why choice is needed.", "Does not treat income as unlimited."],
            )
        return (
            "A student has $20 and must choose between buying a revision guide and going to the cinema. Explain how scarcity creates an economic choice.",
            ["Identify the limited resource.", "Name the two competing wants.", "Explain why a choice has to be made."],
            ["The limited resource is the student's $20.", "The student wants both the revision guide and the cinema trip.", "Because the money is scarce, both wants cannot be satisfied at the same time.", "So the student must choose one option and give up the other."],
            ["Names the scarce resource.", "Uses needs/wants or choice language.", "Explains why not all wants can be satisfied."],
        )
    if any(word in text for word in ["specialisation", "division of labour", "exchange"]):
        if number % 2:
            return (
                "A car factory splits production into design, assembly and quality-checking teams. Explain how specialisation can improve output and give one risk.",
                ["Identify specialised tasks.", "Explain one productivity benefit.", "Give one possible risk."],
                ["Workers and teams focus on particular tasks.", "This can increase output because workers build skill and save time switching tasks.", "One risk is that work may become repetitive or production may stop if one stage fails.", "So specialisation can raise efficiency but can create dependence between stages."],
                ["Benefit and risk are both present.", "The answer uses the factory context.", "It links specialisation to output."],
            )
        return (
            "In a sandwich shop, one worker prepares bread, one adds fillings and one handles payments. Explain one benefit and one possible cost of division of labour.",
            ["Describe the specialised roles.", "Give one benefit.", "Give one cost."],
            ["Each worker focuses on a narrow task.", "A benefit is higher output because workers become faster at their task.", "A possible cost is boredom or lower motivation from repeated work.", "So division of labour can raise productivity but may affect workers negatively."],
            ["Benefit and cost are both included.", "The answer uses the sandwich-shop scenario.", "It links specialisation to productivity."],
        )
    if any(word in text for word in ["factor", "land", "capital", "enterprise"]):
        if number % 2:
            return (
                "A delivery business uses vans, drivers, fuel and a founder who organises the firm. Classify each resource as land, labour, capital or enterprise.",
                ["Identify natural resources.", "Identify human effort.", "Separate man-made equipment from enterprise."],
                ["Fuel is land because it comes from natural resources.", "Drivers are labour because they provide human effort.", "Vans are capital because they are man-made equipment used in production.", "The founder is enterprise because they organise resources and take risk."],
                ["All resources are classified.", "Capital means equipment, not just money.", "Enterprise is linked to organisation and risk."],
            )
        return (
            "A bakery uses wheat, ovens, workers and an owner who takes the business risk. Classify each as a factor of production.",
            ["Match each resource to land, labour, capital or enterprise.", "State the reward for at least one factor.", "Keep the classification tied to the scenario."],
            ["Wheat is land because it is a natural resource.", "Workers are labour because they provide human effort.", "Ovens are capital because they are man-made equipment used in production.", "The owner is enterprise because they organise resources and take risk."],
            ["All four factors are classified.", "Capital is not money in this context; it is equipment.", "Enterprise is linked to risk and organisation."],
        )
    if any(word in text for word in ["opportunity cost", "resource allocation", "making choices"]):
        if number % 2:
            return (
                "A government can spend the same budget on either a new clinic or a sports centre. If it chooses the clinic, explain the opportunity cost.",
                ["Identify the chosen project.", "Identify the next best alternative.", "State what is given up."],
                ["The chosen project is the clinic.", "The next best alternative is the sports centre.", "The opportunity cost is the sports centre that cannot be built with the same budget.", "So opportunity cost is the value of the next best alternative forgone."],
                ["Only the next best alternative is counted.", "The answer uses the budget constraint.", "The forgone option is named."],
            )
        return (
            "A school can use one classroom for either an economics club or a revision workshop. Explain the opportunity cost of choosing the economics club.",
            ["Identify the chosen option.", "Identify the next best alternative given up.", "State opportunity cost clearly."],
            ["The school chooses the economics club.", "The next best alternative is the revision workshop.", "The opportunity cost is the revision workshop that cannot happen in that classroom.", "Answer: opportunity cost is the value of the next best alternative forgone."],
            ["Opportunity cost is not every possible alternative.", "The answer names the forgone option.", "The context is used."],
        )
    if any(word in text for word in ["sector", "goods and services", "primary", "secondary", "tertiary"]):
        if number % 2:
            return (
                "Classify a fishing boat, a canned-fish factory and a supermarket into economic sectors.",
                ["Match each activity to a sector.", "Explain each classification briefly.", "Separate production from selling."],
                ["The fishing boat is primary because it extracts a natural resource.", "The canned-fish factory is secondary because it manufactures a product.", "The supermarket is tertiary because it provides retail services to consumers.", "Answer: primary, secondary and tertiary respectively."],
                ["Each sector is used once.", "Manufacturing is secondary.", "Retail service is tertiary."],
            )
        return (
            "Classify a wheat farm, a flour mill and a bakery cafe into economic sectors, then explain the difference between a good and a service.",
            ["Identify primary, secondary and tertiary activities.", "Classify each business.", "Separate goods from services."],
            ["The wheat farm is primary because it extracts or grows raw materials.", "The flour mill is secondary because it manufactures a product.", "The bakery cafe is tertiary when it sells food and service to customers.", "A good is a physical item; a service is an activity provided for someone."],
            ["Each sector is named correctly.", "The cafe example includes service.", "The answer does not treat every business as one sector automatically."],
        )
    if any(word in text for word in ["demand", "supply", "price", "equilibrium", "market"]):
        if number % 2:
            return (
                "A drought reduces the supply of oranges while demand stays unchanged. Explain the likely effect on equilibrium price and quantity.",
                ["Identify the supply change.", "State the direction of the shift.", "Explain the new equilibrium."],
                ["A drought reduces supply, so the supply curve shifts left.", "At the old price there is excess demand.", "The equilibrium price is likely to rise.", "The equilibrium quantity is likely to fall."],
                ["Uses supply, not demand, as the cause.", "Explains price and quantity.", "Keeps demand unchanged."],
            )
        return (
            "A new phone becomes more popular. Using demand and supply, explain what is likely to happen to its market price, assuming supply is unchanged.",
            ["Identify which curve changes.", "State the direction of the shift.", "Explain the effect on equilibrium price."],
            ["Popularity affects demand, not supply.", "Demand shifts to the right.", "At the old price there is excess demand.", "Market price is likely to rise to a new equilibrium."],
            ["Uses demand, not just 'people like it'.", "Supply is held unchanged.", "Explains the price rise through excess demand."],
        )
    if "elasticity" in text:
        if number % 2:
            return (
                "Price falls by 20% and quantity demanded rises by 40%. Calculate price elasticity of demand and state whether demand is elastic or inelastic.",
                ["Use PED = percentage change in quantity demanded / percentage change in price.", "Substitute the percentages.", "Interpret the absolute value."],
                ["PED = 40% / -20%.", "PED = -2.", "The absolute value is 2, which is greater than 1.", "Demand is price elastic."],
                ["Quantity demanded is divided by price.", "The sign is interpreted carefully.", "Elasticity judgement uses absolute value."],
            )
        return (
            "Price rises by 10% and quantity demanded falls by 5%. Calculate price elasticity of demand and state whether demand is elastic or inelastic.",
            ["Use PED = percentage change in quantity demanded / percentage change in price.", "Substitute the two percentages.", "Interpret the absolute value."],
            ["PED = -5% / 10%.", "PED = -0.5.", "The absolute value is 0.5, which is less than 1.", "Demand is price inelastic."],
            ["Quantity demanded change is divided by price change.", "The negative sign is expected for demand.", "Elastic/inelastic judgement uses absolute value."],
        )
    if any(word in text for word in ["cost", "revenue", "profit", "production"]):
        if number % 2:
            return (
                "A firm sells 150 units at $12 each. Its total cost is $1,350. Calculate total revenue and profit.",
                ["Total revenue = price x quantity.", "Profit = total revenue - total cost.", "Keep the currency."],
                ["Total revenue = $12 x 150 = $1,800.", "Profit = $1,800 - $1,350.", "Profit = $450.", "Answer: total revenue $1,800; profit $450."],
                ["Revenue is calculated before profit.", "Cost is subtracted once.", "Currency is shown."],
            )
        return (
            "A producer sells 200 units at $8 each. Total cost is $1,100. Calculate total revenue and profit.",
            ["Total revenue = price x quantity.", "Profit = total revenue - total cost.", "Keep the currency."],
            ["Total revenue = $8 x 200 = $1,600.", "Profit = $1,600 - $1,100.", "Profit = $500.", "Answer: total revenue $1,600; profit $500."],
            ["Revenue is not the same as profit.", "Costs are subtracted after revenue is calculated.", "Currency is shown."],
        )
    if any(word in text for word in ["government", "inflation", "growth", "employment", "income", "balance of payments"]):
        if number % 2:
            return (
                "A government cuts taxes to reduce unemployment. Explain one possible benefit and one possible inflation risk.",
                ["Identify the policy effect on spending.", "Link spending to jobs.", "Explain the inflation risk."],
                ["Lower taxes can increase households' disposable income.", "Higher spending may raise demand for goods and services, encouraging firms to hire more workers.", "If demand rises faster than output, prices may rise.", "So the policy may reduce unemployment but create inflationary pressure."],
                ["Benefit and risk are both included.", "Uses demand as the link.", "Avoids saying the outcome is guaranteed."],
            )
        return (
            "A government wants lower inflation and faster economic growth at the same time. Explain why these objectives might conflict.",
            ["Name both objectives.", "Explain the policy tension.", "Give a balanced conclusion."],
            ["Lower inflation may require policies that reduce spending in the economy.", "Reduced spending can slow output growth.", "Faster growth may increase demand and put upward pressure on prices.", "So policies for one objective can make the other harder to achieve."],
            ["Both objectives are named.", "The answer explains a trade-off.", "It avoids saying conflict always happens."],
        )
    if any(word in text for word in ["trade", "exchange rate", "globalisation", "import", "export"]):
        if number % 2:
            return (
                "A tariff is placed on imported shoes. Explain one likely effect on domestic consumers and one effect on domestic producers.",
                ["Define the import barrier effect.", "Apply it to consumers.", "Apply it to producers."],
                ["A tariff raises the cost of imported shoes.", "Consumers may face higher prices or less choice.", "Domestic producers may benefit because imported competitors become more expensive.", "So consumers may lose, while some domestic producers may gain."],
                ["Consumers and producers are separated.", "The price effect is clear.", "The answer avoids claiming everyone benefits."],
            )
        return (
            "A country's currency appreciates. Explain one likely effect on exporters and one likely effect on consumers buying imports.",
            ["Define the direction of the exchange-rate change.", "Apply it to export prices.", "Apply it to import prices."],
            ["Appreciation means the currency becomes stronger.", "Exports may become more expensive for foreign buyers, so exporters may sell less.", "Imports become cheaper for domestic consumers.", "Answer: exporters may lose competitiveness, while consumers may benefit from cheaper imports."],
            ["Exporter and consumer effects are separated.", "The direction of price change is correct.", "The answer links to competitiveness."],
        )
    if any(word in text for word in ["money", "bank", "financial", "interest"]):
        if number % 2:
            return (
                "A central bank raises interest rates. Explain one likely effect on saving and one likely effect on borrowing.",
                ["Identify the interest-rate change.", "Apply it to savers.", "Apply it to borrowers."],
                ["Higher interest rates increase the reward for saving.", "Savers may choose to save more.", "Borrowing becomes more expensive because loan repayments or interest costs rise.", "So borrowing may fall while saving may rise."],
                ["Saving and borrowing are both covered.", "Direction of change is correct.", "The answer uses incentives."],
            )
        return (
            "Explain how a commercial bank can help savers and borrowers in the economy.",
            ["Identify the two groups.", "Explain the service for savers.", "Explain the service for borrowers."],
            ["Savers can deposit money and earn interest.", "Borrowers can receive loans for spending or investment.", "The bank links people with surplus funds to people who need funds.", "This supports saving, borrowing and investment in the economy."],
            ["Mentions savers and borrowers.", "Uses the role of a bank, not just money storage.", "Links to the wider economy."],
        )
    return (
        f"Use the economics idea '{focus}' in a short market scenario: identify the economic agent, explain the incentive, and state the likely outcome.",
        ["Name the economic agent.", "Identify the incentive or constraint.", "Explain the likely outcome."],
        [f"The focus idea is {focus}.", "Apply it to a consumer, producer or government decision.", "Explain how incentives or scarcity affect the decision.", "Finish with the likely economic outcome."],
        ["Uses an economics agent.", "Explains a cause-and-effect link.", "Avoids unsupported real-world claims."],
    )


def build_visual_brief(
    topic: Topic,
    guide: TopicGuide,
    run_options: GuideRunOptions,
    subject_area: str | None = None,
) -> VisualBrief | None:
    points = topic.points[:4] or [topic.title]
    focus = points[0]
    visual_type, complexity, trigger = choose_visual_type(topic, points, subject_area)
    if complexity == "text-ok":
        return None
    provider = choose_provider_for_visual(complexity, run_options)
    if run_options.output_language == "en":
        visible_focus = focus
        visible_points = points
        visible_visual_type = visual_type
        visible_trigger = trigger
        prompt = (
            f"Create a student-friendly International GCSE revision visual for '{topic.title}'. "
            f"Focus on the syllabus point '{focus}'. Visual type: {visual_type}. "
            "Combine a clear diagram or infographic with concise English labels. "
            "Use original educational styling, not copyrighted characters or copied exam-paper art. "
            "Do not add facts beyond these source syllabus points: "
            f"{'; '.join(points)}. Leave space for a short question and answer frame."
        )
    else:
        visible_focus = zh_point_label(focus)
        visible_points = zh_point_labels(points)
        visible_visual_type = zh_visual_type(visual_type)
        visible_trigger = zh_visual_trigger(trigger)
        prompt = (
            f"为“{zh_topic_reference(topic)}”制作一张适合学生复习的国际课程图文学习图。"
            f"聚焦：“{visible_focus}”。图形类型：{visible_visual_type}。"
            "画面需要把清晰图解或信息图与简短中文标签结合起来；公式、单位和必要符号保持准确。"
            "使用原创教育风格，不使用受版权保护的角色，也不要复制考试卷图片。"
            "不要添加超出这些来源大纲点的事实；官方英文来源仅用于结构化复核，不出现在学生可见标签中。"
            f"可见标签围绕：{'；'.join(visible_points)}。预留一个简短题目和答题框架的位置。"
        )
    return VisualBrief(
        topic_title=topic.title,
        focus_point=visible_focus,
        trigger=visible_trigger,
        visual_type=visible_visual_type,
        complexity=complexity,
        image_provider=provider,
        prompt=prompt,
        source_points=points,
        source_snippets=topic.source_snippets[:2],
    )


def choose_visual_type(
    topic: Topic,
    points: list[str],
    subject_area: str | None = None,
) -> tuple[str, str, str]:
    text = f"{topic.title} {' '.join(points)}".lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    has = tokens.__contains__
    has_phrase = text.__contains__
    profile = resolve_subject_profile(subject_area, topic, text)

    if profile.example_domain == "accounting":
        if any(has(word) for word in ["source", "document", "documents", "journal", "ledger", "ledgers", "entry", "entries"]):
            return "source-document to book-of-prime-entry and ledger flow infographic", "infographic", "accounting records are clearer as a source-to-ledger flow"
        if any(has(word) for word in ["trial", "balance", "control", "reconciliation", "bank", "error", "errors", "suspense"]):
            return "verification and reconciliation workflow infographic", "infographic", "verification topics need step-by-step comparison and correction flow"
        if any(has(word) for word in ["depreciation", "receivables", "payables", "irrecoverable", "accruals", "prudence", "concepts"]):
            return "accounting adjustment and concept-effect infographic", "infographic", "adjustments need linked record, statement, and profit effects"
        if any(has(word) for word in ["statement", "statements", "profit", "position", "partnership", "company", "manufacturing", "non-profit"]):
            return "financial-statement layout and calculation infographic", "infographic", "financial statements need layout plus calculation path"
        if any(has(word) for word in ["ratio", "liquidity", "profitability", "analysis"]):
            return "ratio-analysis formula and interpretation infographic", "infographic", "ratios need formula, substitution, and interpretation together"
        return "accounting process infographic with records and statement effects", "infographic", "accounting ideas are clearer with documents, accounts, and statement effects linked"

    if profile.example_domain == "economics":
        if any(has(word) for word in ["demand", "supply", "market", "price", "equilibrium", "elasticity"]):
            return "demand-supply curve and market scenario infographic", "infographic", "market relationships need curve shifts plus context labels"
        if any(has(word) for word in ["factor", "factors", "land", "labour", "capital", "enterprise", "production"]):
            return "factors of production scenario infographic", "infographic", "production resources are clearer as a labelled real-world scenario"
        if any(has(word) for word in ["scarcity", "choice", "choices", "opportunity", "cost", "costs", "allocation"]):
            return "choice and opportunity-cost flow infographic", "infographic", "economic choice is clearer as a trade-off flow"
        if any(has(word) for word in ["sector", "sectors", "primary", "secondary", "tertiary"]):
            return "economic sectors production-chain infographic", "infographic", "sector classification works best as a chain from raw material to service"
        if any(has(word) for word in ["money", "bank", "financial", "interest"]):
            return "money and banking flow infographic", "infographic", "financial roles are clearer as flows between savers, banks, and borrowers"
        if any(has(word) for word in ["government", "inflation", "growth", "employment", "trade", "exchange", "imports", "exports"]):
            return "policy and trade cause-effect infographic", "infographic", "macroeconomic relationships need cause-effect arrows and trade-offs"
        if any(has(word) for word in ["business", "revenue", "profit", "profits", "cash"]):
            return "business case-study canvas with icons and flow arrows", "infographic", "business/accounting cases benefit from icon flow and statement layout"
        return "scenario infographic with curve or flow chart", "infographic", "economic relationships are clearer as curves, flows, or scenarios"

    if profile.example_domain == "chemistry":
        if any(has(word) for word in ["chromatography", "purity", "pure", "mixture", "mixtures", "separation"]):
            return "chromatography and purity lab-method infographic", "infographic", "separation methods and purity checks need a labelled apparatus/process visual"
        if any(has(word) for word in ["gas", "gases", "splint", "limewater", "ammonia", "oxygen", "hydrogen"]):
            return "common gas tests observation infographic", "infographic", "gas tests need apparatus, observation, and conclusion labels"
        if any(has(word) for word in ["solid", "liquid", "liquids", "particle", "particles", "atom", "atoms"]):
            return "particle model with labelled states", "svg-basic", "state changes are clearer with particle arrangement and movement"
        if any(has(word) for word in ["bond", "bonds", "bonding", "ionic", "covalent", "metallic", "structure", "structures"]):
            return "bonding and structure model", "infographic", "bonding and structure relationships need visual spatial explanation"
        if any(has(word) for word in ["acid", "acids", "base", "bases", "alkali", "alkalis", "salt", "salts", "ph"]):
            return "pH scale and preparation flow diagram", "svg-basic", "scales and preparation flow are clearer as diagrams"
        if any(has(word) for word in ["rate", "rates", "equilibrium", "haber"]):
            return "reaction-rate graph and particle explanation", "infographic", "rate and equilibrium need graph plus particle interpretation"
        if any(has(word) for word in ["energy", "exothermic", "endothermic"]):
            return "reaction energy profile diagram", "svg-basic", "energy profile curves are visual by nature"
        if any(has(word) for word in ["organic", "hydrocarbon", "hydrocarbons", "polymer", "polymers", "crude", "carboxylic"]):
            return "organic structure and reaction pathway infographic", "infographic", "organic structures and pathways need labelled visual representation"
        if any(has(word) for word in ["electrolysis", "reactivity", "mole", "moles", "molar", "concentration", "concentrations"]):
            return "chemistry calculation and process infographic", "infographic", "chemistry process and quantity topics need linked formula, particles, and observations"

    if profile.example_domain == "generic":
        if any(has(word) for word in ["graph", "graphs", "table", "tables", "data", "measurement", "measurements"]):
            return "data table and graph interpretation visual", "svg-basic", "data handling and graph reading are clearer with annotated visuals"
        return "text explanation with concept map only", "text-ok", "plain source-bound explanation is sufficient"

    if any(has(word) for word in ["set", "sets", "subset", "subsets", "venn", "union", "intersection"]):
        return "set notation and Venn diagram infographic", "infographic", "set notation needs Venn regions and symbol labels, not a generic statistics chart"
    if any(
        has(word)
        for word in [
            "number",
            "numbers",
            "fraction",
            "fractions",
            "percentage",
            "percentages",
            "decimal",
            "decimals",
            "ratio",
            "proportion",
        ]
    ):
        return "number line, fraction bar, and ratio visual", "svg-basic", "number work is clearer with position, part-whole, and proportion diagrams"

    if any(has(word) for word in ["matrix", "matrices", "vector", "vectors", "transformation", "transformations"]):
        return "transformation, matrix, or vector infographic", "infographic", "multi-step geometry movement and vector reasoning need a richer labelled visual"
    if any(has(word) for word in ["construction", "constructions", "locus", "loci", "bearing", "bearings"]):
        return "geometry construction or bearings infographic", "infographic", "construction and bearings diagrams need precise labels and step annotations"
    if any(has(word) for word in ["histogram", "histograms", "cumulative", "sampling", "population"]):
        return "statistics method infographic", "infographic", "statistical representations need the exact chart type instead of a generic SVG"
    if any(has(word) for word in ["calculus", "tangent", "gradient"]):
        return "calculus graph annotation infographic", "infographic", "calculus and gradient reasoning need carefully annotated graph features"

    if any(
        has(word)
        for word in [
            "algebra",
            "function",
            "functions",
            "equation",
            "equations",
            "inequality",
            "inequalities",
            "sequence",
            "sequences",
        ]
    ):
        return "function graph and equation-balance visual", "svg-basic", "algebra is clearer when symbols connect to graphs and transformations"
    if any(
        has(word)
        for word in [
            "triangle",
            "triangles",
            "angle",
            "angles",
            "pythagoras",
        ]
    ):
        return "simple labelled triangle or angle diagram", "svg-basic", "simple geometry can be drawn accurately with deterministic SVG"
    if any(has(word) for word in ["geometry", "geometric", "measure", "measures", "mensuration", "trigonometry", "circle", "circles", "volume", "surface"]):
        return "geometry or mensuration infographic", "infographic", "non-trivial geometry needs diagrams that match the exact shape and labels"
    if any(
        has(word)
        for word in [
            "probability",
            "statistics",
            "statistical",
            "chart",
            "charts",
            "scatter",
            "correlation",
            "distribution",
            "distributions",
        ]
    ):
        return "statistics chart and probability visual", "svg-basic", "statistics and probability are clearer with charts, tables, and chance diagrams"
    if has_phrase("distance-time") or any(has(word) for word in ["speed", "distance"]):
        return "distance-time graph visual", "svg-basic", "distance-time graphs can be drawn safely with deterministic axes and a labelled line"
    if any(has(word) for word in ["force", "forces", "motion"]):
        return "force and motion infographic", "infographic", "force and motion questions need context-specific arrows and labels"
    if any(has(word) for word in ["graph", "graphs", "table", "tables", "data", "measurement", "measurements"]):
        return "data table and graph interpretation visual", "svg-basic", "data handling and graph reading are clearer with annotated visuals"
    return "text explanation with concept map only", "text-ok", "plain source-bound explanation is sufficient"


def choose_provider_for_visual(complexity: str, run_options: GuideRunOptions) -> str:
    if complexity == "svg-basic":
        return "deterministic-svg"
    if run_options.image_provider in {"prompt-queue", "deterministic-svg"}:
        return "external-generation-required"
    if run_options.image_provider == "custom":
        return f"custom:{run_options.image_model or 'model-not-set'}"
    return run_options.image_provider


def zh_visual_type(visual_type: str) -> str:
    text = visual_type.lower()
    if "chromatography" in text or "lab" in text:
        return "实验流程信息图"
    if "gas" in text:
        return "气体检验观察信息图"
    if "particle" in text or "states" in text:
        return "粒子模型示意图"
    if "bond" in text or "structure" in text:
        return "结构与性质关系信息图"
    if re.search(r"\bph\b", text) or "acid" in text or "alkali" in text or "neutralisation" in text:
        return "酸碱与流程示意图"
    if "demand" in text or "supply" in text or "market" in text:
        return "市场曲线与情境信息图"
    if "production" in text:
        return "生产要素场景信息图"
    if "set" in text or "venn" in text:
        return "集合与韦恩图信息图"
    if "triangle" in text or "geometry" in text:
        return "几何标注图"
    if "statistics" in text or "probability" in text:
        return "统计与概率图表"
    return "图文结合学习图"


def zh_visual_trigger(trigger: str) -> str:
    text = trigger.lower()
    if "apparatus" in text or "process" in text:
        return "需要同时看清装置、步骤和观察结果，单纯文字不够直观。"
    if "spatial" in text or "structure" in text:
        return "结构关系需要空间示意，单纯文字容易误解。"
    if "curve" in text or "graph" in text:
        return "曲线、坐标或移动方向需要图上标注。"
    if "scenario" in text or "flow" in text:
        return "场景、因果和流程需要用箭头串起来。"
    return "这个知识点用图文结合更容易理解和复习。"


def build_revision_stages(qualification_type: str, output_language: str = "en") -> list[str]:
    if output_language == "zh-CN":
        if qualification_type == "international_as_a_level":
            return [
                "第 1 阶段 - 单元地图：先分清 AS、A2 或模块单元，再做综合题。",
                "第 2 阶段 - 建构：把每个单元点整理成短讲解、一道应用题和一个易错点。",
                "第 3 阶段 - 测试：先按单元练，再在指令词和来源边界稳定后做综合练习。",
            ]
        return [
            "第 1 阶段 - 线性地图：先掌握整门课的主题边界，再进入混合题。",
            "第 2 阶段 - 建构：把每个大纲点整理成一页笔记、一道例题和一个易错点。",
            "第 3 阶段 - 测试：练习整卷混合题，复盘错题，并每周更新检查清单。",
        ]
    if qualification_type == "international_as_a_level":
        return [
            "Stage 1 - Unit map: separate AS and A2 or modular units before mixing questions.",
            "Stage 2 - Build: turn each unit point into a short explanation, one application prompt, and one pitfall.",
            "Stage 3 - Test: practise by unit first, then combine units once command words and source boundaries are secure.",
        ]
    return [
        "Stage 1 - Linear map: learn the full-course topic boundaries before doing mixed papers.",
        "Stage 2 - Build: turn each syllabus point into a one-page note, one worked example, and one pitfall.",
        "Stage 3 - Test: practise mixed end-of-course questions, review errors, and update the checklist weekly.",
    ]


def choose_command_word(number: int, qualification_type: str, output_language: str = "en") -> str:
    if output_language == "zh-CN":
        if qualification_type == "international_as_a_level":
            words = ["解释", "分析", "比较", "评价"]
        else:
            words = ["写出", "描述", "解释", "提出"]
        return words[number % len(words)]
    if qualification_type == "international_as_a_level":
        words = ["explain", "analyse", "compare", "evaluate"]
    else:
        words = ["state", "describe", "explain", "suggest"]
    return words[number % len(words)]


def choose_difficulty(number: int, output_language: str = "en") -> str:
    if output_language == "zh-CN":
        return ["基础", "标准", "挑战"][number % 3]
    return ["core", "standard", "stretch"][number % 3]
