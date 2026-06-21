from intl_exam_guide.models import Topic
from intl_exam_guide.planning.localization import (
    zh_point_labels,
    zh_topic_reference,
    zh_visual_trigger,
)


def test_zh_topic_reference_uses_topic_code_or_generic_reference():
    assert zh_topic_reference(Topic(title="A2 Ledger entries")) != zh_topic_reference(
        Topic(title="Ledger entries")
    )
    assert "A2" in zh_topic_reference(Topic(title="A2 Ledger entries"))
    assert "3.1" in zh_topic_reference(Topic(title="3.1 Source documents"))


def test_zh_point_labels_maps_known_keywords_and_keeps_chinese_text():
    labels = zh_point_labels(
        [
            "source document purchase invoice",
            "demand and supply market",
            "triangle geometry construction",
            "已经是中文考点，应该保留原文",
            "unmatched source statement",
        ]
    )

    assert len(labels) == 5
    assert len(set(labels[:3])) == 3
    assert labels[3] == "已经是中文考点，应该保留原文"[:24]
    assert labels[4].endswith("5")


def test_zh_visual_trigger_covers_process_structure_graph_flow_and_default_routes():
    triggers = {
        "apparatus process observation": "process",
        "spatial structure model": "structure",
        "curve graph movement": "graph",
        "scenario flow relationship": "flow",
        "plain visual support": "default",
    }
    outputs = {name: zh_visual_trigger(trigger) for trigger, name in triggers.items()}

    assert set(outputs) == {"process", "structure", "graph", "flow", "default"}
    assert len(set(outputs.values())) == 5
    assert all(output for output in outputs.values())
