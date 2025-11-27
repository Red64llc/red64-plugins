# From the OS Agent documentation: https://buildermethods.com/agent-os/workflow

The best way to develop complex features and products using AI coding agents is to adopt a spec-driven development process. Agent OS is designed to help you power your spec-driven development process with six development phases:

# Run Once
## Plan product
The plan-product command kicks off this essential first phase. It is typically run only once at the beginning a new project, or on the day you install Agent OS into an existing project.

The product planning phase is where you define the strategic product mission, its projected feature development roadmap, and its technology stack. This information is documented and used by your agents when planning specs and implementing features to ensure alignment with with the high-level goals of your product.

# Repeatable

## Feature development cycle
The next 5 phases happen on a repeated basis for each new feature (or initiative) you build in your product. You can use all of them or pick and choose based on your needs.

## 1 Shape spec
The shape-spec command helps you take a rough idea and shape it into well-scoped requirements. Use this when you need clarification before officially writing up a feature.

Already have clear requirements? Skip this phase and add them directly to your spec's requirements.md.

## 2 Write spec
The write-spec command transforms your requirements into a detailed specification document.

## 3 Create tasks
The create-tasks command breaks down your spec into an actionable task list, grouped, prioritized, and ready for implementation.

## 4 Implement tasks
The implement-tasks command provides simple, straightforward implementation with your main agent. Perfect for smaller features or when you want direct control.

## 5 Orchestrate tasks
The orchestrate-tasks command provides advanced orchestration for complex features. Delegate task groups to specialized Claude Code subagents or generate targeted prompts with fine-grain control over context and standards.

Choose implement-tasks OR orchestrate-tasks for a given spec—you wouldn't use both for the same feature.