---
layout: default
title: Custom Roles Guide
parent: Usage
nav_order: 4
permalink: /usage/roles/
---

# Custom Roles Guide

This guide explains how to use custom roles in nGPT, a powerful feature that allows you to create and manage specialized AI personas for different tasks.

> **Looking for ready-to-use roles?** Check out our [Role Gallery](/ngpt/examples/role-gallery/) with custom roles for various domains and use cases.
> 
> **Need task-specific tools?** Explore our [Specialized Tools](/ngpt/examples/specialized-tools/) collection for targeted assistance with specific tasks.

## What Are Custom Roles?

Custom roles allow you to create and use specialized AI personas for specific tasks. Unlike one-time system prompts (with `--preprompt`), roles are saved and can be reused across multiple sessions. This provides several benefits:

- **Consistency**: Get predictable behavior across different sessions
- **Efficiency**: Save time by not having to rewrite specialized prompts
- **Specialization**: Create focused experts for different domains
- **Sharing**: Save and share useful roles with others

## Managing Roles

nGPT provides a complete set of commands for managing your custom roles:

```bash
# Show role configuration help
ngpt --role-config help

# Create a new role
ngpt --role-config create json_generator

# List all available roles
ngpt --role-config list

# Show details of a specific role
ngpt --role-config show json_generator

# Edit an existing role
ngpt --role-config edit json_generator

# Remove a role
ngpt --role-config remove json_generator
```

When creating or editing a role, nGPT opens a multiline editor where you can enter or modify the system prompt for that role. This makes it easy to define complex instructions that guide the AI's behavior.

## Using Roles

Once you've created a role, you can use it with any mode by specifying the `--role` parameter:

```bash
# Use a role in standard chat mode
ngpt --role json_generator "Generate user data with name, email, and address"

# Use a role with code generation
ngpt --code --role python_expert "Create a function to parse JSON data"

# Use a role with shell command generation
ngpt --shell --role linux_expert "Find all large log files"

# Use a role in interactive mode
ngpt -i --role writing_assistant
```

The `--role` parameter is mutually exclusive with `--preprompt` since both set the system prompt.

## Role Storage

Roles are stored in JSON files in the following locations:
- Linux: `~/.config/ngpt/ngpt_roles/`
- macOS: `~/Library/Application Support/ngpt/ngpt_roles/`
- Windows: `%APPDATA%\ngpt\ngpt_roles\`

Each role is saved as a separate JSON file with the role name as the filename.

## Example Roles

Here are some useful role examples that you can create and use:

### JSON Generator Role

```
You are an expert JSON generator. Always respond with valid, well-formatted JSON based on the user's requirements. 
Never include explanations, markdown formatting, or comments in your response - only valid JSON.
Follow best practices for JSON structure and naming conventions.
```

Example usage:
```bash
# First create the role (one-time setup)
ngpt --role-config create json_generator

# Then use it whenever you need JSON data
ngpt --role json_generator "Generate a user profile with name, email, address, and preferences"
```

### Linux Expert Role

```
You are a Linux system administration expert. Always provide the most efficient and appropriate Linux commands to 
complete the task the user requests. Be concise and focus on commands rather than explanations.
Prefer modern tools and approaches. Always consider security implications of commands.
```

Example usage:
```bash
# Use with shell command generation mode for best results
ngpt --shell --role linux_expert "Set up a cronjob to clean temp files every day at midnight"
```

### Code Review Role

```
You are a senior code reviewer with expertise in multiple programming languages. When analyzing code:
1. Identify potential bugs, security vulnerabilities, and performance issues
2. Suggest improvements to code structure, readability, and maintainability
3. Check for adherence to standard coding conventions
4. Highlight any edge cases that might not be handled
Be specific in your feedback and provide concrete examples of improvements when possible.
```

Example usage:
```bash
# Review code from a file
cat mycode.py | ngpt --pipe --role code_reviewer "Review this code: {}"
```

### Technical Writer Role

```
You are an expert technical writer specializing in clear, concise documentation.
Follow these guidelines:
1. Use simple, direct language and avoid jargon unless necessary
2. Structure information logically with headings and lists
3. Include relevant examples to illustrate concepts
4. Focus on practical use cases rather than theory
5. Use consistent terminology throughout
Remember that good documentation anticipates user questions and provides answers proactively.
```

Example usage:
```bash
ngpt --role technical_writer "Write documentation for a REST API endpoint that creates new users"
```

### SQL Expert Role

```
You are an expert in SQL database queries and optimization. Provide efficient, well-structured SQL queries 
that follow best practices. Always consider:
1. Query performance and optimization
2. Proper indexing recommendations when relevant
3. Security concerns like SQL injection
4. Database compatibility issues between different SQL dialects when mentioned
When generating queries, use clear formatting with appropriate indentation and line breaks for readability.
```

Example usage:
```bash
ngpt --role sql_expert "Write a query to find customers who haven't made a purchase in the last 6 months"
```

### Data Analyst Role

```
You are a data analysis expert. When responding to questions:
1. Recommend appropriate statistical methods and data visualization techniques
2. Provide code examples in Python using libraries like pandas, numpy, matplotlib, or seaborn
3. Explain your analytical approach and reasoning
4. Always consider data quality, outliers, and appropriate statistical tests
5. Include interpretation of results in business or practical terms
Balance technical rigor with clear explanations.
```

Example usage:
```bash
ngpt --role data_analyst "How should I analyze customer churn data to identify key factors?"
```

### Bug Hunter Role

```
You are an expert in debugging software issues. Your approach should be:
1. First, ask clarifying questions to understand the exact symptoms and context
2. Suggest specific diagnostic steps and commands to gather more information
3. Provide possible causes based on the symptoms
4. Recommend solutions in order of likelihood
5. Explain why these problems might occur to help prevent future issues
Be methodical and consider both common and less obvious causes.
```

Example usage:
```bash
ngpt --role bug_hunter "My Python script crashes with 'IndexError: list index out of range' occasionally but not always"
```

### Git Workflow Expert Role

```
You are a Git version control expert. Provide clear, accurate Git commands and workflows with a focus on:
1. Best practices for collaboration and code management
2. Proper branching strategies
3. Efficient techniques for common version control scenarios
4. Recovery steps for Git mistakes or problems
Always include the exact Git commands needed, with explanations of what each command does and any cautions to be aware of.
```

Example usage:
```bash
ngpt --role git_expert "How do I fix a commit that I accidentally made to the main branch instead of a feature branch?"
```

### Meeting Facilitator Role

```
You are an expert meeting facilitator. Help create effective meeting agendas, discussion points, and follow-up items.
Focus on:
1. Clear meeting objectives and desired outcomes
2. Time-efficient agenda structures
3. Techniques for encouraging participation from all attendees
4. Methods to keep discussions on track
5. Action item formulation and assignment
Prioritize clarity, inclusivity, and purposeful use of meeting time.
```

Example usage:
```bash
ngpt --role meeting_facilitator "Create an agenda for a 30-minute weekly team stand-up for a software development team"
```

### API Documentation Generator

```
You are an API documentation specialist. When documenting APIs:
1. Use clear, consistent terminology
2. Include comprehensive endpoint details (URL, method, parameters, headers)
3. Provide request and response examples with proper formatting
4. Document error codes and their meanings
5. Include authentication requirements when applicable
6. Add helpful notes for common use cases or edge conditions
Format all code examples, URLs, and JSON properly.
```

Example usage:
```bash
ngpt --role api_doc_generator "Document a user registration endpoint that accepts email, password, and name"
```

Example output:
```markdown
## User Registration

Creates a new user account in the system.

**Endpoint:** `/api/v1/users/register`  
**Method:** POST  
**Content-Type:** application/json

### Request Parameters

| Parameter | Type   | Required | Description                           |
|-----------|--------|----------|---------------------------------------|
| email     | string | Yes      | User's email address (must be unique) |
| password  | string | Yes      | User's password (min 8 characters)    |
| name      | string | Yes      | User's full name                      |

### Example Request

```json
POST /api/v1/users/register HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secureP@ssw0rd",
  "name": "Jane Doe"
}
```

### Success Response

**Code:** 201 CREATED

```json
{
  "id": "usr_12345",
  "email": "user@example.com",
  "name": "Jane Doe",
  "created_at": "2023-06-15T14:22:30Z"
}
```

### Error Responses

**Code:** 400 BAD REQUEST - Invalid input
**Code:** 409 CONFLICT - Email already exists

### Notes

- Passwords must contain at least 8 characters, including a number and a special character
- Email verification will be sent automatically after successful registration
```

### Regex Expert

```
You are a regular expression expert. When asked to create regex patterns:
1. Provide the exact regex pattern that matches the requirements
2. Explain what the regex pattern does component by component
3. Include test cases that demonstrate the pattern working
4. Provide variations for different regex engines/languages if needed
5. Note any limitations or edge cases of the pattern
Use clear formatting and examples to illustrate proper usage.
```

Example usage:
```bash
ngpt --role regex_expert "Create a regex pattern to validate email addresses"
```

Example output:
```
Regex Pattern:
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$

Explanation:
- ^: Matches the start of the string
- [a-zA-Z0-9._%+-]+: Matches one or more letters, numbers, or the characters ._%+- for the username part
- @: Matches the @ symbol (literal character)
- [a-zA-Z0-9.-]+: Matches one or more letters, numbers, or the characters .- for the domain name
- \.: Matches a literal dot (escaped with backslash)
- [a-zA-Z]{2,}: Matches two or more letters for the top-level domain
- $: Matches the end of the string

Test Cases:
✓ valid@email.com
✓ user.name+tag@example.co.uk
✓ user-name@example.org
✓ 123.456@example.com
✗ invalid@email (missing TLD)
✗ @example.com (missing username)
✗ user@.com (missing domain name)
✗ user@example. (incomplete TLD)

Language Variations:
JavaScript: Use as is with RegExp object or literal notation
Python: Use raw string prefix: r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHP: Use as is with preg_match() and delimiters: '/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/'

Limitations:
This pattern follows general email format rules but doesn't validate all RFC 5322 compliant emails, which can be more complex. It won't validate some valid but uncommon email formats, such as emails with quotes or certain special characters.
```

### Study Plan Creator

```
You are an educational expert specializing in creating personalized study plans. When creating study plans:
1. Break down the subject into logical learning components
2. Order topics from foundational to advanced concepts
3. Suggest specific learning resources (books, courses, websites, videos)
4. Create a realistic timeline with daily/weekly goals
5. Include methods to test understanding and retention
6. Suggest practice exercises and projects where applicable
Balance ambition with realistic time constraints and include time for review and consolidation.
```

Example usage:
```bash
ngpt --role study_plan_creator "Create a 3-month study plan for learning Python from beginner to intermediate level"
```

### Interview Question Generator

```
You are an interview preparation expert specializing in technical interviews. Create high-quality interview questions that:
1. Test both theoretical knowledge and practical application
2. Cover a range of difficulty levels (easy, medium, hard)
3. Include clear, detailed solutions or answer guidelines
4. Relate to real-world scenarios where appropriate
5. Target specific skills, concepts, or technologies as requested
Design questions that assess not just memorization but problem-solving ability and conceptual understanding.
```

Example usage:
```bash
ngpt --role interview_question_generator "Generate 5 Python data structures interview questions with solutions"
```

### Storyteller

```
You are a creative storyteller with expertise in narrative crafting. When creating stories:
1. Develop vivid, memorable characters with clear motivations
2. Craft engaging plots with natural progression and satisfying arcs
3. Create immersive settings with sensory details
4. Use varied and appropriate dialogue that reveals character
5. Maintain consistent tone and style fitting the genre requested
Prioritize originality, emotional resonance, and narrative cohesion.
```

Example usage:
```bash
ngpt --role storyteller "Write a short science fiction story about a time traveler's first journey"
```

### Marketing Copywriter

```
You are an expert marketing copywriter. When creating marketing content:
1. Use compelling, benefits-focused language that resonates with the target audience
2. Create attention-grabbing headlines and hooks
3. Follow the AIDA principle (Attention, Interest, Desire, Action)
4. Incorporate persuasive calls-to-action
5. Maintain the brand voice and positioning
6. Keep language concise, clear, and jargon-free unless appropriate for the audience
Optimize for both emotional appeal and clarity of value proposition.
```

Example usage:
```bash
ngpt --role marketing_copywriter "Write email marketing copy for a new fitness app that helps busy professionals"
```

## Real-World Use Cases

Here are some practical examples of how custom roles can enhance your workflow:

### Development Workflow

Create specialized roles for different aspects of software development:

```bash
# Create a planning role
ngpt --role-config create requirements_analyzer
cat project_brief.txt | ngpt --pipe --role requirements_analyzer "Extract technical requirements from this brief: {}"

# Create a design role
ngpt --role-config create system_architect
ngpt --role system_architect "Design a microservice architecture for an e-commerce platform"

# Create a development role
ngpt --role-config create test_driven_developer
ngpt --role test_driven_developer "Create a user authentication service with tests"

# Create a documentation role
ngpt --role-config create code_documenter
cat my_module.py | ngpt --pipe --role code_documenter "Generate comprehensive documentation for this code: {}"
```

### Data Analysis Workflow

Create roles for different stages of data analysis:

```bash
# Data cleaning role
ngpt --role-config create data_cleaner
cat raw_data.csv | ngpt --pipe --role data_cleaner "What steps should I take to clean this dataset: {}"

# Exploratory analysis role
ngpt --role-config create data_explorer
ngpt --role data_explorer "What visualizations would help understand customer purchasing patterns?"

# Statistical analysis role
ngpt --role-config create statistician
cat analysis_results.txt | ngpt --pipe --role statistician "Interpret these statistical results: {}"

# Reporting role
ngpt --role-config create data_storyteller
ngpt --role data_storyteller "Create an executive summary of our findings on customer churn"
```

### Writing Workflow

Create roles for different types of writing and editing:

```bash
# First draft role
ngpt --role-config create rough_drafter
ngpt --role rough_drafter "Write a first draft of a blog post about cloud security"

# Editor role
cat draft.md | ngpt --pipe --role editor "Edit this draft for clarity and conciseness: {}"

# Fact checker role
cat article.md | ngpt --pipe --role fact_checker "Check this article for factual accuracy: {}"

# SEO optimizer role
cat blog_post.md | ngpt --pipe --role seo_optimizer "Suggest SEO improvements for this blog post: {}"
```

## Creating Effective Roles

When creating your own roles, consider the following tips:

1. **Be specific**: Clearly define the role's expertise and how it should respond
2. **Include constraints**: Specify any limitations or guidelines (e.g., "always write code with comments")
3. **Define format**: If you want responses in a particular format, spell it out explicitly
4. **Add context**: For technical roles, include relevant technologies or frameworks
5. **Set tone**: Specify the communication style (e.g., concise, detailed, casual, formal)

Example structure for a custom role:

```
You are an expert in [DOMAIN/SKILL].

When responding to questions, follow these guidelines:
1. [SPECIFIC INSTRUCTION 1]
2. [SPECIFIC INSTRUCTION 2]
3. [SPECIFIC INSTRUCTION 3]

Always include [REQUIRED ELEMENT] in your responses.
Never [PROHIBITED BEHAVIOR].

Style and tone should be [DESIRED COMMUNICATION STYLE].
```

## Combining Roles with Other Features

Roles can be combined with other nGPT features for enhanced functionality:

```bash
# Role with web search
ngpt --role technical_writer --web-search "Write documentation for JWT authentication"

# Role with pretty formatting
ngpt --role python_expert "Explain decorators in Python"

# Role with logging
ngpt --role data_analyst --log analysis.log "Analyze this customer retention data"

# Role with piped content
cat data.csv | ngpt --pipe --role data_analyst "Analyze this CSV data: {}"
```

## Switching Between Roles

You can easily switch between different roles to get varied perspectives on the same question:

```bash
# Get technical explanation
ngpt --role software_engineer "Explain how WebSockets work"

# Get simplified explanation
ngpt --role teacher "Explain how WebSockets work in simple terms"

# Get security perspective
ngpt --role security_expert "Explain security considerations for WebSockets"
```

This allows you to explore different aspects of the same topic based on the expertise of each role.

## Conclusion

Custom roles in nGPT provide a powerful way to create reusable, specialized AI personas that can enhance your productivity. By creating and using roles for different tasks, you can get more consistent, focused, and efficient responses.

For more useful roles, check out our [Role Gallery](/ngpt/examples/role-gallery/) with over 100 ready-to-use custom roles across various domains.

For more information on using nGPT's other features, check out:
- [CLI Usage Guide](cli_usage.md)
- [CLI Configuration Guide](cli_config.md)
- [Git Commit Message Generation](gitcommsg.md) 