import re

INJECTION_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"disregard (above|previous)",
    r"reveal (system|hidden) prompt",
    r"show .*api key",
    r"bypass security",
]

class PromptInjectionGuard:

    def detect(self, text: str) -> bool:
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False