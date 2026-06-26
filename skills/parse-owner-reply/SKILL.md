---
name: parse-owner-reply
display_name: "Parse Owner Reply"
description: "Parses a raw owner reply email into structured approval decisions (approve, edit, reject) for each pending conversation."
category: communication
icon: mail-check
skill_type: sandbox
catalog_type: addon
tool_schema:
  name: parse_owner_reply
  description: "Parse the owner's raw reply email text into structured approval decisions for pending conversations. Returns an array of decisions per conversation."
  parameters:
    type: object
    properties:
      reply_text:
        type: "string"
        description: "The full raw text of the owner's reply email containing approval instructions."
      pending_conversations:
        type: "array"
        description: "List of pending conversations to match against. Each item must have 'conversation_id' and 'sender_name'."
        items:
          type: object
          properties:
            conversation_id:
              type: "string"
              description: "Unique identifier for the conversation."
            sender_name:
              type: "string"
              description: "Name of the sender in the conversation."
            draft_reply:
              type: "string"
              description: "The current draft reply text for this conversation."
          required: [conversation_id, sender_name]
    required: [reply_text, pending_conversations]
---
# Parse Owner Reply

Parses a raw owner reply email into structured approval decisions for each pending conversation.

## Be Proactive
When an owner has replied to a digest or review email containing instructions like "send reply to John", "skip Sarah's", or "change the reply to X to say: ...", call this skill immediately to extract structured decisions before taking any send/edit/reject actions.