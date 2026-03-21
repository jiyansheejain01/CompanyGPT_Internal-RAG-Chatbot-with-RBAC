from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

PII_ENTITIES = [
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "CREDIT_CARD",
    "US_SSN",
    "IP_ADDRESS",
    "PERSON",
    "LOCATION",
    "DATE_TIME",
    "IBAN_CODE",
    "US_BANK_NUMBER"
]


def detect_pii(text: str) -> list:
    results = analyzer.analyze(
        text=text,
        entities=PII_ENTITIES,
        language="en"
    )
    return results


def mask_pii(text: str) -> tuple[str, bool]:
    results = detect_pii(text)
    if not results:
        return text, False

    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators={
            "PHONE_NUMBER":    OperatorConfig("replace", {"new_value": "<PHONE>"}),
            "EMAIL_ADDRESS":   OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            "CREDIT_CARD":     OperatorConfig("replace", {"new_value": "<CREDIT_CARD>"}),
            "US_SSN":          OperatorConfig("replace", {"new_value": "<SSN>"}),
            "IP_ADDRESS":      OperatorConfig("replace", {"new_value": "<IP>"}),
            "PERSON":          OperatorConfig("replace", {"new_value": "<PERSON>"}),
            "LOCATION":        OperatorConfig("replace", {"new_value": "<LOCATION>"}),
            "DATE_TIME":       OperatorConfig("replace", {"new_value": "<DATE>"}),
            "IBAN_CODE":       OperatorConfig("replace", {"new_value": "<IBAN>"}),
            "US_BANK_NUMBER":  OperatorConfig("replace", {"new_value": "<BANK_ACCOUNT>"}),
        }
    )
    return anonymized.text, True


if __name__ == "__main__":
    test = "Hi, my name is John Smith, email is john@atliq.com and SSN is 123-45-6789"
    masked, found = mask_pii(test)
    print(f"Original : {test}")
    print(f"Masked   : {masked}")
    print(f"PII found: {found}")
