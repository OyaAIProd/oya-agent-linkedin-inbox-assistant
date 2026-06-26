import os, json, re

try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))

    reply_text = inp.get("reply_text", "").strip()
    if not reply_text:
        raise ValueError("'reply_text' is required and must not be empty.")

    pending = inp.get("pending_conversations", [])
    if not isinstance(pending, list) or len(pending) == 0:
        raise ValueError("'pending_conversations' must be a non-empty array.")

    for i, conv in enumerate(pending):
        if not conv.get("conversation_id") or not conv.get("sender_name"):
            raise ValueError(f"Each conversation must have 'conversation_id' and 'sender_name'. Item {i} is invalid.")

    def normalize(text):
        return text.lower().strip()

    # Build lookup maps
    by_id = {normalize(c["conversation_id"]): c for c in pending}
    by_name = {normalize(c["sender_name"]): c for c in pending}

    def find_conversation(token):
        t = normalize(token)
        if t in by_id:
            return by_id[t]
        if t in by_name:
            return by_name[t]
        # Partial name match
        for name_key, conv in by_name.items():
            if t in name_key or name_key in t:
                return conv
        for id_key, conv in by_id.items():
            if t in id_key or id_key in t:
                return conv
        return None

    decisions = {}  # conversation_id -> decision dict

    lines = reply_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        low = line.lower()

        # --- EDIT patterns ---
        # "change the reply to <X> to say: ..." or "change <X>'s reply to say: ..."
        edit_match = re.match(
            r"change(?:\s+the)?\s+(?:reply\s+to\s+|)(.+?)(?:'s\s+reply)?\s+to\s+say[:\s]+(.+)",
            low, re.IGNORECASE
        )
        if not edit_match:
            # "edit <X>: ..." or "edit reply to <X>: ..."
            edit_match = re.match(
                r"edit(?:\s+(?:the\s+)?reply(?:\s+(?:to|for))?\s+)?(.+?)[:\-]\s*(.+)",
                low, re.IGNORECASE
            )
        if not edit_match:
            # "update <X> to say: ..."
            edit_match = re.match(
                r"update(?:\s+(?:the\s+)?reply(?:\s+(?:to|for))?\s+)?(.+?)\s+to\s+say[:\s]+(.+)",
                low, re.IGNORECASE
            )

        if edit_match:
            token = edit_match.group(1).strip().strip("'\"")
            new_text_inline = edit_match.group(2).strip()
            conv = find_conversation(token)
            if conv:
                # Collect multi-line edit text
                collected = [new_text_inline]
                j = i + 1
                while j < len(lines):
                    next_low = lines[j].strip().lower()
                    # Stop if next line looks like a new instruction
                    if re.match(r"(approve|send|reject|skip|change|edit|update|deny)\b", next_low):
                        break
                    if lines[j].strip():
                        collected.append(lines[j].strip())
                    j += 1
                final_text = " ".join(collected).strip()
                cid = conv["conversation_id"]
                decisions[cid] = {
                    "conversation_id": cid,
                    "decision": "edit",
                    "final_reply_text": final_text
                }
                i = j
                continue

        # --- APPROVE patterns ---
        # "approve <X>", "send reply to <X>", "send <X>'s reply", "ok <X>", "yes to <X>", "go ahead with <X>"
        approve_match = re.match(
            r"(?:approve|send(?:\s+(?:the\s+)?reply(?:\s+to)?)?|ok|okay|yes(?:\s+to)?|go\s+ahead(?:\s+with)?|confirm)\s+(.+)",
            low, re.IGNORECASE
        )
        if approve_match:
            token = approve_match.group(1).strip().strip("'\".,")
            # Remove trailing noise
            token = re.sub(r"\s*(reply|'s reply|message)$", "", token, flags=re.IGNORECASE).strip()
            conv = find_conversation(token)
            if conv:
                cid = conv["conversation_id"]
                decisions[cid] = {
                    "conversation_id": cid,
                    "decision": "approve",
                    "final_reply_text": conv.get("draft_reply", "")
                }
                i += 1
                continue

        # --- REJECT patterns ---
        # "reject <X>", "skip <X>", "don't send to <X>", "do not reply to <X>", "ignore <X>", "deny <X>"
        reject_match = re.match(
            r"(?:reject|skip|ignore|deny|don'?t\s+(?:send|reply)(?:\s+to)?|do\s+not\s+(?:send|reply)(?:\s+to)?|hold|cancel)\s+(.+)",
            low, re.IGNORECASE
        )
        if reject_match:
            token = reject_match.group(1).strip().strip("'\".,")
            token = re.sub(r"\s*(reply|'s reply|message|one|the one from)$", "", token, flags=re.IGNORECASE).strip()
            # Handle "the one from <X>"
            from_match = re.search(r"(?:the\s+one\s+)?from\s+(.+)", token, re.IGNORECASE)
            if from_match:
                token = from_match.group(1).strip()
            conv = find_conversation(token)
            if conv:
                cid = conv["conversation_id"]
                decisions[cid] = {
                    "conversation_id": cid,
                    "decision": "reject",
                    "final_reply_text": ""
                }
                i += 1
                continue

        # --- Inline shorthand: "<X>: approve/reject/edit ..." ---
        inline_match = re.match(r"(.+?)[:\-]\s*(approve|reject|skip|send|edit|change)\b(.*)", low, re.IGNORECASE)
        if inline_match:
            token = inline_match.group(1).strip().strip("'\"")
            action = inline_match.group(2).strip().lower()
            extra = inline_match.group(3).strip()
            conv = find_conversation(token)
            if conv:
                cid = conv["conversation_id"]
                if action in ("approve", "send"):
                    decisions[cid] = {
                        "conversation_id": cid,
                        "decision": "approve",
                        "final_reply_text": conv.get("draft_reply", "")
                    }
                elif action in ("reject", "skip"):
                    decisions[cid] = {
                        "conversation_id": cid,
                        "decision": "reject",
                        "final_reply_text": ""
                    }
                elif action in ("edit", "change"):
                    # Extra may contain new text after "say:" or just inline
                    say_match = re.search(r"(?:to\s+say|say)[:\s]+(.+)", extra, re.IGNORECASE)
                    new_text = say_match.group(1).strip() if say_match else extra.strip()
                    if not new_text:
                        new_text = conv.get("draft_reply", "")
                    decisions[cid] = {
                        "conversation_id": cid,
                        "decision": "edit",
                        "final_reply_text": new_text
                    }
                i += 1
                continue

        i += 1

    # Build final result — include all pending conversations, unmatched ones marked as no_decision
    results = []
    for conv in pending:
        cid = conv["conversation_id"]
        if cid in decisions:
            results.append(decisions[cid])
        else:
            results.append({
                "conversation_id": cid,
                "decision": "no_decision",
                "final_reply_text": conv.get("draft_reply", "")
            })

    print(json.dumps({
        "decisions": results,
        "total": len(results),
        "approved": sum(1 for d in results if d["decision"] == "approve"),
        "edited": sum(1 for d in results if d["decision"] == "edit"),
        "rejected": sum(1 for d in results if d["decision"] == "reject"),
        "no_decision": sum(1 for d in results if d["decision"] == "no_decision")
    }))

except Exception as e:
    print(json.dumps({"error": str(e)}))