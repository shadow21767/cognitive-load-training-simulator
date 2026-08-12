from config import load_study_config


def test_default_study_config():
    cfg = load_study_config()
    assert "study" in cfg
    assert "conditions" in cfg
    assert "Control" in cfg["conditions"]
