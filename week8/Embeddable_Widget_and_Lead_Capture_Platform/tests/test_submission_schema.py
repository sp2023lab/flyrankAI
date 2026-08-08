import pytest
from pydantic import ValidationError
from app.schemas.submissions import SubmissionBody

def test_honeypot_alias_parses():
    body=SubmissionBody.model_validate({"fields":{"email":"a@example.com"},"_website":""})
    assert body.honeypot == ""

def test_unknown_outer_key_is_rejected():
    with pytest.raises(ValidationError):
        SubmissionBody.model_validate({"fields":{},"unknown":1})
