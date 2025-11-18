# Capital Ink Hub Email Campaign Engine

A modular, production-ready email campaign engine for **m.capitalinkhub.com** that handles:
- Cold outreach to buyers and sellers
- Member email communications
- Warm lead follow-ups

Built with Python, SQLAlchemy, and Jinja2, with support for multiple email backends (Sendy API and SMTP).

---

## Features

✅ **Multiple Campaign Types**: Cold outreach, member updates, warm lead nurturing
✅ **Flexible Email Backends**: Sendy HTTP API and generic SMTP
✅ **Template System**: Jinja2-based email templates with merge fields
✅ **Rate Limiting**: Configurable hourly/daily limits with random delays
✅ **Segmentation**: Buyer, seller, investor, advisor, member, cold lead
✅ **CSV Import**: Easy recipient import from CSV files
✅ **Activity Logging**: Webhook integration for IndieStack CRM
✅ **CLI Interface**: Comprehensive command-line tools
✅ **Extensible**: Clean architecture for future integrations

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Database Setup](#database-setup)
  - [Creating Campaigns](#creating-campaigns)
  - [Importing Recipients](#importing-recipients)
  - [Scheduling Campaigns](#scheduling-campaigns)
  - [Running the Worker](#running-the-worker)
- [Email Templates](#email-templates)
- [Rate Limiting](#rate-limiting)
- [Email Backends](#email-backends)
- [IndieStack Integration](#indiestack-integration)
- [Testing](#testing)
- [Architecture](#architecture)
- [Extending](#extending)

---

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. **Clone or download the project:**
   ```bash
   cd capitalinkhub-email-engine
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

5. **Edit `.env` with your configuration** (see [Configuration](#configuration))

---

## Quick Start

```bash
# 1. Initialize database
./email-engine db init

# 2. Create a campaign
./email-engine campaign create \
  --name "Q1 Buyer Outreach" \
  --type cold \
  --subject "Exclusive Business Acquisition Opportunities" \
  --template templates/cold_outreach_buyer.html \
  --sender-name "Capital Ink Hub" \
  --sender-email "outreach@capitalinkhub.com" \
  --backend smtp

# 3. Import recipients
./email-engine recipient import 1 \
  --file examples/sample_buyers.csv \
  --email-col email \
  --name-col name \
  --segment-col segment

# 4. Schedule the campaign
./email-engine campaign schedule 1 --when now

# 5. Run the worker
./email-engine worker run --continuous --interval 60
```

---

## Configuration

Edit the `.env` file with your settings:

### Database
```env
DATABASE_URL=sqlite:///./email_campaigns.db
```

### Sendy Configuration
```env
SENDY_BASE_URL=https://your-sendy-instance.com
SENDY_API_KEY=your_api_key
SENDY_LIST_ID=your_list_id
```

### SMTP Configuration
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
SMTP_FROM_NAME=Capital Ink Hub
SMTP_FROM_EMAIL=noreply@capitalinkhub.com
```

### Rate Limiting Defaults
```env
DEFAULT_MAX_PER_HOUR=100
DEFAULT_MAX_PER_DAY=500
DEFAULT_MIN_DELAY_SECONDS=2
DEFAULT_MAX_DELAY_SECONDS=7
```

### IndieStack Integration (Optional)
```env
INDIESTACK_WEBHOOK_URL=https://your-crm.com/webhook/email-events
INDIESTACK_API_KEY=your_webhook_api_key
```

### Application Settings
```env
LOG_LEVEL=INFO
LOG_FILE=logs/email_engine.log
ENVIRONMENT=production
```

---

## Usage

### Database Setup

#### Initialize Database
```bash
./email-engine db init
```

This creates all tables and a default rate limit profile.

#### Create Custom Rate Limit Profile
```bash
./email-engine db create-rate-limit \
  --name "aggressive" \
  --max-hour 200 \
  --max-day 1000 \
  --min-delay 1 \
  --max-delay 3
```

---

### Creating Campaigns

```bash
./email-engine campaign create \
  --name "Campaign Name" \
  --type [cold|member|warm] \
  --subject "Subject line with {{ merge_fields }}" \
  --template templates/your_template.html \
  --sender-name "Your Name" \
  --sender-email "you@example.com" \
  --backend [sendy|smtp] \
  --rate-limit default
```

**Campaign Types:**
- `cold`: Cold outreach to prospects
- `member`: Communications to existing members
- `warm`: Follow-ups to engaged leads

**Example:**
```bash
./email-engine campaign create \
  --name "Seller Outreach April" \
  --type cold \
  --subject "Thinking about selling {{ company_name }}?" \
  --template templates/cold_outreach_seller.html \
  --sender-name "Sarah Johnson" \
  --sender-email "sarah@capitalinkhub.com" \
  --backend smtp
```

#### List Campaigns
```bash
./email-engine campaign list
./email-engine campaign list --status scheduled
./email-engine campaign list --type cold
```

---

### Importing Recipients

```bash
./email-engine recipient import <campaign_id> \
  --file path/to/recipients.csv \
  --email-col email \
  --name-col name \
  --segment-col segment \
  --default-segment other
```

**CSV Format:**

Your CSV should have at minimum an `email` column. Additional columns become merge fields.

Example `recipients.csv`:
```csv
email,name,segment,company_name,industry,target_revenue
john@example.com,John Smith,buyer,Smith Capital,Technology,$1M-5M
sarah@example.com,Sarah Johnson,seller,TechCorp,SaaS,$2M
```

**Segments:**
- `buyer` - Business buyers
- `seller` - Business sellers
- `investor` - Investors
- `advisor` - Advisors
- `member` - Existing members
- `cold_lead` - Cold leads
- `other` - Other

---

### Scheduling Campaigns

```bash
# Schedule for immediate sending
./email-engine campaign schedule <campaign_id> --when now

# Schedule for specific time (ISO format)
./email-engine campaign schedule <campaign_id> --when "2024-12-01 09:00:00"
```

---

### Running the Worker

The worker processes scheduled campaigns and sends emails.

#### Single Run
```bash
./email-engine worker run --max-sends 100
```

#### Continuous Mode
```bash
./email-engine worker run --continuous --interval 60
```

**Options:**
- `--continuous` / `-c`: Run continuously
- `--interval` / `-i`: Seconds between runs (default: 60)
- `--max-sends` / `-m`: Max emails per run (default: 100)

#### Check Worker Status
```bash
./email-engine worker status
```

---

## Email Templates

Templates use **Jinja2** syntax and are stored in the `templates/` directory.

### Available Merge Fields

**Standard fields** (always available):
- `{{ email }}` - Recipient email
- `{{ name }}` - Recipient full name
- `{{ first_name }}` - First name only
- `{{ segment }}` - Recipient segment

**Custom fields**: Any column from your CSV becomes a merge field.

### Example Template

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Hi {{ first_name|default('there') }},</h2>

    {% if company_name %}
    <p>I noticed your company, <strong>{{ company_name }}</strong>.</p>
    {% endif %}

    <p>We specialize in {{ industry|default('your') }} industry...</p>

    <p>Best regards,<br>
    {{ sender_name }}</p>
</body>
</html>
```

### Custom Filters

- `{{ value|currency }}` - Format as currency: `$1,234.56`
- `{{ text|titlecase }}` - Title case: `"john smith"` → `"John Smith"`
- `{{ value|default('fallback') }}` - Use fallback if empty

### Included Templates

- `templates/cold_outreach_buyer.html` - For buyer outreach
- `templates/cold_outreach_seller.html` - For seller outreach
- `templates/member_update.html` - For member communications

---

## Rate Limiting

Rate limiting prevents sending too many emails too quickly.

### How It Works

1. **Hourly Limit**: Max emails per rolling hour
2. **Daily Limit**: Max emails per calendar day (UTC)
3. **Random Delays**: Random 2-7 second delays between sends (configurable)

### Rate Limit Profiles

Create custom profiles for different campaign needs:

```bash
./email-engine db create-rate-limit \
  --name "conservative" \
  --max-hour 50 \
  --max-day 300 \
  --min-delay 5 \
  --max-delay 10
```

### Behavior

- Worker checks limits before each send
- If hourly limit reached: waits until next hour
- If daily limit reached: waits until next day
- Random delays humanize sending patterns

---

## Email Backends

### SMTP Backend

Generic SMTP sender. Works with any SMTP server.

**Configuration:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your_password
SMTP_USE_TLS=true
```

**Gmail Users:** Use an [App Password](https://support.google.com/accounts/answer/185833)

### Sendy Backend

Sends via Sendy API.

**Configuration:**
```env
SENDY_BASE_URL=https://your-sendy.com
SENDY_API_KEY=your_api_key
SENDY_LIST_ID=default_list_id
```

**Note:** The current implementation uses Sendy's campaign creation API. Adjust based on your Sendy setup.

---

## IndieStack Integration

Send email events to IndieStack CRM via webhook.

### Setup

1. Configure webhook URL:
   ```env
   INDIESTACK_WEBHOOK_URL=https://your-crm.com/webhooks/email
   INDIESTACK_API_KEY=your_key
   ```

2. Events are sent automatically after each email

### Webhook Payload

```json
{
  "event_type": "email_sent",
  "campaign_id": 1,
  "campaign_name": "Q1 Outreach",
  "campaign_type": "cold",
  "recipient_email": "john@example.com",
  "recipient_name": "John Smith",
  "recipient_segment": "buyer",
  "sent_at": "2024-11-18T10:30:00",
  "success": true,
  "message_id": "abc123",
  "backend": "smtp"
}
```

### Future Extension

To replace webhook with direct API integration:

1. Create new class in `app/scheduler/activity_logger.py`
2. Extend `ActivityLogger` base class
3. Update `get_activity_logger()` factory

---

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_template_renderer.py
```

### Test Coverage

Included tests:
- ✅ Template rendering and validation
- ✅ Rate limiting logic
- ✅ CSV contact source loading
- ✅ Merge fields and custom filters

---

## Architecture

```
capitalinkhub-email-engine/
├── app/
│   ├── core/              # Configuration, logging, database
│   ├── models/            # SQLAlchemy models (Campaign, Recipient, etc.)
│   ├── repositories/      # Database access layer
│   ├── senders/           # Email backend implementations
│   ├── scheduler/         # Rate limiting, worker, activity logging
│   ├── cli/               # CLI commands
│   └── utils/             # Template rendering, contact sources
├── templates/             # Jinja2 email templates
├── examples/              # Sample CSV files
├── tests/                 # Unit tests
├── .env                   # Environment configuration (create from .env.example)
├── requirements.txt       # Python dependencies
└── email-engine          # CLI entrypoint
```

### Key Design Patterns

- **Repository Pattern**: Clean data access abstraction
- **Adapter Pattern**: Pluggable email backends
- **Factory Pattern**: Dynamic sender creation
- **Strategy Pattern**: Rate limiting strategies

---

## Extending

### Adding a New Email Backend

1. Create file in `app/senders/`:
   ```python
   from .base import EmailSender, EmailMessage, SendResult

   class CustomSender(EmailSender):
       def send(self, message: EmailMessage) -> SendResult:
           # Your implementation
           pass

       def validate_config(self) -> bool:
           # Validate configuration
           pass
   ```

2. Register in `EmailBackend` enum (`app/models/enums.py`)

3. Update factory in `app/senders/factory.py`

### Adding a New Contact Source

1. Create class in `app/utils/contact_source.py`:
   ```python
   class MyContactSource(ContactSource):
       def load_contacts(self) -> List[Dict[str, Any]]:
           # Load from your source
           pass
   ```

2. Use in custom import scripts

### Adding Custom Template Filters

Edit `app/utils/template_renderer.py`:

```python
def _my_custom_filter(value):
    return value.upper()

self.env.filters["uppercase"] = _my_custom_filter
```

Use in templates: `{{ text|uppercase }}`

---

## Production Deployment

### Using Cron

```bash
# Run worker every minute
* * * * * cd /path/to/capitalinkhub-email-engine && ./email-engine worker run --max-sends 50 >> /var/log/email-worker.log 2>&1
```

### Using Systemd

Create `/etc/systemd/system/email-worker.service`:

```ini
[Unit]
Description=Email Campaign Worker
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/capitalinkhub-email-engine
ExecStart=/path/to/capitalinkhub-email-engine/venv/bin/python email-engine worker run --continuous --interval 60
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable email-worker
sudo systemctl start email-worker
```

### Database Backups

```bash
# SQLite backup
cp email_campaigns.db email_campaigns.backup.db

# Or use cron for automated backups
0 2 * * * cp /path/to/email_campaigns.db /backups/email_campaigns_$(date +\%Y\%m\%d).db
```

---

## Troubleshooting

### Common Issues

**"SMTP authentication failed"**
- Check username/password
- For Gmail, use App Password
- Verify SMTP settings

**"Template not found"**
- Ensure template file exists in `templates/` directory
- Check path is relative to `templates/` folder

**"Rate limit profile not found"**
- Run `./email-engine db init` to create default profile
- Or create custom profile with `db create-rate-limit`

**No emails sending**
- Check campaign status: `./email-engine campaign list`
- Verify campaign is scheduled: `campaign schedule <id> --when now`
- Check worker status: `./email-engine worker status`

---

## Support & Contributing

For issues, questions, or contributions, contact the Capital Ink Hub development team.

---

## License

Proprietary - Capital Ink Hub

---

**Built with ❤️ for Capital Ink Hub**
