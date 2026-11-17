import os
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

from gradio_app import create_demo, on_ticket_select, resolve_ticket, approve_action, reject_action


def test_on_ticket_select():
    ticket_id, customer, text = on_ticket_select("T-1001 - Asha (I see two charges...)")
    assert ticket_id == "T-1001"
    assert customer == "Asha"
    assert "ORD-1042" in text


def test_empty_ticket_select():
    ticket_id, customer, text = on_ticket_select("")
    assert ticket_id == ""
    assert customer == ""
    assert text == ""


def test_invalid_ticket_id():
    draft, warning, approval_visible, decision_visible, status = resolve_ticket("INVALID")
    assert "Invalid Ticket ID Format" in warning


def test_approval_actions():
    app_res = approve_action("T-1001")
    assert "Approved" in app_res
    rej_res = reject_action("T-1001")
    assert "Rejected" in rej_res


def test_demo_creates_successfully():
    demo = create_demo()
    assert demo is not None
