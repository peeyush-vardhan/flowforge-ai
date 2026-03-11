import type { NodeType, WorkflowPort } from "@flowforge/shared-types";

export type PrimitiveType = "string" | "number" | "boolean" | "object" | "array";

export interface FieldSchema {
  name: string;
  type: PrimitiveType;
  description?: string;
  required?: boolean;
  example?: unknown;
}

export interface IOSchema {
  description?: string;
  fields: FieldSchema[];
}

export interface RegistryNodeDefinition {
  /** Stable node identifier used in graphs (e.g. "llm_summarize"). */
  id: string;
  /** Human readable name for UIs. */
  display_name: string;
  /** High-level grouping (e.g. "triggers", "llm", "integrations", "control"). */
  category: string;
  /** Short description of what the node does. */
  description: string;
  /** Underlying workflow node type (used for validation & execution). */
  node_type: NodeType;
  /** Logical input ports exposed in the graph editor. */
  inputs?: WorkflowPort[];
  /** Logical output ports exposed in the graph editor. */
  outputs?: WorkflowPort[];
  /** Shape of the primary structured input payload (beyond ports). */
  input_schema?: IOSchema;
  /** Shape of the structured output payload. */
  output_schema?: IOSchema;
  /** Configuration fields editable at design time. */
  config_schema?: IOSchema;
  /** Natural-language examples that illustrate usage. */
  example_use_cases: string[];
  /** Explicit constraints (rate limits, auth requirements, etc.). */
  constraints?: string[];
  /** Hints to help the planner know when to choose this node. */
  prompt_hints_for_planner: string[];
}

export const NODE_REGISTRY: RegistryNodeDefinition[] = [
  {
    id: "manual_trigger",
    display_name: "Manual Trigger",
    category: "triggers",
    description: "Starts a workflow manually from the UI or an API call.",
    node_type: "input",
    outputs: [{ id: "event", label: "Trigger Event" }],
    output_schema: {
      description: "Metadata about the manual invocation.",
      fields: [
        {
          name: "initiator",
          type: "string",
          description: "User or system that started the run.",
          required: false
        },
        {
          name: "payload",
          type: "object",
          description: "Optional initial payload.",
          required: false
        }
      ]
    },
    example_use_cases: [
      "Run a workflow on demand from an internal tool.",
      "Test a workflow graph before connecting real triggers."
    ],
    constraints: ["Does not run automatically on external events."],
    prompt_hints_for_planner: [
      "Use manual_trigger when the user says they want to run the workflow manually or from the app.",
      "Prefer manual_trigger for prototypes or one-off jobs."
    ]
  },
  {
    id: "webhook_trigger",
    display_name: "Webhook Trigger",
    category: "triggers",
    description: "Starts a workflow when an HTTP webhook is received.",
    node_type: "input",
    outputs: [{ id: "event", label: "Webhook Event" }],
    output_schema: {
      description: "Raw webhook payload and headers.",
      fields: [
        {
          name: "body",
          type: "object",
          description: "Parsed JSON body of the webhook.",
          required: false
        },
        {
          name: "headers",
          type: "object",
          description: "HTTP headers associated with the request.",
          required: false
        },
        {
          name: "query",
          type: "object",
          description: "Query parameters sent with the request.",
          required: false
        }
      ]
    },
    config_schema: {
      description: "Webhook validation and routing settings.",
      fields: [
        {
          name: "secret",
          type: "string",
          description: "Optional secret used to validate incoming requests.",
          required: false
        },
        {
          name: "allowed_origins",
          type: "array",
          description: "List of allowed origins or hosts.",
          required: false
        }
      ]
    },
    example_use_cases: [
      "Trigger a workflow when a CRM sends a webhook.",
      "Receive events from a Stripe or Shopify webhook."
    ],
    constraints: [
      "Requires an externally accessible URL.",
      "Should validate signatures or secrets for security."
    ],
    prompt_hints_for_planner: [
      "Use webhook_trigger when the user mentions 'webhook', 'HTTP callback', or 'when an external system sends a POST'."
    ]
  },
  {
    id: "gmail_trigger_mock",
    display_name: "Gmail Trigger (Mock)",
    category: "triggers",
    description: "Simulates a Gmail new-email trigger for prototyping email workflows.",
    node_type: "input",
    outputs: [{ id: "email", label: "Email Event" }],
    output_schema: {
      description: "Simplified email event payload.",
      fields: [
        { name: "from", type: "string", description: "Sender email address." },
        { name: "to", type: "string", description: "Recipient email address." },
        { name: "subject", type: "string", description: "Email subject line." },
        { name: "body", type: "string", description: "Plaintext body." }
      ]
    },
    example_use_cases: [
      "Prototype an email triage workflow without connecting to real Gmail.",
      "Demo summarization or classification of incoming emails."
    ],
    constraints: [
      "Mock only; does not connect to a real Gmail account.",
      "Suitable for demos, tests, and offline examples."
    ],
    prompt_hints_for_planner: [
      "Use gmail_trigger_mock when the user describes workflows starting from 'an incoming email' but no real Gmail integration is required.",
      "Prefer gmail_trigger_mock for examples, evals, or offline simulations."
    ]
  },
  {
    id: "llm_summarize",
    display_name: "LLM Summarize",
    category: "llm",
    description: "Summarizes long text into a concise summary using an LLM.",
    node_type: "llm",
    inputs: [{ id: "text", label: "Text" }],
    outputs: [{ id: "summary", label: "Summary" }],
    input_schema: {
      description: "Text content to be summarized.",
      fields: [
        {
          name: "text",
          type: "string",
          description: "The raw text or email body to summarize.",
          required: true
        }
      ]
    },
    output_schema: {
      description: "Summary generated by the LLM.",
      fields: [
        {
          name: "summary",
          type: "string",
          description: "Short summary of the input text.",
          required: true
        }
      ]
    },
    config_schema: {
      description: "Summarization controls.",
      fields: [
        {
          name: "style",
          type: "string",
          description: "Tone or style of the summary (e.g. 'bullet points').",
          required: false
        },
        {
          name: "max_tokens",
          type: "number",
          description: "Approximate maximum length of the summary.",
          required: false
        }
      ]
    },
    example_use_cases: [
      "Summarize customer support tickets before routing.",
      "Generate short summaries of long status reports."
    ],
    constraints: ["Input text length is limited by the underlying LLM context window."],
    prompt_hints_for_planner: [
      "Use llm_summarize when the user asks to 'summarize', 'condense', 'TL;DR', or 'shorten' text.",
      "Combine with triggers like gmail_trigger_mock or webhook_trigger when summarizing incoming content."
    ]
  },
  {
    id: "llm_classify",
    display_name: "LLM Classify",
    category: "llm",
    description: "Classifies text into one of several categories using an LLM.",
    node_type: "llm",
    inputs: [{ id: "text", label: "Text" }],
    outputs: [{ id: "label", label: "Label" }],
    input_schema: {
      description: "Text and optional label schema.",
      fields: [
        {
          name: "text",
          type: "string",
          description: "Content to classify.",
          required: true
        }
      ]
    },
    output_schema: {
      description: "Chosen label and optional confidence.",
      fields: [
        {
          name: "label",
          type: "string",
          description: "Predicted category label.",
          required: true
        },
        {
          name: "confidence",
          type: "number",
          description: "Model's confidence (0-1) if available.",
          required: false
        }
      ]
    },
    config_schema: {
      description: "Classification label set.",
      fields: [
        {
          name: "labels",
          type: "array",
          description: "List of allowed labels or classes.",
          required: true
        },
        {
          name: "allow_other",
          type: "boolean",
          description: "Whether the model may respond with 'other' or 'unknown'.",
          required: false
        }
      ]
    },
    example_use_cases: [
      "Route incoming requests to 'sales', 'support', or 'billing'.",
      "Classify feedback as positive, negative, or neutral."
    ],
    constraints: ["Labels should be short, clear, and mutually exclusive where possible."],
    prompt_hints_for_planner: [
      "Use llm_classify when the user wants to bucket or route items into discrete categories.",
      "Look for words like 'classify', 'label', 'categorize', or 'route based on type'."
    ]
  },
  {
    id: "llm_extract_fields",
    display_name: "LLM Extract Fields",
    category: "llm",
    description: "Extracts structured fields from unstructured text using an LLM.",
    node_type: "llm",
    inputs: [{ id: "text", label: "Text" }],
    outputs: [{ id: "fields", label: "Extracted Fields" }],
    input_schema: {
      description: "Input text to parse.",
      fields: [
        {
          name: "text",
          type: "string",
          description: "Raw document, form, or email body.",
          required: true
        }
      ]
    },
    output_schema: {
      description: "Dictionary of extracted fields.",
      fields: [
        {
          name: "fields",
          type: "object",
          description: "Key-value pairs for extracted entities.",
          required: true
        }
      ]
    },
    config_schema: {
      description: "Field extraction schema.",
      fields: [
        {
          name: "schema",
          type: "object",
          description: "Description of fields to extract (names and types).",
          required: true
        }
      ]
    },
    example_use_cases: [
      "Extract customer name, company, and intent from an email.",
      "Parse order numbers and totals from invoices."
    ],
    constraints: ["Extraction quality depends on how clearly the schema is described."],
    prompt_hints_for_planner: [
      "Use llm_extract_fields when the user wants 'structured data' or 'fields' from free text.",
      "Look for instructions like 'pull out', 'extract', or 'parse into JSON'."
    ]
  },
  {
    id: "slack_send",
    display_name: "Slack Send Message",
    category: "integrations",
    description: "Sends a message to a Slack channel or user.",
    node_type: "tool",
    inputs: [{ id: "message", label: "Message" }],
    outputs: [{ id: "response", label: "Response" }],
    input_schema: {
      description: "Message content and target.",
      fields: [
        {
          name: "text",
          type: "string",
          description: "Message text to send.",
          required: true
        }
      ]
    },
    output_schema: {
      description: "Slack API response payload.",
      fields: [
        {
          name: "ok",
          type: "boolean",
          description: "Whether the message was accepted.",
          required: false
        }
      ]
    },
    config_schema: {
      description: "Slack channel configuration.",
      fields: [
        {
          name: "channel",
          type: "string",
          description: "Channel ID or @user to send to.",
          required: true
        }
      ]
    },
    example_use_cases: [
      "Post a summary of new support tickets to #support.",
      "Send approval requests to a manager in Slack."
    ],
    constraints: ["Requires Slack authentication and appropriate channel permissions."],
    prompt_hints_for_planner: [
      "Use slack_send when the user wants to notify a Slack channel or user.",
      "Look for phrases like 'send a Slack message', 'post to Slack', or 'notify in Slack'."
    ]
  },
  {
    id: "notion_create_page",
    display_name: "Notion Create Page",
    category: "integrations",
    description: "Creates a new Notion page in a specified database.",
    node_type: "tool",
    inputs: [{ id: "content", label: "Content" }],
    outputs: [{ id: "page", label: "Page" }],
    input_schema: {
      description: "Page title and content blocks.",
      fields: [
        {
          name: "title",
          type: "string",
          description: "Title of the new page.",
          required: true
        },
        {
          name: "properties",
          type: "object",
          description: "Database properties for the page.",
          required: false
        }
      ]
    },
    output_schema: {
      description: "Notion page metadata.",
      fields: [
        {
          name: "id",
          type: "string",
          description: "Notion page ID.",
          required: false
        }
      ]
    },
    config_schema: {
      description: "Notion database configuration.",
      fields: [
        {
          name: "database_id",
          type: "string",
          description: "Target Notion database ID.",
          required: true
        }
      ]
    },
    example_use_cases: [
      "Log summarized meeting notes into a Notion database.",
      "Create a page for each new deal or opportunity."
    ],
    constraints: ["Requires Notion integration and access to the target database."],
    prompt_hints_for_planner: [
      "Use notion_create_page when the user wants to store results or notes in Notion.",
      "Look for phrases like 'log into Notion', 'create a Notion page', or 'save in Notion database'."
    ]
  },
  {
    id: "http_request",
    display_name: "HTTP Request",
    category: "integrations",
    description: "Performs an HTTP request to an external API.",
    node_type: "tool",
    inputs: [{ id: "payload", label: "Payload" }],
    outputs: [{ id: "response", label: "Response" }],
    input_schema: {
      description: "Optional request body.",
      fields: [
        {
          name: "body",
          type: "object",
          description: "JSON body to send with the request.",
          required: false
        }
      ]
    },
    output_schema: {
      description: "HTTP response payload.",
      fields: [
        {
          name: "status",
          type: "number",
          description: "HTTP status code.",
          required: true
        },
        {
          name: "body",
          type: "object",
          description: "Parsed response body if JSON.",
          required: false
        }
      ]
    },
    config_schema: {
      description: "HTTP method and target URL.",
      fields: [
        {
          name: "method",
          type: "string",
          description: "HTTP method such as GET or POST.",
          required: true,
          example: "POST"
        },
        {
          name: "url",
          type: "string",
          description: "Absolute or templated URL.",
          required: true,
          example: "https://api.example.com/resource"
        },
        {
          name: "headers",
          type: "object",
          description: "Optional HTTP headers.",
          required: false
        }
      ]
    },
    example_use_cases: [
      "Call an internal microservice with data extracted by the LLM.",
      "Send data to a third-party webhook or REST API."
    ],
    constraints: ["May require authentication headers or API keys stored in config."],
    prompt_hints_for_planner: [
      "Use http_request when the user wants to 'call an API', 'send a POST request', or 'hit an endpoint'.",
      "Prefer http_request for generic HTTP integrations that are not covered by a more specific node."
    ]
  },
  {
    id: "branch_condition",
    display_name: "Branch Condition",
    category: "control",
    description: "Routes execution down different paths based on a boolean condition.",
    node_type: "branch",
    inputs: [{ id: "input", label: "Input" }],
    outputs: [
      { id: "true", label: "True" },
      { id: "false", label: "False" }
    ],
    input_schema: {
      description: "Payload to evaluate and forward.",
      fields: [
        {
          name: "condition",
          type: "boolean",
          description: "Boolean value used to choose the branch.",
          required: true
        }
      ]
    },
    example_use_cases: [
      "Route urgent tickets to a priority queue.",
      "Send high-value leads to an account executive while others go to SDRs."
    ],
    constraints: ["Expects a pre-computed boolean; complex logic should be done upstream."],
    prompt_hints_for_planner: [
      "Use branch_condition when the user describes 'if/else' logic or different flows based on a condition.",
      "Combine with llm_classify or llm_extract_fields when the condition depends on model output."
    ]
  },
  {
    id: "wait_delay",
    display_name: "Wait / Delay",
    category: "control",
    description: "Pauses execution for a specified duration before continuing.",
    node_type: "tool",
    inputs: [{ id: "input", label: "Input" }],
    outputs: [{ id: "output", label: "Output" }],
    config_schema: {
      description: "Delay configuration.",
      fields: [
        {
          name: "duration_seconds",
          type: "number",
          description: "Number of seconds to wait before resuming.",
          required: true
        }
      ]
    },
    example_use_cases: [
      "Wait 1 hour before sending a follow-up email.",
      "Introduce a small delay to respect external API rate limits."
    ],
    constraints: ["Long waits may be limited by the underlying scheduler implementation."],
    prompt_hints_for_planner: [
      "Use wait_delay when the user says 'wait', 'pause', 'delay', or 'after X minutes/hours'."
    ]
  },
  {
    id: "human_approval",
    display_name: "Human Approval",
    category: "control",
    description: "Pauses execution until a human approves or rejects a decision.",
    node_type: "tool",
    inputs: [{ id: "request", label: "Approval Request" }],
    outputs: [
      { id: "approved", label: "Approved" },
      { id: "rejected", label: "Rejected" }
    ],
    input_schema: {
      description: "Context sent to the approver.",
      fields: [
        {
          name: "summary",
          type: "string",
          description: "Short description of what is being approved.",
          required: true
        },
        {
          name: "details",
          type: "object",
          description: "Additional structured context.",
          required: false
        }
      ]
    },
    example_use_cases: [
      "Require manager approval before sending a large discount offer.",
      "Have a human check a generated email before sending to a VIP customer."
    ],
    constraints: [
      "Workflow remains pending until a human responds.",
      "Requires a UI or notification channel to collect approvals."
    ],
    prompt_hints_for_planner: [
      "Use human_approval when the user wants 'a human in the loop', 'manual review', or 'manager approval'.",
      "Prefer human_approval for high-risk actions like financial changes or external communications."
    ]
  }
];

export function list_nodes(): RegistryNodeDefinition[] {
  return NODE_REGISTRY;
}

export function get_node(id: string): RegistryNodeDefinition | undefined {
  return NODE_REGISTRY.find((node) => node.id === id);
}

export function search_nodes(query: string): RegistryNodeDefinition[] {
  const q = query.trim().toLowerCase();
  if (!q) return NODE_REGISTRY;

  return NODE_REGISTRY.filter((node) => {
    const haystacks: string[] = [
      node.id,
      node.display_name,
      node.category,
      node.description,
      node.example_use_cases.join(" "),
      node.prompt_hints_for_planner.join(" ")
    ];
    return haystacks.some((h) => h.toLowerCase().includes(q));
  });
}

export interface PlannerNodeContext {
  id: string;
  display_name: string;
  category: string;
  description: string;
  example_use_cases: string[];
  prompt_hints_for_planner: string[];
}

export interface PlannerContext {
  nodes: PlannerNodeContext[];
}

export function get_planner_context(): PlannerContext {
  return {
    nodes: NODE_REGISTRY.map(
      ({ id, display_name, category, description, example_use_cases, prompt_hints_for_planner }) => ({
        id,
        display_name,
        category,
        description,
        example_use_cases,
        prompt_hints_for_planner
      })
    )
  };
}

export function rank_relevant_nodes(
  user_prompt: string,
  limit: number = 5
): RegistryNodeDefinition[] {
  const q = user_prompt.trim().toLowerCase();
  if (!q) return NODE_REGISTRY.slice(0, limit);

  const scored = NODE_REGISTRY.map((node) => {
    const textChunks = {
      id: node.id.toLowerCase(),
      name: node.display_name.toLowerCase(),
      category: node.category.toLowerCase(),
      description: node.description.toLowerCase(),
      examples: node.example_use_cases.join(" ").toLowerCase(),
      hints: node.prompt_hints_for_planner.join(" ").toLowerCase()
    };

    let score = 0;
    if (textChunks.id.includes(q)) score += 4;
    if (textChunks.name.includes(q)) score += 4;
    if (textChunks.category.includes(q)) score += 2;
    if (textChunks.description.includes(q)) score += 3;
    if (textChunks.examples.includes(q)) score += 2;
    if (textChunks.hints.includes(q)) score += 2;

    return { node, score };
  });

  return scored
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ node }) => node);
}

