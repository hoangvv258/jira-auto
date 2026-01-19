#!/usr/bin/env node

require('dotenv').config();

const { Command } = require('commander');
const axios = require('axios');
const OpenAI = require('openai');

const program = new Command();

program
  .name('create-jira-ticket')
  .description('CLI tool to create Jira tickets using AI-generated content')
  .version('1.0.0')
  .requiredOption('-t, --type <type>', 'Ticket type: Bug, Task, or Story')
  .requiredOption('-p, --priority <priority>', 'Priority: Lowest, Low, Medium, High, Highest')
  .requiredOption('-i, --input <input>', 'Feature/bug description')
  .action(async (options) => {
    try {
      // Validate environment variables
      const requiredEnvVars = ['JIRA_BASE_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN', 'JIRA_PROJECT_KEY', 'OPENAI_API_KEY'];
      for (const varName of requiredEnvVars) {
        if (!process.env[varName]) {
          throw new Error(`Environment variable ${varName} is required. Please set it in your .env file.`);
        }
      }

      const { type, priority, input } = options;

      // Validate type
      const validTypes = ['Bug', 'Task', 'Story'];
      if (!validTypes.includes(type)) {
        throw new Error(`Invalid type. Must be one of: ${validTypes.join(', ')}`);
      }

      // Validate priority
      const validPriorities = ['Lowest', 'Low', 'Medium', 'High', 'Highest'];
      if (!validPriorities.includes(priority)) {
        throw new Error(`Invalid priority. Must be one of: ${validPriorities.join(', ')}`);
      }

      console.log('Generating ticket content using AI...');

      // Generate content using OpenAI
      const openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY,
      });

      const prompt = `
Generate a Jira ticket based on the following:

Ticket Type: ${type}
Priority: ${priority}
Description: ${input}

Use the following template:

Summary: [Concise, action-oriented title]

Description:
1. Background
2. Problem / Requirement
3. Expected Behavior
${type === 'Bug' ? '4. Actual Behavior' : ''}
5. Notes / Constraints

Acceptance Criteria:
- Given ...
- When ...
- Then ...

Output the summary, description, and acceptance criteria in JSON format:
{
  "summary": "...",
  "description": "...",
  "acceptanceCriteria": "..."
}
`;

      const completion = await openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 1000,
      });

      const response = completion.choices[0].message.content.trim();
      let generated;
      try {
        generated = JSON.parse(response);
      } catch (e) {
        throw new Error('Failed to parse AI response. Please try again.');
      }

      const { summary, description, acceptanceCriteria } = generated;

      // Combine description and acceptance criteria
      const fullDescription = `${description}\n\nAcceptance Criteria:\n${acceptanceCriteria}`;

      // Create Jira ticket
      console.log('Creating Jira ticket...');

      const jiraUrl = `${process.env.JIRA_BASE_URL}/rest/api/3/issue`;
      const auth = Buffer.from(`${process.env.JIRA_EMAIL}:${process.env.JIRA_API_TOKEN}`).toString('base64');

      const payload = {
        fields: {
          project: {
            key: process.env.JIRA_PROJECT_KEY,
          },
          summary: summary,
          description: fullDescription,
          issuetype: {
            name: type,
          },
          priority: {
            name: priority,
          },
        },
      };

      const responseJira = await axios.post(jiraUrl, payload, {
        headers: {
          'Authorization': `Basic ${auth}`,
          'Content-Type': 'application/json',
        },
      });

      const ticketKey = responseJira.data.key;
      const ticketUrl = `${process.env.JIRA_BASE_URL}/browse/${ticketKey}`;

      console.log(`Ticket created successfully!`);
      console.log(`Key: ${ticketKey}`);
      console.log(`URL: ${ticketUrl}`);

    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

program.parse();