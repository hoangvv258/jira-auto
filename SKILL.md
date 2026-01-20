---
name: create-jira-ticket
description: Create Jira tickets via REST API with AI-generated content. Use when the user wants to create a Jira issue (Story or Bug) based on conversation context. The skill prompts for project selection, generates summary/description from context, and handles project-specific payload structures.
---

# Create Jira Ticket

Create Jira tickets programmatically with Bearer authentication and dynamic project-based payloads.

## Workflow

1. **Validate Inputs**: Ensure Project Key, Issue Type, and Content are clear.
2. **Clarify (if needed)**: If inputs are missing/ambiguous, ask the user a numbered list of questions.
3. **Generate Content**: Create summary and description using templates.
4. **Execute**: Run `scripts/create_jira_ticket.py`.

## Clarification Policy

**IF** user input is unclear, incomplete, or ambiguous, you **MUST** pause and ask a numbered list of clarifying questions. Do NOT guess.

**Required Inputs:**
- **Project Key**: ACPF, DPR, DMCD.
- **Issue Type**: Story, Bug, Request.
- **Description Details**: Sufficient context to fill the [template](references/content_templates.md).

**Example Clarification:**
> I can help with that. To create the ticket, I need to clarify:
> 1. Should this go to the **ACPF** or **DPR** or **DMCD** project?
> 2. Is this a **Story** or **Bug** or **Request**?
> 3. What are the specific acceptance criteria?

## Quick Start
> [!IMPORTANT] 
> **ALWAYS** use the correct template for the `description` field as defined below. Do not make up your own format.

```bash
# Create ACTUAL ticket using the Required Template
python3 scripts/create_jira_ticket.py \
    --project-key ACPF \
    --issue-type Story \
    --summary "[RECO][Algo] Implement user profile screen" \
    --description "h3. Background\nRequirement to allow profile editing.\n\nh3. Current State (Before Change)\nNo edit screen.\n\nh3. Proposed State (After Change)\nUser can edit name/bio.\n\nh3. Implementation Details\nNew API endpoint.\n\nh3. DoD\n* Tests passed." \
    --custom-fields '{"device_type": "iOS"}'
```

## Configuration

Set environment variables before running:

```bash
export JIRA_BASE_URL="https://yourcompany.atlassian.net"
export JIRA_PAT="your-personal-access-token"
```

## Project Schemas

The script uses dynamic payload structures based on project key:

| Project | Required Fields | Description |
|---------|----------------|-------------|
| ACPF | algo_id, model_type | Algo project |
| DPR | dataset_id, data_sensitivity | Data project |
| DMCD | device_os, test_device (opt) | Mobile project |

## AI Content Generation

When triggered, generate ticket content from conversation.

**Summary**: You **MUST** start with the prefix `[RECO][Algo]`. Follow with a concise title (max 100 chars).
Example: `[RECO][Algo] Implement dark mode`

**Description**: Use the standard templates defined in [content_templates.md](references/content_templates.md).

### Standard Template

```text
h3. Background
[High-level context. Why is this task necessary? What is the business or technical value?]

h3. Current State (Before Change)
[Describe the existing behavior, logical flow, or issue.]

h3. Proposed State (After Change)
[Describe exactly what needs to be different. Include detailed flow or requirements.]

h3. Implementation Details
[List specific components, configurations, or systems involved.]

h3. DoD
[Checklist to ensure the task is fully completed and verified.]
```

Example prompt to user:
> I'll create a Jira ticket based on our discussion.
> - **Project**: Which project? (ACPF/DPR/DMCD)
> - **Type**: Story or Bug or Request?
