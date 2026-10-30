
from src.ai_explainer import (
    explain_word,
    simplify_paragraph
)

sentence = (
    "The proposed methodology mitigates "
    "computational overhead while maintaining "
    "predictive accuracy."
)

print("=== VOCABULARY EXPLANATION ===")

result = explain_word(
    word="mitigates",
    context=sentence,
    level="B1"
)

print(result)

print("\n=== PARAGRAPH EXPLANATION ===")

result = simplify_paragraph(
    paragraph=sentence,
    level="A2"
)

print(result)
