# pii_guard.py

import re
from app.guard_rails.pii_pattenns import PII_PATTERNS


class PIIGuard:
    def __init__(self):
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

        
        self.ner_labels = set()

    def detect_regex_pii(self, text: str):
        detected = {}

        for label, pattern in PII_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detected[label] = matches

        return detected

 
    def detect_ner_pii(self, text: str):
        if self.nlp is None:
            return {}

        doc = self.nlp(text)
        detected = {}

        for ent in doc.ents:
            if ent.label_ in self.ner_labels:
                detected.setdefault(ent.label_, []).append(ent.text)

        return detected

    def detect_all(self, text: str):
        regex_pii = self.detect_regex_pii(text)
        ner_pii = self.detect_ner_pii(text)

        combined = regex_pii.copy()

        for label, values in ner_pii.items():
            combined.setdefault(label, []).extend(values)

        return combined

    def mask(self, text: str):
        detected = self.detect_all(text)

        for label, values in detected.items():
            for value in set(values):
                text = text.replace(value, f"[{label}]")

        return text, detected
