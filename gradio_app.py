import os
import json
from pathlib import Path

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

import gradio as gr

from agent import run_agent
from guardrails import validate_ticket_id, needs_human_approval, grounding_warnings

DATA_DIR = Path(__file__).parent / "data"


def load_tickets():
    ticket_file = DATA_DIR / "tickets.json"
    if ticket_file.exists():
        return json.loads(ticket_file.read_text(encoding="utf-8"))
    return []


TICKETS = load_tickets()
TICKET_MAP = {t["id"]: t for t in TICKETS}
TICKET_CHOICES = [
    f"{t['id']} - {t['customer']} ({t['text'][:40]}...)" for t in TICKETS
]


def on_ticket_select(selected_choice):
    if not selected_choice:
        return "", "", ""
    ticket_id = selected_choice.split(" - ")[0].strip()
    ticket_info = TICKET_MAP.get(ticket_id, {})
    customer = ticket_info.get("customer", "Unknown")
    text = ticket_info.get("text", "")
    return ticket_id, customer, text


def resolve_ticket(ticket_id):
    ticket_id = (ticket_id or "").strip()
    if not ticket_id:
        return (
            "⚠️ Please enter or select a valid Ticket ID.",
            "❌ Invalid Input",
            gr.update(visible=False),
            gr.update(visible=False),
            "",
        )

    try:
        validate_ticket_id(ticket_id)
    except ValueError as e:
        return (
            f"⚠️ Validation error: {e}",
            "❌ Invalid Ticket ID Format (must be like T-1001)",
            gr.update(visible=False),
            gr.update(visible=False),
            "",
        )

    try:
        result = run_agent(ticket_id)
        draft = str(result["messages"][-1].content)
    except Exception as e:
        return (
            f"❌ Execution failed: {str(e)}",
            "Error",
            gr.update(visible=False),
            gr.update(visible=False),
            "",
        )

    warnings = grounding_warnings(draft)
    warning_text = ""
    if warnings:
        warning_text = "### ⚠️ Guardrail Warnings\n" + "\n".join(
            f"- {w}" for w in warnings
        )
    else:
        warning_text = "✅ **All guardrail checks passed.** Response is grounded and cites evidence."

    is_sensitive = needs_human_approval(draft)

    if is_sensitive:
        status_md = (
            "### 🛡️ Status: **Human Approval Required**\n"
            "A sensitive action (e.g. refund, cancellation, or data modification) was detected in this response draft. "
            "Please review and submit an approval decision below."
        )
        return (
            draft,
            warning_text,
            gr.update(visible=True),
            gr.update(
                visible=True,
                value=f"Pending approval for ticket **{ticket_id}**.",
            ),
            status_md,
        )
    else:
        status_md = (
            "### 🟢 Status: **Ready for Review**\n"
            "No sensitive actions detected. The drafted response is safe for standard delivery."
        )
        return (
            draft,
            warning_text,
            gr.update(visible=False),
            gr.update(visible=False),
            status_md,
        )


def approve_action(ticket_id):
    return (
        f"✅ **Approved** — Action authorized for ticket `{ticket_id}`. Downstream resolution triggered."
    )


def reject_action(ticket_id):
    return (
        f"❌ **Rejected** — Action declined for ticket `{ticket_id}`. Ticket escalated to human supervisor for manual review."
    )


def create_demo():
    with gr.Blocks(title="TrustDesk - AI Support Agent", analytics_enabled=False) as demo:
        gr.Markdown(
            """
            # 🛡️ TrustDesk — AI Support Resolution Agent
            **Safe, Grounded Customer Support Resolution with Human-in-the-Loop Guardrails**
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 1. Select or Enter Ticket")
                ticket_dropdown = gr.Dropdown(
                    choices=TICKET_CHOICES,
                    label="Sample Tickets",
                    value=TICKET_CHOICES[0] if TICKET_CHOICES else None,
                )
                ticket_id_input = gr.Textbox(
                    label="Ticket ID",
                    value="T-1001",
                    placeholder="e.g. T-1001",
                )

                with gr.Group():
                    gr.Markdown("#### Ticket Metadata")
                    customer_display = gr.Textbox(
                        label="Customer",
                        value=TICKETS[0]["customer"] if TICKETS else "",
                        interactive=False,
                    )
                    issue_display = gr.Textbox(
                        label="Issue Description",
                        value=TICKETS[0]["text"] if TICKETS else "",
                        lines=3,
                        interactive=False,
                    )

                resolve_btn = gr.Button("🚀 Resolve Ticket", variant="primary")

            with gr.Column(scale=2):
                gr.Markdown("### 2. Resolution Draft & Safety Guardrails")
                status_display = gr.Markdown(
                    value="*Click 'Resolve Ticket' to run the TrustDesk agent.*"
                )
                draft_output = gr.Markdown(
                    label="Agent Draft Response",
                    value="*(Draft response will appear here)*",
                )
                guardrail_output = gr.Markdown(
                    label="Guardrail Analysis",
                    value="*(Safety checks will appear here)*",
                )

                with gr.Group(visible=False) as approval_group:
                    gr.Markdown("### 3. 👤 Human-in-the-Loop Decision")
                    decision_status = gr.Markdown(
                        value="*Pending reviewer action.*"
                    )
                    with gr.Row():
                        approve_btn = gr.Button(
                            "✓ Approve Action", variant="primary"
                        )
                        reject_btn = gr.Button(
                            "✕ Reject & Escalate", variant="stop"
                        )

        # Wire up event listeners
        ticket_dropdown.change(
            fn=on_ticket_select,
            inputs=[ticket_dropdown],
            outputs=[ticket_id_input, customer_display, issue_display],
        )

        resolve_btn.click(
            fn=resolve_ticket,
            inputs=[ticket_id_input],
            outputs=[
                draft_output,
                guardrail_output,
                approval_group,
                decision_status,
                status_display,
            ],
        )

        approve_btn.click(
            fn=approve_action,
            inputs=[ticket_id_input],
            outputs=[decision_status],
        )

        reject_btn.click(
            fn=reject_action,
            inputs=[ticket_id_input],
            outputs=[decision_status],
        )

    return demo


CUSTOM_CSS = """
.gradio-container { max-width: 950px !important; margin: auto; }
.status-box { padding: 12px; border-radius: 8px; margin-top: 8px; }
"""

if __name__ == "__main__":
    demo = create_demo()
    demo.launch(server_name="127.0.0.1", server_port=7860, css=CUSTOM_CSS)
