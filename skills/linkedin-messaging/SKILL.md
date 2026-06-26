---
name: linkedin-messaging
display_name: "LinkedIn Messaging"
description: "Send and receive LinkedIn messages, manage conversations, and prospect via LinkedIn DMs"
category: messaging
icon: message-circle
skill_type: sandbox
catalog_type: platform
requirements: "httpx>=0.25"
resource_requirements:
  - env_var: UNIPILE_DSN
    name: "Unipile API Base URL"
    description: "Unipile REST API endpoint (auto-provided)"
  - env_var: UNIPILE_API_KEY
    name: "Unipile API Key"
    description: "Unipile API authentication key (auto-provided)"
  - env_var: UNIPILE_ACCOUNT_ID
    name: "Unipile Account ID"
    description: "Per-user Unipile account ID (auto-provided by gateway connection)"
tool_schema:
  name: linkedin_messaging
  description: "Send and receive LinkedIn messages, manage conversations, and start new DMs"
  parameters:
    type: object
    properties:
      action:
        type: "string"
        description: "Which operation to perform"
        enum: ['list_chats', 'read_messages', 'send_message', 'start_chat', 'get_chat']
      chat_id:
        type: "string"
        description: "Chat/conversation ID for read_messages, send_message, get_chat"
        default: ""
      text:
        type: "string"
        description: "Message text for send_message and start_chat"
        default: ""
      attendees_ids:
        type: "string"
        description: "Comma-separated LinkedIn user IDs for start_chat"
        default: ""
      limit:
        type: "integer"
        description: "Max results for list_chats and read_messages (default 20)"
        default: 20
    required: [action]
---
# LinkedIn Messaging

Send and receive LinkedIn messages via the Unipile messaging API. Requires LinkedIn to be connected in Apps first.

## Conversations
- **list_chats** -- List recent LinkedIn conversations.
- **get_chat** -- Get details of a specific conversation. Provide `chat_id`.

## Messages
- **read_messages** -- Read messages from a conversation. Provide `chat_id` and optional `limit`.
- **send_message** -- Send a LinkedIn message in an existing conversation. Provide `chat_id` and `text`.

## Outreach
- **start_chat** -- Start a new LinkedIn conversation. Provide `attendees_ids` (LinkedIn user ID) and `text`. Requires an existing connection or InMail credits.

## Notes
- LinkedIn messaging uses the same Unipile account as LinkedIn posting (no separate auth needed)
- InMail for non-connections requires a Premium/Sales Navigator account
