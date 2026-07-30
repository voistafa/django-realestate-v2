‏حالا فایل `architecture.md` را باز کن و متن زیر را داخلش قرار بده. این معماری بر پایه **Modular Monolith** است؛ یعنی پروژه یک Django واحد باقی می‌ماند، اما بخش‌ها مرزبندی حرفه‌ای و مستقل دارند.

````md
# System Architecture — Django Real Estate V2

## 1. Architecture Goals

The architecture of Django Real Estate V2 must support:

- Clear separation of responsibilities
- Long-term maintainability
- Easy feature development
- Professional deployment
- Automated testing
- Reusability for future clients
- A clean path toward V3

The project must avoid both:

- A single oversized Django app
- Unnecessary enterprise-level complexity

---

## 2. Architectural Style

V2 will use a modular monolith architecture.

This means:

- The project is deployed as one Django application
- The system uses one primary PostgreSQL database
- Each business area is separated into its own Django app
- Apps communicate through explicit model relationships and public interfaces
- The project does not use microservices

This architecture is appropriate because V2 is a professional agency website, not a large multi-company marketplace.

---

## 3. Application Type

V2 will be a server-rendered Django application.

The frontend will use:

- Django Templates
- Semantic HTML
- A CSS framework
- Custom CSS
- Minimal JavaScript where necessary

V2 will not use:

- React
- Vue
- A separate frontend application
- Django REST Framework
- A public API

An API may be introduced in V3 only when a real requirement exists.

---

## 4. Proposed Project Structure

```text
django-realestate-v2/
├── apps/
│   ├── __init__.py
│   ├── core/
│   ├── locations/
│   ├── properties/
│   ├── projects/
│   ├── agents/
│   └── inquiries/
│
├── config/
│   ├── __init__.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       └── production.py
│
├── templates/
│   ├── base.html
│   ├── includes/
│   ├── components/
│   └── errors/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/
├── docs/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
````

---

## 5. Django App Responsibilities

### core

The `core` app is responsible for website-wide functionality.

Responsibilities:

* Home page
* About page
* Global website content
* Shared context processors
* Website settings
* Shared abstract models when genuinely required

The `core` app must not become a container for unrelated business logic.

---

### locations

The `locations` app is responsible for geographical data.

Main entities:

* City
* Region

Responsibilities:

* Managing cities
* Managing regions
* Providing location choices to properties and projects
* Supporting property filtering by location

Location data must not be stored as repeated free-text values inside properties.

---

### properties

The `properties` app is responsible for real estate listings.

Main entities:

* Property
* PropertyImage
* PropertyType
* Feature

Responsibilities:

* Property creation and management
* Property listing
* Property detail pages
* Property search
* Property filtering
* Property sorting
* Property pagination
* Property image galleries
* Featured properties
* Property SEO data

This app owns all property-specific business rules.

---

### projects

The `projects` app is responsible for construction and development projects.

Main entities:

* DevelopmentProject
* ProjectImage
* ProjectFeature

Responsibilities:

* Project listing
* Project detail pages
* Project galleries
* Project location
* Project status
* Project marketing information

Projects must remain separate from normal property listings because they have different content, lifecycle, and marketing requirements.

---

### agents

The `agents` app is responsible for real estate agents.

Main entity:

* Agent

Responsibilities:

* Agent profiles
* Agent contact information
* Agent profile images
* Connecting agents to properties
* Connecting agents to projects
* Agent listing and detail pages

V2 agents are content entities managed by administrators.

They do not receive personal dashboards or authentication accounts in V2.

---

### inquiries

The `inquiries` app is responsible for customer leads and contact requests.

Main entity:

* Inquiry

Responsibilities:

* General contact inquiries
* Property-specific inquiries
* Project-specific inquiries
* Agent-specific inquiries
* Form validation
* Inquiry status management
* Admin review of customer requests

Inquiry data must not be mixed with property or agent models.

---

## 6. Settings Architecture

Django settings will be separated by environment.

### base.py

Contains settings shared by every environment:

* Installed apps
* Middleware
* Templates
* Authentication configuration
* Internationalization
* Shared static and media configuration

### local.py

Contains development settings:

* Debug mode
* Local database configuration
* Development email backend
* Developer-friendly configuration

### production.py

Contains production settings:

* Debug disabled
* Secure cookies
* Allowed hosts
* Production database configuration
* Production email configuration
* Security settings
* Production static and media storage

Secrets must be loaded from environment variables.

Secrets must never be committed to Git.

---

## 7. URL Architecture

Each Django app will own its URLs.

Example structure:

```text
/
├── properties/
├── properties/<slug>/
├── projects/
├── projects/<slug>/
├── agents/
├── agents/<slug>/
├── about/
└── contact/
```

The main `config/urls.py` file will only:

* Include app URL configurations
* Configure the Django admin
* Configure development media handling
* Register custom error handlers

Business URLs must not all be defined inside `config/urls.py`.

---

## 8. Template Architecture

The project will use a shared base template.

```text
templates/
├── base.html
├── includes/
│   ├── header.html
│   ├── footer.html
│   └── messages.html
├── components/
│   ├── property-card.html
│   ├── project-card.html
│   ├── agent-card.html
│   └── pagination.html
└── errors/
    ├── 404.html
    └── 500.html
```

Each app will also contain templates related to its own pages.

Reusable visual elements must be implemented as template components or includes instead of duplicated markup.

---

## 9. Static and Media Files

Static files include:

* CSS
* JavaScript
* Icons
* Brand assets
* Design images

Media files include administrator-uploaded content:

* Property images
* Project images
* Agent images

Static files and uploaded media must be treated separately.

Production media storage must be configurable and must not depend permanently on the application server filesystem.

---

## 10. Data and Business Logic Rules

The following rules apply throughout the project:

* Models define data structure and model-level rules
* Forms handle user input validation
* Views coordinate requests and responses
* Templates only present data
* Database queries must not be performed inside templates
* Views should remain small and readable
* Complex reusable business workflows may be moved into service modules
* Reusable query logic may be implemented with custom QuerySets or managers
* Service layers must not be created before real complexity exists
* Generic repositories will not be introduced without a concrete requirement

---

## 11. Database Principles

PostgreSQL will be the primary database.

Database design must follow these rules:

* Use proper foreign-key relationships
* Avoid duplicated location and category text
* Use database constraints where appropriate
* Add indexes only for real query requirements
* Use slugs for public detail-page URLs
* Preserve migration history
* Commit every migration to Git
* Test migrations locally before deployment

---

## 12. Model Relationship Overview

The expected high-level relationships are:

```text
City
└── Region

Property
├── PropertyType
├── Region
├── Agent
├── PropertyImage
└── Feature

DevelopmentProject
├── Region
├── Agent
├── ProjectImage
└── ProjectFeature

Inquiry
├── Property (optional)
├── DevelopmentProject (optional)
└── Agent (optional)
```

Detailed fields and constraints will be defined in the database design document before models are created.

---

## 13. Testing Architecture

Tests will be stored inside their relevant Django apps.

Critical areas include:

* Model constraints
* Property search
* Property filters
* Inquiry validation
* Detail-page availability
* Pagination
* Admin configuration
* Critical user journeys

Tests must focus on application behavior rather than implementation details.

---

## 14. Security Principles

The project must follow these security rules:

* No secrets in Git
* Debug mode disabled in production
* Environment-based configuration
* Server-side form validation
* CSRF protection
* Safe file-upload validation
* Secure production cookies
* Restricted admin access
* Correct allowed-host configuration
* No direct trust in user-submitted data

---

## 15. Performance Principles

Performance will be handled through deliberate query design.

The project will use when appropriate:

* `select_related`
* `prefetch_related`
* Pagination
* Optimized image sizes
* Database indexes
* Cached static assets

Caching infrastructure will not be introduced until a measured requirement exists.

---

## 16. Features Not Required in the Initial Architecture

The following technologies will not be introduced in V2 without a real need:

* Microservices
* Docker orchestration
* Celery
* Redis
* Elasticsearch
* WebSockets
* GraphQL
* Kubernetes
* Separate frontend deployment
* Generic repository patterns

Avoiding unnecessary infrastructure keeps the system easier to understand, test, deploy, and maintain.

---

## 17. Architectural Boundaries

Each app must:

* Own its business models
* Own its forms
* Own its views
* Own its URLs
* Own its app-specific templates
* Own its tests

Apps must not:

* Import unrelated implementation details from other apps
* Duplicate shared behavior
* Create circular dependencies
* Place unrelated code in generic `utils.py` files
* Depend on template logic for business rules

---

## 18. Deployment Direction

The production system will consist of:

* Django application
* Gunicorn
* PostgreSQL
* Production static-file handling
* External or persistent media storage
* Environment variables
* Automated deployment from GitHub

Deployment configuration will be implemented only after the application foundation is stable.

---

## 19. Architecture Decision Summary

V2 will use:

* Modular monolith architecture
* Server-rendered Django templates
* PostgreSQL
* Environment-specific settings
* Domain-focused Django apps
* App-owned URLs, templates, forms, and tests
* Thin views
* Explicit database relationships
* Progressive complexity only when justified

This architecture provides a professional foundation for V2 while preserving a clear path toward a reusable V3 product.
