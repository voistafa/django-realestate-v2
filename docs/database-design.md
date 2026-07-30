# Database Design — Django Real Estate V2

## 1. Database Goals

The database must support:

- Professional property listings
- Sale and rental properties
- Construction projects
- Multiple property images
- Real estate agents
- Geographical filtering
- Customer inquiries
- SEO-friendly URLs
- Future customization for different clients

PostgreSQL will be the primary database.

---

## 2. General Database Rules

The following rules apply to all database models:

- All primary keys use Django `BigAutoField`
- Money values must never use `FloatField`
- Public pages use unique slugs
- Repeated information must not be stored as free text
- Important relationships use foreign keys
- Uploaded images are stored in separate image models
- Every main content model has creation and update timestamps
- Database deletion behavior must be explicitly defined
- Core searchable data must not be stored inside `JSONField`
- Soft deletion will not be used in V2
- Archived content will be controlled through status fields

---

## 3. Shared Abstract Models

These models will exist only in Python and will not create database tables.

### TimeStampedModel

Fields:

- `created_at`
- `updated_at`

Purpose:

Provides creation and modification timestamps to other models.

### SEOModel

Fields:

- `seo_title`
- `seo_description`

Purpose:

Allows important public pages to have custom SEO metadata.

These abstract models will only be introduced when the real Django models are created.

---

# 4. Core Domain

## SiteSettings

Stores company-wide website information.

This model is intended to contain only one record.

Fields:

- `company_name`
- `logo`
- `phone`
- `email`
- `whatsapp_number`
- `address`
- `instagram_url`
- `about_summary`
- `default_seo_title`
- `default_seo_description`
- `updated_at`

Rules:

- Only one active `SiteSettings` record may exist
- Sensitive settings and passwords must not be stored here
- Deployment secrets remain in environment variables

---

# 5. Locations Domain

## City

Represents a city.

Fields:

- `name`
- `slug`
- `is_active`
- `created_at`
- `updated_at`

Constraints:

- `name` must be unique
- `slug` must be unique

Example:

```text
City: Tehran
```

---

## Region

Represents a district, neighborhood, or region inside a city.

Fields:

- `city`
- `name`
- `slug`
- `is_active`
- `created_at`
- `updated_at`

Relationships:

- Each region belongs to one city
- One city can contain many regions

Constraints:

- A region name must be unique inside its city
- A region slug must be unique inside its city

Deletion rule:

- A city cannot be deleted while it has regions

Example:

```text
City: Tehran
Region: Saadat Abad
```

---

# 6. Agents Domain

## Agent

Represents a real estate agent displayed on the website.

Fields:

- `first_name`
- `last_name`
- `slug`
- `job_title`
- `bio`
- `phone`
- `email`
- `whatsapp_number`
- `photo`
- `is_active`
- `sort_order`
- `seo_title`
- `seo_description`
- `created_at`
- `updated_at`

Constraints:

- `slug` must be unique
- `sort_order` cannot be negative

Rules:

- An agent is managed through Django Admin
- An agent does not have a login account in V2
- Inactive agents are not displayed publicly

---

# 7. Properties Domain

## PropertyType

Represents the type of a property.

Examples:

- Apartment
- Villa
- Land
- Office
- Commercial Property

Fields:

- `name`
- `slug`
- `is_active`
- `sort_order`
- `created_at`
- `updated_at`

Constraints:

- `name` must be unique
- `slug` must be unique

Deletion rule:

- A property type cannot be deleted while properties use it

---

## Feature

Represents a reusable property feature.

Examples:

- Elevator
- Balcony
- Swimming Pool
- Storage Room
- Security System

Fields:

- `name`
- `slug`
- `icon`
- `is_active`
- `sort_order`

Constraints:

- `name` must be unique
- `slug` must be unique

Relationship:

- One property can have many features
- One feature can belong to many properties

---

## Property

Represents a real estate listing.

### Identity fields

- `title`
- `slug`
- `listing_code`

Rules:

- `slug` must be unique
- `listing_code` must be unique
- `listing_code` is a human-readable property reference

Example:

```text
PROP-1001
```

### Classification fields

- `property_type`
- `transaction_type`
- `publication_status`
- `availability_status`

`transaction_type` choices:

- `sale`
- `rent`

`publication_status` choices:

- `draft`
- `published`
- `archived`

`availability_status` choices:

- `available`
- `sold`
- `rented`
- `reserved`

Publication and availability are separate because a property may be published but already sold.

### Location fields

- `region`
- `address`
- `latitude`
- `longitude`
- `show_exact_location`

Rules:

- City is obtained through `region.city`
- City must not be duplicated directly inside Property
- Latitude and longitude are optional
- Exact location can be hidden from visitors

### Pricing fields

- `currency_code`
- `sale_price`
- `deposit_amount`
- `monthly_rent`

Money fields will use:

```python
DecimalField(max_digits=20, decimal_places=0)
```

Rules:

- `currency_code` must use predefined choices and must not accept arbitrary free-text values
- Sale properties require `sale_price`
- Rental properties require `monthly_rent`
- Rental deposit may be optional
- Float values must never be used for prices
- Price formatting belongs to the presentation layer

### Property specification fields

- `area`
- `land_area`
- `bedrooms`
- `bathrooms`
- `parking_spaces`
- `floor_number`
- `total_floors`
- `year_built`

Rules:

- `area` is required
- `land_area` is optional
- Numeric values cannot be negative
- Optional fields remain nullable instead of using misleading zero values

### Content fields

- `short_description`
- `description`
- `features`
- `agent`
- `is_featured`
- `published_at`
- `seo_title`
- `seo_description`
- `created_at`
- `updated_at`

Relationships:

- Each property belongs to one property type
- Each property belongs to one region
- Each property may have one agent
- Each property can have many features
- Each property can have many images

Deletion rules:

- Property type uses `PROTECT`
- Region uses `PROTECT`
- Agent uses `SET_NULL`
- Property images use `CASCADE`

---

## PropertyImage

Stores images belonging to a property.

Fields:

- `property`
- `image`
- `alt_text`
- `sort_order`
- `is_cover`
- `created_at`

Relationships:

- Each image belongs to one property
- One property can have many images

Constraints:

- `sort_order` cannot be negative
- Each property can have only one cover image

Deletion rule:

- Deleting a property deletes its related image records

Rules:

- Image validation will check file type
- Image validation will check maximum file size
- Images will be optimized for web display
- `alt_text` supports accessibility and SEO

---

# 8. Projects Domain

## ProjectFeature

Represents a reusable construction-project feature.

Examples:

- Smart Building
- Gym
- Rooftop Garden
- Conference Hall
- Private Parking

Fields:

- `name`
- `slug`
- `icon`
- `is_active`
- `sort_order`

Constraints:

- `name` must be unique
- `slug` must be unique

---

## DevelopmentProject

Represents a construction or development project.

### Identity fields

- `title`
- `slug`
- `project_code`

Constraints:

- `slug` must be unique
- `project_code` must be unique

### Status fields

- `publication_status`
- `project_status`

`publication_status` choices:

- `draft`
- `published`
- `archived`

`project_status` choices:

- `planned`
- `under_construction`
- `completed`

### Location fields

- `region`
- `address`
- `latitude`
- `longitude`
- `show_exact_location`

### Project information

- `short_description`
- `description`
- `unit_count`
- `start_date`
- `expected_completion_date`
- `features`
- `agent`
- `is_featured`
- `published_at`
- `seo_title`
- `seo_description`
- `created_at`
- `updated_at`

Relationships:

- Each project belongs to one region
- Each project may have one agent
- Each project can have many features
- Each project can have many images

Deletion rules:

- Region uses `PROTECT`
- Agent uses `SET_NULL`
- Project images use `CASCADE`

---

## ProjectImage

Stores images belonging to a construction project.

Fields:

- `project`
- `image`
- `alt_text`
- `sort_order`
- `is_cover`
- `created_at`

Constraints:

- `sort_order` cannot be negative
- Each project can have only one cover image

Deletion rule:

- Deleting a project deletes its related image records

---

# 9. Inquiries Domain

## Inquiry

Represents a customer contact or sales lead.

### Customer fields

- `full_name`
- `phone`
- `email`
- `message`

Rules:

- Name is required
- Phone is required
- Email is optional
- Message is required
- All fields require server-side validation

### Inquiry classification

- `inquiry_type`
- `status`

`inquiry_type` choices:

- `general`
- `property`
- `project`
- `agent`

`status` choices:

- `new`
- `contacted`
- `closed`
- `spam`

### Optional target relationships

- `property`
- `project`
- `agent`

Rules:

- A general inquiry has no target
- A property inquiry may reference one property
- A project inquiry may reference one project
- An agent inquiry may reference one agent
- One inquiry must not reference multiple targets simultaneously
- `GenericForeignKey` will not be used

### Administrative fields

- `admin_notes`
- `created_at`
- `updated_at`

Deletion rules:

- Property uses `SET_NULL`
- Project uses `SET_NULL`
- Agent uses `SET_NULL`

Customer inquiries must remain stored even if the related property, project, or agent is later removed.

---

# 10. Relationship Overview

```text
City
└── Region
    ├── Property
    └── DevelopmentProject

PropertyType
└── Property

Agent
├── Property
└── DevelopmentProject

Property
├── PropertyImage
├── Feature
└── Inquiry

DevelopmentProject
├── ProjectImage
├── ProjectFeature
└── Inquiry

Agent
└── Inquiry
```

---

# 11. Database Constraints

The database should enforce important rules whenever practical.

Required constraints include:

- Unique property listing codes
- Unique project codes
- Unique public slugs
- Non-negative numeric property values
- Only one cover image per property
- Only one cover image per project
- Correct property pricing based on transaction type
- Only one inquiry target at a time
- Unique region names inside each city

Validation must exist at both:

- Form level
- Model level

Critical rules should also use database constraints where possible.

---

# 12. Indexing Strategy

Indexes will be added for real search and filtering requirements.

Likely indexed fields include:

- Property publication status
- Property availability status
- Property transaction type
- Property featured status
- Property publication date
- Project publication status
- Project status
- Project featured status
- Inquiry status
- Inquiry creation date

Foreign-key fields already receive database indexes from Django.

Indexes must not be added to every field without a real query requirement.

---

# 13. Deletion Strategy

The following deletion rules apply:

### PROTECT

Used when deleting referenced data would damage existing content.

Examples:

- City
- Region
- PropertyType

### SET_NULL

Used when historical content should remain after a related object is removed.

Examples:

- Property agent
- Project agent
- Inquiry property
- Inquiry project
- Inquiry agent

### CASCADE

Used for dependent records that have no meaning without their parent.

Examples:

- Property images
- Project images

---

# 14. Data Integrity Principles

The project must follow these principles:

- Do not duplicate city data inside properties
- Do not store features as comma-separated text
- Do not store money as floating-point numbers
- Do not store several unrelated values inside one field
- Do not use generic relationships without a real requirement
- Do not delete customer inquiries automatically
- Do not use zero when a value is genuinely unknown
- Do not create database fields only for temporary UI needs

---

# 15. Database Design Decision Summary

V2 will use:

- PostgreSQL
- Relational models
- Explicit foreign keys
- Separate image models
- Many-to-many feature relationships
- Separate publication and availability statuses
- Decimal money fields
- Unique slugs and listing codes
- Database constraints for critical rules
- Conservative indexing
- Clear deletion behavior

This design provides a maintainable foundation for V2 and supports future V3 development without unnecessary complexity. 