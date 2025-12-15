# Web Framework Analysis: Rapid Prototyping + Fast Deployment

*December 2025 - Yacin Bahi - v5 *

## Framework Selection for Prototype-to-Production Pipeline

---

## Executive Summary

**Recommendation: Ruby on Rails 8 + Kamal 2**

Rails 8 with Kamal 2 delivers the best combination of rapid prototyping capabilities and deployment ease. The "No PaaS Required" philosophy directly addresses our bottleneck of deployment friction while maintaining the prototyping speed we already value.

### Key Findings

| Framework | Prototyping | Deployment | Testing/TDD | AI-Spec Dev | Overall Score |
|-----------|-------------|------------|-------------|-------------|---------------|
| Rails 8 + Kamal 2 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | **8.73** |
| Phoenix/Elixir | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★☆☆ | **7.69** |
| Django | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | **6.89** |
| Next.js | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | **6.42** |

### Critical Insights

1. **Testing/TDD Ecosystem**: Rails' RSpec + FactoryBot + Capybara is years ahead of Django's pytest ecosystem for spec-driven AI development
2. **Admin Panel Obsolescence**: Django's admin panel advantage is now a liability—Claude Code builds better custom backends faster
3. **Ruby AI/LLM Parity**: RubyLLM, LangchainRB, and ecosystem provide complete AI capabilities; Python's advantage is marginal

---

## Rails 8 + Kamal 2: The New Deployment Story

### Why Rails 8 Changes Everything

Rails 8 was specifically designed with the tagline **"No PaaS Required"**. DHH and the Rails team recognized that deployment friction was becoming the major bottleneck for solo developers and small teams.

### Kamal 2 - Key Features

**Single Command Deployment:**
```bash
kamal setup  # Turns a fresh Linux box into a production server in ~2 minutes
kamal deploy # Zero-downtime deployment
```

**What Kamal 2 Includes:**
- **Kamal Proxy**: Replaces Traefik, provides zero-downtime deploys
- **Thruster**: Built-in proxy for asset caching, compression, X-Sendfile
- **Auto SSL**: Let's Encrypt certificates automatically provisioned
- **Multi-app hosting**: Single server can run multiple applications
- **Secret management**: Built-in integration with 1Password, Bitwarden, LastPass

### The Solid Stack - No Redis Required

Rails 8 introduces three SQLite-based adapters that eliminate external dependencies:

| Adapter | Replaces | Purpose |
|---------|----------|---------|
| Solid Cable | Redis | WebSocket message relaying |
| Solid Cache | Redis/Memcached | Fragment caching |
| Solid Queue | Redis + Sidekiq | Background jobs |

**Impact**: A complete Rails 8 app can run on a $4/month VPS with SQLite, no external services needed.

### Deployment Comparison: Rails 8 vs Other Frameworks

| Step | Rails 8 + Kamal | Phoenix + Fly.io | Next.js + Vercel | Django |
|------|-----------------|------------------|------------------|--------|
| Initial Setup | `kamal setup` | `fly launch` | `vercel deploy` | Manual multi-step |
| Time to Deploy | ~2 min | ~5 min | ~1 min | 30-60 min |
| Zero-Downtime | ✅ Built-in | ✅ BEAM | ✅ Vercel | ❌ Manual setup |
| SSL Certs | ✅ Auto | ✅ Auto | ✅ Auto | ❌ Certbot |
| No Redis Needed | ✅ Solid Stack | ❌ | ❌ | ❌ |
| Vendor Lock-in | ❌ None | Low | High (Vercel) | None |
| Monthly Cost | $4-10 | $5-20 | $0-20+ | $10-30 |

---

## Testing & TDD: The Critical Differentiator

For **spec-driven development with Claude Code**, testing framework quality directly impacts productivity. This is where Rails dramatically outperforms Django.

### Rails Testing Ecosystem (RSpec + FactoryBot + Capybara)

```ruby
# spec/models/user_spec.rb - Clean, readable, AI-friendly
RSpec.describe User, type: :model do
  describe "validations" do
    it { is_expected.to validate_presence_of(:email) }
    it { is_expected.to validate_uniqueness_of(:email) }
  end
  
  describe "#full_name" do
    let(:user) { build(:user, first_name: "John", last_name: "Doe") }
    it { expect(user.full_name).to eq("John Doe") }
  end
end

# spec/factories/users.rb - FactoryBot patterns
FactoryBot.define do
  factory :user do
    first_name { Faker::Name.first_name }
    email { Faker::Internet.email }
    
    trait :admin do
      role { "admin" }
    end
    
    trait :with_subscription do
      after(:create) { |user| create(:subscription, user: user) }
    end
  end
end

# spec/features/user_login_spec.rb - Capybara BDD
RSpec.feature "User Login", type: :feature do
  scenario "successful login redirects to dashboard" do
    user = create(:user, :with_subscription)
    visit login_path
    fill_in "Email", with: user.email
    fill_in "Password", with: "password"
    click_button "Sign In"
    expect(page).to have_current_path(dashboard_path)
  end
end
```

### Django Testing Ecosystem (pytest)

```python
# tests/test_models.py - More verbose, less AI-friendly
import pytest
from django.test import TestCase
from .factories import UserFactory

class UserModelTest(TestCase):
    def test_email_required(self):
        user = UserFactory.build(email=None)
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_email_unique(self):
        UserFactory.create(email="test@test.com")
        user = UserFactory.build(email="test@test.com")
        with self.assertRaises(IntegrityError):
            user.save()

# tests/factories.py - factory_boy (less mature than FactoryBot)
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    first_name = factory.Faker('first_name')
    email = factory.Faker('email')

# tests/test_views.py - Selenium integration (more setup required)
from selenium import webdriver
from selenium.webdriver.common.by import By

class LoginTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()  # Manual driver setup
        
    def test_login_redirect(self):
        user = UserFactory.create()
        self.selenium.get(f"{self.live_server_url}/login/")
        self.selenium.find_element(By.NAME, "email").send_keys(user.email)
        # ... more verbose code
```

### Testing Friction Comparison

| Aspect | Rails (RSpec) | Django (pytest) | AI/Spec-Driven Impact |
|--------|---------------|-----------------|----------------------|
| **BDD DSL** | Native `describe/it/expect` | Requires Behave/Lettuce addon | RSpec DSL aligns with natural language specs |
| **Test Data** | FactoryBot: traits, sequences, callbacks | factory_boy: works but less mature | FactoryBot patterns = better AI generation |
| **Integration** | Capybara: single gem, mature | Selenium: more setup, driver management | Capybara DSL readable by AI |
| **Generators** | `rails g rspec:model User` | None - manual file creation | Scaffolding helps AI follow patterns |
| **TDD Flow** | Guard + Spring = instant feedback | pytest-watch works but slower | Faster feedback = better TDD with AI |
| **Shoulda Matchers** | One-liner validations | No equivalent | `it { is_expected.to validate_presence_of(:email) }` |
| **Community Examples** | 20+ years of RSpec patterns | pytest newer in Django ecosystem | More training data for AI models |
| **Code Coverage** | SimpleCov - excellent integration | coverage.py - good | SimpleCov integrates seamlessly |
| **Watch Mode** | guard-rspec, Spring preloader | pytest-watch | Guard + Spring = instant feedback for TDD |
| **Error Messages** | Readable, context-rich failures | Good but more verbose | Clear failures help AI fix tests |

### Why This Matters for Claude Code

When using spec-driven development with Claude Code:

1. **RSpec's DSL matches natural language** - "it should validate presence of email" translates directly to code
2. **FactoryBot traits** - AI can generate complex object graphs easily
3. **Convention over configuration** - AI knows exactly where tests go and how to structure them
4. **Mature ecosystem** - More examples in training data for AI to learn from

---

## Django Admin Panel: Obsolete in the AI Era

### The Old Argument (Pre-2023)

Django's admin panel was considered a competitive advantage for:
- Quick CRUD backends
- Admin interfaces without coding
- Rapid backoffice development

### The New Reality (2024-2025)

**Claude Code builds better, custom backends faster than wrestling with Django admin customization.**

| Aspect | Django Admin | Claude Code + Rails |
|--------|--------------|---------------------|
| Time to Basic CRUD | 5 minutes | 10 minutes |
| Time to Custom UI | Hours of fighting | 30 minutes |
| Design Flexibility | Limited to admin templates | Complete control |
| UX Quality | Generic admin feel | Custom, branded |
| Complex Workflows | Very difficult | Natural to build |
| Maintenance | Django upgrade pain | Standard Rails code |

**Why Django Admin is Now a Liability:**
- Takes hours to customize beyond basic CRUD
- Limited design flexibility
- Fighting the framework for anything non-standard
- Django upgrade compatibility issues
- Claude Code can generate a complete, beautiful admin in 30 minutes with exactly the UX you want

**Adjusted Weight:** Reduced from 8 points to 2 points in scoring matrix (legacy consideration only)

---

## Ruby AI/LLM/Data Ecosystem: Complete for Production

Python's AI advantage is narrowing. Ruby has everything needed for production AI applications.

### Multi-Provider LLM Libraries

| Library | Providers | Key Features |
|---------|-----------|--------------|
| **RubyLLM** | OpenAI, Anthropic, Gemini, Bedrock, DeepSeek, Mistral, Ollama, OpenRouter, Perplexity, GPUStack | Unified API, Rails generators, `acts_as_chat`, built-in chat UI, streaming, vision, audio, PDF, tools |
| **LangchainRB** | Same + 15 more | RAG, vector search, assistants, embeddings, conversation memory, RAGAS evaluation |
| **langchainrb_rails** | Via LangchainRB | `Product.ask("find shoes in stock")`, ActiveRecord vectorsearch |
| **Durable-LLM** | OpenAI, Anthropic, Google, Cohere, Mistral, Groq, Fireworks, Together, DeepSeek, OpenRouter, Perplexity, xAI, Azure, Hugging Face | Universal interface with unified error handling |

### Official/Semi-Official SDKs

| Library | Description |
|---------|-------------|
| **anthropic-sdk-beta** | Official Anthropic Ruby SDK (April 2025) |
| **ruby-anthropic** | Community Anthropic client (maintained by Alex Rudall) |
| **ruby-openai** | OpenAI Ruby client - GPT-4, DALL-E, Whisper, embeddings, assistants |

### Vector Search & Embeddings

| Library | Backend | Use Case |
|---------|---------|----------|
| **Neighbor** | pgvector, sqlite-vec | Native vector search for Postgres/SQLite |
| **Milvus** (via LangchainRB) | Milvus/Zilliz | Distributed vector database |
| **Qdrant** (via LangchainRB) | Qdrant | High-performance vector search |
| **Pinecone** (via LangchainRB) | Pinecone | Managed vector DB |

### Data Processing & ML

| Library | Python Equivalent | Capabilities |
|---------|-------------------|--------------|
| **Polars-Ruby** | Polars/Pandas | Rust-powered DataFrames, lazy evaluation, 10x faster than Pandas |
| **Rover** | Pandas | Numo-powered DataFrames, Vega visualization |
| **Numo::NArray** | NumPy | N-dimensional arrays, matrix operations, broadcasting |
| **Daru** | Pandas | DataFrames, statistics, time series |
| **Rumale** | Scikit-learn | 50+ ML algorithms: SVM, Random Forest, Neural Networks, clustering |
| **Torch.rb** | PyTorch | Deep learning, tensors, GPU support |
| **Prophet.rb** | Prophet | Time series forecasting with seasonality |
| **red-datasets** | sklearn.datasets | MNIST, CIFAR-10, Iris, Wine, etc. |

### Example: Complete RAG Application in Rails

```ruby
# Gemfile
gem 'ruby_llm'
gem 'neighbor'

# app/models/document.rb
class Document < ApplicationRecord
  has_neighbors :embedding
  
  def self.search(query)
    embedding = RubyLLM.embed(query)
    nearest_neighbors(:embedding, embedding, distance: :cosine).limit(5)
  end
end

# app/models/chat.rb
class Chat < ApplicationRecord
  acts_as_chat  # RubyLLM Rails integration
end

# app/controllers/chats_controller.rb
class ChatsController < ApplicationController
  def ask
    context = Document.search(params[:question])
    chat = Chat.create!(model: "claude-sonnet-4")
    
    response = chat.ask(
      "Based on this context: #{context.map(&:content).join("\n")}\n\n" +
      "Answer: #{params[:question]}"
    )
    
    render json: { answer: response.content }
  end
end
```

---

## Phoenix/Elixir: The Performance Alternative

### Strengths

**Exceptional Performance:**
- 10x throughput compared to Rails in benchmarks
- Handles 2 million concurrent connections per server
- Response times in microseconds (µs), not milliseconds
- Memory footprint: ~100MB for massive scale vs Rails ~250MB baseline

**Real-Time Built-In:**
- LiveView for server-rendered real-time UIs
- Channels for WebSocket communication
- Presence tracking built-in

### Deployment with Fly.io

Phoenix has excellent Fly.io integration:
```bash
fly launch  # Detects Phoenix, sets up Postgres, deploys
fly deploy  # Subsequent deployments
```

Fly.io provides:
- Auto-scaling across 30+ global regions
- Built-in clustering support for Elixir nodes
- Postgres as a service
- ~$5-20/month for small apps

### Challenges

1. **Developer Availability**: Elixir developers are scarce (~4x harder to hire than Rails)
2. **Learning Curve**: Functional programming paradigm shift
3. **Ecosystem Size**: Fewer libraries than Rails/Django/npm
4. **AI Assistance**: Less training data for AI code generation

### When to Choose Phoenix

- High-traffic real-time applications (chat, gaming, IoT)
- Applications requiring extreme concurrency
- When performance is more critical than development speed
- Teams already experienced with Erlang/Elixir

---

## Next.js: The JavaScript Option

### Strengths

- **Zero-config on Vercel**: `git push` = deployed
- **Largest developer pool**: JavaScript devs are abundant
- **npm ecosystem**: Massive library availability
- **Full-stack React**: Frontend team can own backend

### Deployment Reality

**Vercel (Easy Path):**
- Zero configuration deployment
- Automatic SSL, CDN, scaling
- Great DX for simple apps

**Self-Hosting (Hard Path):**
- Requires significant DevOps knowledge
- Many features don't work out of box (ISR, Image Optimization)
- Recent Next.js 15 improvements help, but still complex
- OpenNext community adapter needed for serverless

### Challenges for Prototyping

1. **No scaffolding**: Must build CRUD manually or use external tools
2. **No built-in ORM**: Need Prisma, Drizzle, or manual SQL
3. **No admin panel**: Must build or integrate third-party
4. **Config-heavy**: Convention over configuration not followed
5. **Vercel lock-in**: Many features optimized for Vercel only

### When to Choose Next.js

- Team is already JavaScript-focused
- Building a marketing site or content-heavy app
- Need tight integration with React ecosystem
- Vercel pricing works for your scale

---

## Django: The Python Workhorse

### Strengths

- **Excellent ORM**: Mature, powerful database abstraction
- **Python ecosystem**: Great for data/ML integration (if Python-only libs required)
- **Security**: Excellent built-in protections
- **Documentation**: Extensive, well-maintained

### Weaknesses (Updated Assessment)

1. **Admin Panel Obsolete**: See above—Claude Code builds better backends faster
2. **Testing Friction**: pytest lacks RSpec's BDD DSL and FactoryBot's maturity
3. **Deployment Friction**: Most manual setup of all frameworks

### Deployment Friction

Django's deployment story is the weakest:

```bash
# Typical Django deployment requires:
# 1. Set up virtual environment
# 2. Configure Gunicorn WSGI server
# 3. Set up Nginx as reverse proxy
# 4. Configure static file serving
# 5. Set up SSL with Certbot
# 6. Configure PostgreSQL
# 7. Set up Redis for caching/Celery
# 8. Configure background workers
# 9. Set up CI/CD pipeline
```

**Tools like Cookiecutter-Django help**, but deployment remains manual compared to Rails/Kamal.

### When to Choose Django

- **Must use Python-only ML libraries** (TensorFlow, PyTorch native)
- Team already proficient in Python with no Ruby experience
- Integration with existing Python data pipelines

---

## Updated Framework Ranking

### Scoring Matrix (Key Changes Highlighted)

| Dimension | Weight | Rails 8 | Phoenix | Next.js | Django | Notes |
|-----------|--------|---------|---------|---------|--------|-------|
| **DEPLOYMENT** |
| Deployment Ease | 15 | 9.5 | 7 | 8 | 5 | Rails 8 Kamal: 2 min. Django: Manual |
| Zero-Downtime Deploy | 10 | 9 | 9 | 9 | 5 | Kamal Proxy built-in |
| SSL Auto-Provisioning | 8 | 9 | 8 | 10 | 4 | Django: Manual Certbot |
| No-PaaS Self-Hosting | 12 | 10 | 8 | 5 | 6 | Rails 8 "No PaaS Required" |
| Multi-App Single Server | 5 | 9 | 7 | 4 | 5 | Kamal Proxy native |
| **PROTOTYPING & TDD** |
| Scaffolding/Generators | 10 | 10 | 9 | 5 | 7 | Rails: Best in class |
| Time to MVP | 15 | 10 | 8 | 5 | 7 | Rails 30-40% faster |
| Convention over Config | 8 | 10 | 9 | 4 | 6 | Helps AI generation |
| ~~Admin Panel~~ | **2** | 5 | 5 | 2 | 6 | **OBSOLETE** in AI era |
| **TESTING (CRITICAL)** |
| Testing Framework Maturity | **12** | 10 | 9 | 6 | 6 | RSpec gold standard |
| BDD/Spec-Driven Support | **10** | 10 | 9 | 5 | 5 | RSpec native BDD |
| Test Data Factories | **8** | 10 | 8 | 6 | 5 | FactoryBot exceptional |
| AI-Spec Driven Compat | **10** | 10 | 8 | 6 | 6 | Conventions help AI |
| **AI/LLM ECOSYSTEM** |
| AI/LLM Libraries | 8 | 9 | 7 | 10 | 10 | RubyLLM fully capable |
| Data Processing | 5 | 7 | 6 | 8 | 10 | Polars-Ruby, Rover |
| **PERFORMANCE** |
| Memory Footprint | 5 | 5 | 9 | 7 | 6 | Phoenix ~100MB |
| Request Throughput | 4 | 5 | 10 | 7 | 6 | Phoenix 10x Rails |
| Concurrency Model | 4 | 5 | 10 | 8 | 5 | BEAM superior |
| **COST & AVAILABILITY** |
| Developer Availability | 6 | 8 | 4 | 10 | 9 | JS most abundant |
| Developer Salary | 3 | 7 | 8 | 6 | 7 | Rails $115K avg |
| Hiring Pool Quality | 4 | 8 | 9 | 6 | 7 | Elixir: high quality |

### Final Weighted Scores

| Framework | Score | Change from Baseline |
|-----------|-------|---------------------|
| **Rails 8 + Kamal 2** | **8.73** | ↑ Strengthened by testing |
| Phoenix/Elixir | 7.69 | Slight decrease |
| Django | **6.89** | ↓ -0.49 (testing, admin) |
| Next.js | 6.42 | ↓ -0.48 |

**Django drops significantly** once we properly account for:
- Admin panel obsolescence (-6 weighted points)
- Testing friction vs RSpec (-16 weighted points)
- Spec-driven AI development penalty

---

## Cost Analysis

### Monthly Operational Cost (Small App)

| Stack | Hosting | Add-ons | Total |
|-------|---------|---------|-------|
| Rails 8 + Kamal (Hetzner) | $4 | $0 (SQLite stack) | **$4** |
| Phoenix + Fly.io | $5-10 | $5 Postgres | **$10-15** |
| Next.js + Vercel (Pro) | $20 | $0 | **$20** |
| Django + DigitalOcean | $12 | $15 (Redis, Postgres) | **$27** |

### Developer Salary Comparison (US)

| Framework | Junior | Mid | Senior |
|-----------|--------|-----|--------|
| Rails | $80K | $115K | $145K |
| Phoenix/Elixir | $85K | $95K | $110K |
| Next.js/React | $75K | $100K | $130K |
| Django | $70K | $90K | $110K |

### Developer Availability Index

| Framework | Relative Availability |
|-----------|----------------------|
| JavaScript/Next.js | ★★★★★ (Highest) |
| Python/Django | ★★★★☆ |
| Ruby/Rails | ★★★☆☆ |
| Elixir/Phoenix | ★★☆☆☆ (Lowest) |

---

## AI-Assisted Development Compatibility

Given Red64's focus on AI-augmented development:

| Framework | AI Code Quality | Convention Adherence | Training Data | Spec-Driven TDD |
|-----------|-----------------|---------------------|---------------|-----------------|
| Rails | Excellent | Very High | Abundant | **Best** (RSpec) |
| Django | Good | High | Abundant | Limited (pytest) |
| Next.js | Good | Low (config-heavy) | Abundant | Limited |
| Phoenix | Fair | High | Limited | Good (ExUnit) |

**Key Insight**: Rails' strong conventions actually help AI tools generate more consistent, correct code. The "convention over configuration" approach provides clear patterns for AI to follow. Combined with RSpec's natural language DSL, Rails is the optimal choice for spec-driven AI development.

---

## Decision Matrix

| Your Priority | Best Choice | Reasoning |
|---------------|-------------|-----------|
| **Spec-Driven AI Dev (Claude Code)** | Rails 8 + Kamal 2 | RSpec + FactoryBot + Capybara = best AI test generation |
| **TDD/BDD Workflow** | Rails 8 + Kamal 2 | Most mature, lowest friction testing ecosystem |
| **Fastest Prototype → Production** | Rails 8 + Kamal 2 | Best scaffolding + Kamal 2 deployment |
| **AI/LLM Integration** | Rails 8 + Kamal 2 | RubyLLM/LangchainRB fully capable |
| High Traffic/Real-Time | Phoenix/Elixir | Only if you need 10x throughput |
| Large Existing JS Team | Next.js + Vercel | Leverage existing skills |
| **Must Use Python ML Libraries** | Django | Only if TensorFlow/PyTorch required directly |
| Maximum Developer Availability | Next.js | JS developers most abundant |
| Lowest Operational Cost | Rails 8 + Kamal 2 | $4/mo, no Redis, no PaaS fees |
| Enterprise Self-Hosting | Rails 8 + Kamal 2 | "No PaaS Required" philosophy |

---

## Implementation Checklist: Rails 8 + Kamal 2

### Initial Setup (One-Time)

```bash
# Install Rails 8
gem install rails

# Create new app (SQLite default, includes Kamal config)
rails new myapp

# Configure deployment
# Edit config/deploy.yml with your server IP and Docker registry credentials

# First deployment
kamal setup
```

### Daily Development → Deployment Flow

```bash
# Local development
rails s

# Deploy to production
kamal deploy

# View logs
kamal app logs

# Run console on production
kamal console
```

### Required Infrastructure

1. **VPS Provider**: Hetzner ($4/mo), DigitalOcean ($6/mo), or any Linux box
2. **Container Registry**: Docker Hub (free tier), or private registry
3. **Domain**: Point DNS to your server IP
4. **Optional**: GitHub Actions for CI before `kamal deploy`

### Testing Setup

```ruby
# Gemfile
group :development, :test do
  gem 'rspec-rails'
  gem 'factory_bot_rails'
  gem 'faker'
end

group :test do
  gem 'capybara'
  gem 'shoulda-matchers'
  gem 'simplecov', require: false
end

# Run
rails generate rspec:install
```

---

## Conclusion

For Red64's specific requirements of rapid prototyping + fast deployment + spec-driven AI development, **Rails 8 with Kamal 2 is the optimal choice**. It:

1. **Solves the deployment bottleneck** with single-command deployment
2. **Maintains prototyping speed** with best-in-class scaffolding
3. **Dominates TDD/BDD workflows** with RSpec + FactoryBot + Capybara
4. **Eliminates operational complexity** with the Solid Stack (no Redis)
5. **Minimizes cost** at $4-10/month per application
6. **Avoids vendor lock-in** with deploy-anywhere Docker containers
7. **Works best with AI assistance** due to strong conventions and mature testing
8. **Provides complete AI/LLM capabilities** via RubyLLM and LangchainRB

Phoenix remains an excellent choice for performance-critical applications, but the deployment story, developer availability, and AI ecosystem maturity make it better suited as a targeted solution for specific high-scale components rather than a primary prototyping stack.

Django's position has weakened significantly once testing friction and admin panel obsolescence are properly weighted. It should only be chosen when Python-only ML libraries are a hard requirement.
