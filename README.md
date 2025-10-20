# Content Tools Server

A production-ready Python application for automated content ingestion, transformation, and publishing to Telegram channels. Built with FastAPI, PostgreSQL, and Docker.

## Features

- **RSS Ingestion**: Automatically fetch content from Telegram channels via RSSHub
- **AI-Powered Transformation**: Use OpenAI to summarize and generate hashtags
- **Telegram Publishing**: Publish transformed content to your channels
- **Scheduled Automation**: Hourly cron jobs for ingestion, transformation, and publishing
- **Excel Import**: Import sources from Excel files
- **REST API**: Manual triggers and monitoring endpoints
- **Docker-First**: Fully containerized with docker-compose

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RSS Sources   │───▶│  RSS Ingest     │───▶│   PostgreSQL   │
│  (Telegram)     │    │   Service       │    │   Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  NLP Transform  │
                       │   Service       │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Telegram       │───▶│  Your Channels  │
                       │  Publisher      │    │  (Telegram)     │
                       └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose
- Git
- OpenAI API key
- Telegram Bot Token

### 2. Clone and Configure

```bash
# Clone the repository
git clone <your-repo-url>
cd content-tools-server

# Copy configuration files
cp env.example .env
cp config.yaml.example config.yaml

# Edit configuration files
nano .env          # Add your API keys and database credentials
nano config.yaml   # Adjust settings if needed
```

### 3. Start the Application

```bash
# Start all services
make run

# Or manually with docker-compose
docker-compose up -d --build
```

### 4. Import Sources

```bash
# Import sources from Excel template
make import-sources

# Or manually
docker-compose exec app python tools/import_sources.py tools/sources_template.csv
```

### 5. Access the Application

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Configuration

### Environment Variables (.env)

```bash
# Database
POSTGRES_DB=content_tools
POSTGRES_USER=content_tools_user
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql+psycopg://user:pass@db:5432/content_tools

# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Logging
LOG_LEVEL=INFO
```

### Application Config (config.yaml)

```yaml
rsshub_base: "https://rsshub.app"

fetch:
  request_timeout_seconds: 12
  user_agent: "content-tools-bot/1.0"

scheduler:
  ingest_cron: "0 * * * *"      # Every hour at minute 0
  transform_cron: "5 * * * *"    # Every hour at minute 5
  publish_cron: "10 * * * *"    # Every hour at minute 10

nlp:
  provider: "openai"
  summary_prompt_template: |
    Сожми текст в 2–3 предложения новостного формата на русском, без воды.
    Выдели факт/событие и итог для читателя.
    Текст:
    {text}

telegram:
  parse_mode: "HTML"
  disable_web_page_preview: false

publish:
  default_type: "text"
```

## Usage

### Manual Triggers

```bash
# Trigger RSS ingestion
curl -X POST http://localhost:8000/run/ingest

# Trigger NLP transformation
curl -X POST http://localhost:8000/run/transform

# Trigger publishing
curl -X POST http://localhost:8000/run/publish
```

### API Endpoints

- `GET /health` - Health check
- `POST /run/ingest` - Manual RSS ingestion
- `POST /run/transform` - Manual NLP transformation
- `POST /run/publish` - Manual publishing
- `GET /posts?status=new|ready|sent` - List posts with filtering
- `GET /sources` - List all sources
- `GET /channels` - List all channels

### Excel Import

Create an Excel file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| our_channel_username | Target channel username | @mynewschannel |
| source_name | Source display name | Tech News |
| source_username | Source Telegram username | technews |
| description | Source description | Technology news |
| default_image_url | Default image URL | https://example.com/tech.jpg |
| source_type | Type: news or commerce | news |
| enabled | Whether source is enabled | True |

Import sources:
```bash
docker-compose exec app python tools/import_sources.py your_sources.xlsx
```

## Development

### Project Structure

```
content-tools-server/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── db.py                   # Database setup
│   ├── models.py               # SQLAlchemy models
│   ├── migrations/             # Alembic migrations
│   ├── services/
│   │   ├── rss_ingest.py       # RSS ingestion service
│   │   ├── nlp_transform/      # NLP transformation
│   │   └── publisher/          # Publishing services
│   └── jobs/                   # APScheduler jobs
├── tools/
│   ├── import_sources.py       # Excel import CLI
│   └── sources_template.csv    # Import template
├── scripts/
│   ├── provision_server.sh     # Server setup
│   └── deploy.sh               # Deployment script
├── tests/                      # Unit tests
├── docker-compose.yml          # Docker services
├── Dockerfile                  # Application container
└── requirements.txt            # Python dependencies
```

### Running Tests

```bash
# Run all tests
make test

# Or manually
docker-compose exec app python -m pytest tests/ -v
```

### Database Migrations

```bash
# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"

# Apply migrations
make migrate

# Or manually
docker-compose exec app alembic upgrade head
```

## Deployment

### Automated Deployment

1. **Provision Server**:
   ```bash
   ./scripts/provision_server.sh
   ```

2. **Deploy Application**:
   ```bash
   ./scripts/deploy.sh https://github.com/yourusername/content-tools-server.git
   ```

### Manual Deployment

1. **Install Dependencies**:
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo apt-get install docker-compose-plugin
   ```

2. **Clone and Configure**:
   ```bash
   git clone <your-repo-url> /opt/content-tools-server
   cd /opt/content-tools-server
   cp env.example .env
   cp config.yaml.example config.yaml
   # Edit .env and config.yaml
   ```

3. **Start Services**:
   ```bash
   docker-compose up -d --build
   ```

## Monitoring

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f scheduler
```

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check database
docker-compose exec db pg_isready
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check DATABASE_URL in .env
   - Ensure PostgreSQL is running: `docker-compose ps`

2. **OpenAI API Errors**:
   - Verify OPENAI_API_KEY in .env
   - Check API key permissions and billing

3. **Telegram Publishing Failed**:
   - Verify TELEGRAM_BOT_TOKEN in .env
   - Ensure bot is added to target channels
   - Check channel permissions

4. **RSS Fetching Failed**:
   - Verify RSSHub is accessible
   - Check source usernames are correct
   - Review network connectivity

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose restart app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue on GitHub
4. Check the API documentation at `/docs`

---

**Next Steps for Non-Developers:**

1. **Set up your environment**:
   - Get OpenAI API key from https://platform.openai.com
   - Create Telegram bot via @BotFather
   - Install Docker on your server

2. **Configure the application**:
   - Edit `.env` with your API keys
   - Adjust `config.yaml` if needed
   - Create your sources Excel file

3. **Deploy and test**:
   - Run `make run` to start the application
   - Import your sources
   - Test with manual triggers
   - Monitor the logs

4. **Production deployment**:
   - Use the deployment scripts for server setup
   - Set up monitoring and backups
   - Configure your Telegram channels

The application will automatically:
- Fetch new content every hour
- Transform it with AI
- Publish to your channels
- Track what's been published to avoid duplicates
