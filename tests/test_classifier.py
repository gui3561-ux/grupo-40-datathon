from src.ml.predict import load_classifier


def test_technical_ticket_predicted_as_technical() -> None:
    classifier = load_classifier()
    category, confidence = classifier.predict(
        "O Wi-Fi do roteador cai e o DHCP nao entrega IP na rede local."
    )
    assert category == "technical"
    assert confidence > 0.4
