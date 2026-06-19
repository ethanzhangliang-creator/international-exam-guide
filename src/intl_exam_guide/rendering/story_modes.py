from __future__ import annotations

import html


def english_story_lines(title: str, focus: str, index: int) -> tuple[str, str, str]:
    escaped_title = html.escape(title, quote=True)
    escaped_focus = html.escape(focus, quote=True)
    variants = [
        (
            f"Treat <strong>{escaped_title}</strong> as a real situation: observe what changes, then explain it with <strong>{escaped_focus}</strong>.",
            "Read the question like a case file: data are clues, the syllabus term is evidence, and the final line must answer the command word.",
            "Turn the topic into a mission: unlock the term, avoid the common trap, and finish with one check sentence.",
        ),
        (
            f"Imagine the concept showing up in a school, shop, lab, or household decision. First name the visible action, then connect it to <strong>{escaped_focus}</strong>.",
            "Build the answer like an investigation: identify the suspect idea, test it against the evidence, then write the verdict precisely.",
            "Use a three-step route: collect the fact, choose the method, and check whether the answer would earn the final mark.",
        ),
        (
            f"Start with the everyday version of <strong>{escaped_title}</strong>: what would a person notice before they knew the technical word?",
            "Separate clues from noise. The useful clue is the one that proves the syllabus point, not the one that merely sounds familiar.",
            "Make the checkpoint explicit: term, evidence, conclusion. If one is missing, the answer is not finished.",
        ),
    ]
    return variants[(index - 1) % len(variants)]


def chinese_story_lines(title: str, focus: str, index: int) -> tuple[str, str, str]:
    escaped_title = html.escape(title, quote=True)
    escaped_focus = html.escape(focus, quote=True)
    variants = [
        (
            f"把 <strong>{escaped_title}</strong> 放进身边场景：先找看得见的现象，再用 <strong>{escaped_focus}</strong> 解释为什么。",
            "像破案一样答题：题干数据是线索，大纲术语是证据，最后一句必须回应指令词。",
            "把本节拆成三关：认出术语、避开陷阱、用一句检查句收尾。",
        ),
        (
            f"想象它出现在学校、商店、实验室或家庭决策里：先说发生了什么，再把它连回 <strong>{escaped_focus}</strong>。",
            "先筛线索：能证明知识点的才是关键证据，只是眼熟的词不一定有用。",
            "按“事实-方法-检查”走：拿到题干事实，选择解法，再确认答案能不能拿最后一分。",
        ),
        (
            f"先用普通话说清 <strong>{escaped_title}</strong>：如果不背术语，一个人会先观察到什么？",
            "把答案当作结案陈词：结论不能单独站着，前面必须有题干证据支撑。",
            "最后检查三件事：术语是否准确，证据是否来自题干，结论是否回答了问题。",
        ),
    ]
    return variants[(index - 1) % len(variants)]
