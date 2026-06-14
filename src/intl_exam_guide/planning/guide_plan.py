from __future__ import annotations

from intl_exam_guide.models import GuidePlan, PracticeItem, Qualification, Topic, TopicGuide


def build_guide_plan(qualification: Qualification, questions_per_topic: int = 2) -> GuidePlan:
    topic_guides: list[TopicGuide] = []
    practice_items: list[PracticeItem] = []
    diagram_briefs: list[str] = []

    for topic in qualification.topics:
        points = topic.points[:4]
        if not points:
            points = [topic.title]
        guide = build_topic_guide(topic, qualification.qualification_type)
        topic_guides.append(guide)
        diagram_briefs.append(guide.diagram_brief)
        for number in range(questions_per_topic):
            focus = points[number % len(points)]
            command_word = choose_command_word(number, qualification.qualification_type)
            difficulty = choose_difficulty(number)
            practice_items.append(
                PracticeItem(
                    topic_title=topic.title,
                    command_word=command_word,
                    difficulty=difficulty,
                    focus_point=focus,
                    question=(
                        f"{command_word.title()} how the syllabus idea '{focus}' could be used in "
                        f"an exam question on '{topic.title}'. Use a short scenario, one precise "
                        "syllabus term, and a final checking sentence."
                    ),
                    answer_frame=[
                        f"Line 1: answer the command word '{command_word}'.",
                        f"Line 2: state the relevant idea from the syllabus point '{focus}'.",
                        "Line 3: apply the idea to the given situation or data.",
                        "Line 4: check units, wording, and whether the answer addresses the command word.",
                    ],
                    public_solution_steps=[
                        f"Read the command word: {command_word}.",
                        f"Select the source-bound focus point: {focus}.",
                        "Write one sentence that defines or names the relevant idea.",
                        "Write one sentence that applies the idea to the scenario or data.",
                        "Finish with a checking sentence that matches the wording of the question.",
                    ],
                    answer_checkpoints=[
                        "Uses the command word directly.",
                        f"Mentions the focus point: {focus}.",
                        "Links the point to the scenario instead of only listing a memorised fact.",
                    ],
                    source_points=points,
                    source_snippets=topic.source_snippets[:2],
                )
            )

    revision_stages = build_revision_stages(qualification.qualification_type)
    return GuidePlan(
        qualification=qualification,
        topic_guides=topic_guides,
        practice_items=practice_items,
        diagram_briefs=diagram_briefs,
        revision_stages=revision_stages,
    )


def build_topic_guide(topic: Topic, qualification_type: str) -> TopicGuide:
    points = topic.points[:5] or [topic.title]
    primary = points[0]
    level_hint = "AS/A-level unit" if qualification_type == "international_as_a_level" else "GCSE topic"
    return TopicGuide(
        topic_title=topic.title,
        essence=(
            f"This {level_hint} is bounded by the official syllabus points around "
            f"'{primary}'. Start by turning each point into a definition, a process, "
            "or an application task."
        ),
        analogy=(
            f"Think of '{topic.title}' as a small toolkit: each syllabus point is one tool, "
            "and exam questions ask the student to choose the right tool for the command word."
        ),
        mini_worked_example=(
            f"Mini example: a question asks the student to explain or apply '{primary}' in a short "
            "scenario. The student should identify the command word, name the relevant idea, "
            "apply it to the scenario, and finish with a checking sentence."
        ),
        worked_solution_steps=[
            "Underline the command word: state, describe, explain, calculate, compare, evaluate, or suggest.",
            f"Select the matching syllabus point: {primary}.",
            "Use one precise term from the syllabus and connect it to the data or context in the question.",
            "Check that the final sentence answers the exact wording of the prompt.",
        ],
        pitfall=(
            "A common pitfall is writing a memorised fact without linking it to the command word. "
            "Train the student to ask: what action does this question want me to perform?"
        ),
        checklist=[
            *[f"Can explain: {point}" for point in points[:4]],
            "Can answer at least one original exam-style prompt without looking at notes.",
            "Can name one common mistake and how to avoid it.",
        ],
        diagram_brief=(
            f"Draw a clean concept map for '{topic.title}' with the central title in the middle, "
            f"branches for {', '.join(points[:4])}, and one short exam-action label on each branch."
        ),
        source_snippets=topic.source_snippets[:3],
    )


def build_revision_stages(qualification_type: str) -> list[str]:
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


def choose_command_word(number: int, qualification_type: str) -> str:
    if qualification_type == "international_as_a_level":
        words = ["explain", "analyse", "compare", "evaluate"]
    else:
        words = ["state", "describe", "explain", "suggest"]
    return words[number % len(words)]


def choose_difficulty(number: int) -> str:
    return ["core", "standard", "stretch"][number % 3]
