# LinkedIn Messaging (Fixed)

Drop-in replacement for the system linkedin-messaging skill.
Reads inputs from `INPUT_JSON` env var (Oya sandbox convention) instead of stdin.

## Actions
- **list_chats** — List recent LinkedIn conversations
- **get_chat** — Get details of a specific conversation (requires `chat_id`)
- **read_messages** — Read messages from a conversation (requires `chat_id`, optional `limit`)
- **send_message** — Send a message in an existing conversation (requires `chat_id`, `text`)
- **start_chat** — Start a new conversation (requires `attendees_ids`, `text`)

## Credentials (auto-injected via LinkedIn gateway)
- `UNIPILE_DSN` — Unipile API base URL
- `UNIPILE_API_KEY` — Unipile API key
- `UNIPILE_ACCOUNT_ID` — Per-user LinkedIn account ID
