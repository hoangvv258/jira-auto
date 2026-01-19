# jira-auto
You are a senior backend engineer and DevOps engineer.

Your task is to design and generate a professional CLI tool that creates Jira tickets using Jira REST API.

=== SECURITY REQUIREMENTS ===
- Use Jira Personal Access Token (PAT) for authentication.
- DO NOT hardcode any secrets in the source code.
- The Jira token must be read from environment variables.
- The user will manually create a `.env` file and execute:
  source .env
- Environment variables required:
  - JIRA_BASE_URL
  - JIRA_EMAIL
  - JIRA_API_TOKEN
  - JIRA_PROJECT_KEY

=== TOOL REQUIREMENTS ===
- Language: choose a common backend language (Node.js or Python).
- Provide clear instructions to run the tool.
- Validate required environment variables before execution.
- Fail gracefully with meaningful error messages.

=== AI-POWERED TICKET CONTENT ===
- Use AI to generate ticket content (summary, description, acceptance criteria).
- Input to AI:
  - Feature / bug description (free text from user)
  - Ticket type (Bug / Task / Story)
  - Priority
- Output from AI must be mapped into Jira fields.

=== JIRA TICKET TEMPLATE ===
Use the following default template structure:

Summary:
[Concise, action-oriented title]

Description:
1. Background
2. Problem / Requirement
3. Expected Behavior
4. Actual Behavior (if Bug)
5. Notes / Constraints

Acceptance Criteria:
- Given ...
- When ...
- Then ...

=== FUNCTIONAL REQUIREMENTS ===
- Allow user to run the tool with CLI arguments or prompts.
- Example:
  create-jira-ticket --type Bug --priority High --input "Login API returns 500 when token expires"
- Automatically fill Jira fields using AI-generated content.
- Print created ticket key and URL after success.

=== OUTPUT ===
- Generate:
  1. Source code
  2. Example `.env` file (with placeholder values)
  3. README-style usage instructions
  4. Example AI-generated ticket payload sent to Jira

Follow best practices for clean code, security, and maintainability.

## Usage

1. Install dependencies:
   ```
   npm install
   ```

2. Create a `.env` file based on `.env.example` and fill in your values:
   ```
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. Source the environment variables:
   ```
   source .env
   ```

4. Run the tool:
   ```
   node index.js --type Bug --priority High --input "Login API returns 500 when token expires"
   ```
   or
   ```
   ./index.js --type Task --priority Medium --input "Add user profile page"
   ```

   After running, the tool will generate AI-powered ticket content and create the Jira ticket, printing the ticket key and URL.

## Example AI-Generated Ticket Payload

For input: `--type Bug --priority High --input "Login API returns 500 when token expires"`

Generated Summary: "Fix 500 error in login API when token expires"

Generated Description:
```
1. Background
   The login API is critical for user authentication.

2. Problem / Requirement
   When a user's token expires, the API returns a 500 internal server error instead of a proper 401 unauthorized.

3. Expected Behavior
   The API should return 401 unauthorized with a clear message.

4. Actual Behavior
   Returns 500 error, causing confusion and poor user experience.

5. Notes / Constraints
   Ensure backward compatibility and proper error logging.

Acceptance Criteria:
- Given a user with an expired token
- When they attempt to login
- Then the API returns 401 with message "Token expired"
```

This content is then used to create the Jira ticket via REST API.