from agent import run_agent
from guardrails import validate_ticket_id, needs_human_approval, grounding_warnings


def main():
    print("=" * 50)
    print("  TrustDesk — AI Support Resolution Agent")
    print("=" * 50)

    ticket_id = input("\nTicket ID [T-1001]: ").strip() or "T-1001"
    validate_ticket_id(ticket_id)
    result = run_agent(ticket_id)
    draft = str(result["messages"][-1].content)

    print("\n--- TrustDesk Draft Response ---")
    print(draft)

    warnings = grounding_warnings(draft)
    if warnings:
        print("\n[TrustDesk] Guardrail warnings:")
        for item in warnings:
            print(f"  ⚠ {item}")

    if needs_human_approval(draft):
        decision = input("\n[TrustDesk] Sensitive action detected. Approve this draft? [y/N]: ").strip().lower()
        print("[TrustDesk] Approved ✓" if decision == "y" else "[TrustDesk] Not approved — escalated for review.")
    else:
        print("\n[TrustDesk] No sensitive action detected. Draft is ready for normal review.")


if __name__ == "__main__":
    main()
