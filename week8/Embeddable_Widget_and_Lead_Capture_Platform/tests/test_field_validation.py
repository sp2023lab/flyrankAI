import pytest
from app.core.errors import InvalidSubmission
from app.services.field_validation import validate_widget_fields

FIELDS = [
    {"name":"name","type":"text","required":True,"max_length":10},
    {"name":"email","type":"email","required":True,"max_length":254},
]

def test_valid_fields_are_returned_clean():
    assert validate_widget_fields(FIELDS, {"name":"Ada","email":"ada@example.com"}) == {"name":"Ada","email":"ada@example.com"}

@pytest.mark.parametrize("payload,reason", [
    ({"email":"ada@example.com"}, "required"),
    ({"name":"Ada","email":"bad"}, "invalid_email"),
    ({"name":"Ada","email":"ada@example.com","admin":True}, "unexpected_field"),
    ({"name":"01234567890","email":"ada@example.com"}, "too_long"),
])
def test_bad_fields_raise_clean_validation(payload, reason):
    with pytest.raises(InvalidSubmission) as exc:
        validate_widget_fields(FIELDS, payload)
    assert any(e["reason"] == reason for e in exc.value.details)
