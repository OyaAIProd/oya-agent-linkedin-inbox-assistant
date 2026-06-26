import os, json
from datetime import datetime, timezone

try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    emails = inp.get("emails")
    if emails is None:
        raise ValueError("'emails' is required and must be a list of classified email objects.")
    if not isinstance(emails, list):
        raise ValueError("'emails' must be a list.")

    run_timestamp = inp.get("run_timestamp") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    total_count = len(emails)

    # ── Category colour palette ──────────────────────────────────────────────
    CATEGORY_COLORS = {
        "finance":      "#2563eb",
        "hr":           "#7c3aed",
        "sales":        "#059669",
        "marketing":    "#d97706",
        "legal":        "#dc2626",
        "engineering":  "#0891b2",
        "support":      "#db2777",
        "operations":   "#65a30d",
        "general":      "#6b7280",
    }
    DEFAULT_COLOR = "#6b7280"

    PRIORITY_BADGE = {
        "urgent": ("background:#ef4444;color:#fff;", "⚠️ URGENT"),
        "high":   ("background:#f97316;color:#fff;", "🔴 HIGH"),
        "medium": ("background:#eab308;color:#1a1a1a;", "🟡 MEDIUM"),
        "low":    ("background:#22c55e;color:#fff;", "🟢 LOW"),
    }

    def cat_color(category: str) -> str:
        return CATEGORY_COLORS.get(category.lower().strip(), DEFAULT_COLOR)

    def priority_badge_html(priority: str) -> str:
        p = priority.lower().strip()
        style, label = PRIORITY_BADGE.get(p, ("background:#6b7280;color:#fff;", priority.upper()))
        return (
            f'<span style="display:inline-block;padding:2px 10px;border-radius:12px;'
            f'font-size:11px;font-weight:700;letter-spacing:.5px;{style}">{label}</span>'
        )

    def email_card_html(em: dict) -> str:
        sender     = em.get("sender", "Unknown")
        subject    = em.get("subject", "(no subject)")
        summary    = em.get("summary", "")
        draft      = em.get("draft_reply", "")
        priority   = em.get("priority", "low")
        badge      = priority_badge_html(priority)
        draft_escaped = draft.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        return f"""
        <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;
                    margin:10px 0;padding:18px 20px;box-shadow:0 1px 4px rgba(0,0,0,.06);">
          <table style="width:100%;border-collapse:collapse;">
            <tr>
              <td style="vertical-align:top;padding-bottom:6px;">
                <span style="font-size:13px;color:#6b7280;font-weight:600;">FROM:&nbsp;</span>
                <span style="font-size:13px;color:#111827;">{sender}</span>
              </td>
              <td style="text-align:right;vertical-align:top;padding-bottom:6px;">{badge}</td>
            </tr>
          </table>
          <div style="font-size:15px;font-weight:700;color:#111827;margin-bottom:6px;">{subject}</div>
          <div style="font-size:13px;color:#374151;margin-bottom:12px;">{summary}</div>
          <blockquote style="margin:0;padding:12px 16px;background:#f3f4f6;border-left:4px solid #9ca3af;
                             border-radius:0 6px 6px 0;font-size:13px;color:#4b5563;line-height:1.6;">
            <strong style="color:#374151;display:block;margin-bottom:4px;">✏️ Draft Reply:</strong>
            {draft_escaped}
          </blockquote>
        </div>"""

    # ── Group emails ─────────────────────────────────────────────────────────
    urgent_emails = [e for e in emails if e.get("priority", "").lower().strip() == "urgent"]
    by_category: dict[str, list] = {}
    for em in emails:
        cat = em.get("category", "General").strip()
        by_category.setdefault(cat, []).append(em)

    # ── Build HTML sections ──────────────────────────────────────────────────
    urgent_section = ""
    if urgent_emails:
        cards = "".join(email_card_html(e) for e in urgent_emails)
        urgent_section = f"""
        <div style="background:#fef2f2;border:2px solid #ef4444;border-radius:12px;
                    padding:20px;margin-bottom:28px;">
          <div style="font-size:18px;font-weight:800;color:#b91c1c;margin-bottom:14px;">
            ⚠️ URGENT — Requires Immediate Attention ({len(urgent_emails)})
          </div>
          {cards}
        </div>"""

    category_sections = ""
    for cat, items in sorted(by_category.items()):
        color  = cat_color(cat)
        cards  = "".join(email_card_html(e) for e in items)
        category_sections += f"""
        <div style="margin-bottom:28px;">
          <div style="background:{color};color:#fff;padding:10px 18px;border-radius:8px 8px 0 0;
                      font-size:15px;font-weight:700;letter-spacing:.3px;">
            📁 {cat} &nbsp;·&nbsp; {len(items)} email{"s" if len(items) != 1 else ""}
          </div>
          <div style="background:#f9fafb;border:1px solid #e5e7eb;border-top:none;
                      border-radius:0 0 8px 8px;padding:14px 14px 4px 14px;">
            {cards}
          </div>
        </div>"""

    # ── Assemble full HTML ───────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="max-width:680px;margin:32px auto;background:#f1f5f9;">

    <!-- HEADER -->
    <div style="background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);
                border-radius:14px 14px 0 0;padding:28px 32px;">
      <div style="font-size:22px;font-weight:800;color:#ffffff;margin-bottom:6px;">
        📬 Email Digest
      </div>
      <div style="font-size:13px;color:#bfdbfe;">
        🕐 Generated: {run_timestamp}
        &nbsp;&nbsp;|&nbsp;&nbsp;
        📧 Total Emails: <strong style="color:#ffffff;">{total_count}</strong>
      </div>
    </div>

    <!-- BODY -->
    <div style="background:#f1f5f9;padding:24px 24px 12px 24px;">

      {urgent_section}
      {category_sections}

    </div>

    <!-- FOOTER -->
    <div style="background:#1e293b;border-radius:0 0 14px 14px;padding:18px 28px;text-align:center;">
      <p style="margin:0;font-size:12px;color:#94a3b8;line-height:1.7;">
        🔍 <strong style="color:#cbd5e1;">Review before sending.</strong>
        All replies above are <em>AI-generated drafts</em> and have not been sent.
        Please verify accuracy, tone, and completeness before using any draft.
      </p>
    </div>

  </div>
</body>
</html>"""

    print(json.dumps({"html_body": html, "total_emails": total_count, "urgent_count": len(urgent_emails), "categories": list(by_category.keys())}))

except Exception as e:
    print(json.dumps({"error": str(e)}))