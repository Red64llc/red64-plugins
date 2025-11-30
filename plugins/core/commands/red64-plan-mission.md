# Plan Product Mission

Create the product mission document with a pre-filled template.

## What This Command Does

This command creates the `.red64/product/mission.md` file with a comprehensive template for defining your product's core identity, target users, differentiators, and success metrics.

## Execution Steps

### Step 1: Check for Existing Mission Document

First, check if `.red64/product/mission.md` already exists in the current working directory.

```bash
test -f .red64/product/mission.md && echo "exists" || echo "missing"
```

### Step 2: Handle Based on Existence

**If mission.md already exists:**

Output the following message and stop:

```
Skipped: .red64/product/mission.md already exists. No changes made.

Your product mission is already defined. Edit the file directly to make changes.
```

**If mission.md does NOT exist:**

Continue to Step 3.

### Step 3: Create Product Directory

Ensure the product directory exists:

```bash
mkdir -p .red64/product
```

### Step 4: Create Mission Document

Create `.red64/product/mission.md` with the following template content:

```markdown
# Product Mission

<!-- This document defines your product's core identity and direction. Edit each section to reflect your specific product. -->

## Pitch

<!-- Write a 1-2 sentence description of what your product does and who it's for. Include a memorable tagline. -->

**[Your Product Name]** is a [type of product] that helps [target users] [achieve specific outcome] by providing [key differentiating capability].

**Tagline:** "[Your memorable tagline here]"

## Vision Statement

<!-- Describe the future state your product enables. What change do you want to create in your users' world? 2-3 paragraphs. -->

[Your Product Name] transforms how [target users] approach [problem domain]. By [key approach], we enable [desired outcome] without sacrificing [important constraint users care about].

The future of [industry/domain] is [trend or shift]. [Your Product Name] bridges the gap between [current state] and [desired future state].

## The Problem

### [Problem Category or Theme]

<!-- Describe the core problem your product solves. Be specific about pain points and their impact. -->

[Target users] struggle with [specific problem]. The current approaches of [existing solutions] result in [negative outcomes]. For [user segment] where [important constraint] is critical, this [limitation] is a fundamental barrier to [desired outcome].

**Quantifiable Impact:**
- [Measurable pain point 1, e.g., "Teams spend 30-40% of time on X"]
- [Measurable pain point 2, e.g., "Y occurs N times per week"]
- [Measurable pain point 3, e.g., "Z costs $X annually"]
- [Measurable pain point 4, e.g., "No way to measure ROI on current solutions"]

**Our Solution:** [One sentence describing how your product addresses these problems].

## Users

### Primary Customers

<!-- List 2-4 customer segments your product serves. -->

- **[Customer Segment 1]:** [Brief description of who they are and what they need]
- **[Customer Segment 2]:** [Brief description of who they are and what they need]
- **[Customer Segment 3]:** [Brief description of who they are and what they need]

### User Personas

<!-- Create 2-3 detailed personas representing your key users. -->

**[Persona Name], [Role Title]** ([Age Range])
- **Role:** [Specific job function and context]
- **Context:** [Situation that leads them to your product]
- **Pain Points:** [2-3 specific frustrations they experience]
- **Goals:** [2-3 outcomes they want to achieve]

**[Persona Name], [Role Title]** ([Age Range])
- **Role:** [Specific job function and context]
- **Context:** [Situation that leads them to your product]
- **Pain Points:** [2-3 specific frustrations they experience]
- **Goals:** [2-3 outcomes they want to achieve]

## Differentiators

<!-- Describe 3-5 key ways your product stands out from alternatives. Use the format "Feature (vs. Alternative Approach)" -->

### [Differentiator 1] (vs. [Alternative Approach])

[2-3 sentences explaining what you do differently and why it matters to users. Include quantifiable benefit if possible.]

### [Differentiator 2] (vs. [Alternative Approach])

[2-3 sentences explaining what you do differently and why it matters to users. Include quantifiable benefit if possible.]

### [Differentiator 3] (vs. [Alternative Approach])

[2-3 sentences explaining what you do differently and why it matters to users. Include quantifiable benefit if possible.]

## Key Features

<!-- List your product's main features grouped by category. -->

### [Feature Category 1]
- **[Feature Name]:** [Brief description of what it does and the benefit]
- **[Feature Name]:** [Brief description of what it does and the benefit]
- **[Feature Name]:** [Brief description of what it does and the benefit]

### [Feature Category 2]
- **[Feature Name]:** [Brief description of what it does and the benefit]
- **[Feature Name]:** [Brief description of what it does and the benefit]
- **[Feature Name]:** [Brief description of what it does and the benefit]

### [Feature Category 3]
- **[Feature Name]:** [Brief description of what it does and the benefit]
- **[Feature Name]:** [Brief description of what it does and the benefit]

## Success Metrics

<!-- Define measurable targets for technical, adoption, and business success. -->

### Technical Metrics
| Metric | Target |
|--------|--------|
| [Technical metric 1, e.g., "Response time"] | [Target value, e.g., "< 200ms"] |
| [Technical metric 2, e.g., "Uptime"] | [Target value, e.g., "99.9%"] |
| [Technical metric 3, e.g., "Error rate"] | [Target value, e.g., "< 0.1%"] |

### Adoption Metrics
| Metric | Target (6 months) |
|--------|-------------------|
| [Adoption metric 1, e.g., "Active users"] | [Target, e.g., "1000+"] |
| [Adoption metric 2, e.g., "Daily active users"] | [Target, e.g., "200+"] |
| [Adoption metric 3, e.g., "User retention rate"] | [Target, e.g., "80%+"] |

### Business Metrics
| Metric | Target |
|--------|--------|
| [Business metric 1, e.g., "Time saved per user"] | [Target, e.g., "2+ hours/week"] |
| [Business metric 2, e.g., "Customer satisfaction"] | [Target, e.g., "NPS 50+"] |
| [Business metric 3, e.g., "Conversion rate"] | [Target, e.g., "15%+"] |
```

### Step 5: Output Success Message

Output the following success message:

```
Success: Created .red64/product/mission.md

Your product mission template is ready. Edit the file to define:
  - Product pitch and vision
  - The problem you're solving
  - Target users and personas
  - Key differentiators
  - Features and success metrics

File location: .red64/product/mission.md
```

## Notes

- This command is idempotent: running it multiple times will not overwrite existing content
- The template uses HTML comments to guide users on what to edit in each section
- All placeholder content uses brackets [like this] to indicate fields requiring user input
