# HTAP Configuration Editor - Deployment Guide

## Table of Contents

1. [Production Deployment](#production-deployment)
2. [Configuration](#configuration)
3. [Performance Tuning](#performance-tuning)
4. [Monitoring](#monitoring)
5. [Security](#security)
6. [Backup & Recovery](#backup--recovery)

---

## Production Deployment

### Option 1: Local Deployment (Python + Streamlit)

**Best for**: Single-user workstation deployment, development

**Requirements:**
- Python 3.9+
- HTAP data files accessible locally
- Windows, Linux, or macOS

**Setup:**

1. **Install dependencies**
   ```bash
   cd C:/HTAP/development/htap-config-editor
   pip install -r requirements.txt
   ```

2. **Configure environment** (optional)
   ```bash
   # Create .env file (optional)
   cp .env.example .env
   # Edit paths if HTAP not at C:/HTAP/
   ```

3. **Start application**
   ```bash
   streamlit run app.py --server.port 8501
   ```

4. **Access application**
   - Open browser to `http://localhost:8501`

**Pros:**
- Simple setup
- Full control
- No network required
- Fast data access

**Cons:**
- Single user only
- Requires Python installation
- Manual startup

---

### Option 2: Streamlit Cloud

**Best for**: Multi-user access, no local infrastructure

**Requirements:**
- GitHub account
- Public or private repository
- HTAP data files in repository

**Setup:**

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Visit https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select repository, branch, and file (app.py)
   - Click "Deploy"

3. **Configure secrets** (if needed)
   - In Streamlit Cloud dashboard
   - Add secrets.toml:
     ```toml
     [paths]
     htap_dir = "/path/to/htap"
     options_file = "/path/to/HTAP-options.json"
     costs_file = "/path/to/HTAPUnitCosts.json"
     ```

4. **Access application**
   - Streamlit Cloud provides URL: `https://<app-name>.streamlit.app`

**Pros:**
- No server management
- Automatic updates from git
- HTTPS included
- Free tier available

**Cons:**
- Requires internet access
- Data must be in repository
- Limited to Streamlit Cloud resources
- Public URL (unless private deployment)

---

### Option 3: Docker Container

**Best for**: Reproducible deployments, multi-environment

**Requirements:**
- Docker installed
- HTAP data files accessible

**Setup:**

1. **Create Dockerfile**
   ```dockerfile
   # Dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application
   COPY . .

   # Expose port
   EXPOSE 8501

   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
     CMD curl --fail http://localhost:8501/_stcore/health || exit 1

   # Run application
   CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
   ```

2. **Build image**
   ```bash
   docker build -t htap-config-editor:latest .
   ```

3. **Run container**
   ```bash
   docker run -d \
     --name htap-editor \
     -p 8501:8501 \
     -v C:/HTAP:/htap:ro \
     htap-config-editor:latest
   ```

4. **Access application**
   - Open browser to `http://localhost:8501`

**Pros:**
- Consistent environment
- Easy to replicate
- Isolated from host system
- Version control of deployments

**Cons:**
- Requires Docker knowledge
- Additional overhead
- Volume mounting for data files

**Docker Compose:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  htap-editor:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - C:/HTAP:/htap:ro
    environment:
      - HTAP_PATH=/htap
    restart: unless-stopped
```

Run with: `docker-compose up -d`

---

## Configuration

### Environment Variables

**Supported variables:**

```bash
# HTAP data paths
HTAP_PATH=/path/to/htap
OPTIONS_FILE=/path/to/HTAP-options.json
COSTS_FILE=/path/to/HTAPUnitCosts.json
ARCHETYPE_DIR=/path/to/archetypes

# Application settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

**Usage:**

1. **Command line:**
   ```bash
   export HTAP_PATH=/custom/path
   streamlit run app.py
   ```

2. **.env file:**
   ```bash
   # .env
   HTAP_PATH=/custom/path
   OPTIONS_FILE=/custom/HTAP-options.json
   COSTS_FILE=/custom/HTAPUnitCosts.json
   ```

3. **Docker:**
   ```bash
   docker run -e HTAP_PATH=/htap htap-editor
   ```

---

### Streamlit Configuration

**Configuration file:** `.streamlit/config.toml`

**Recommended settings:**

```toml
[server]
# Port to run on
port = 8501

# Address to bind to (0.0.0.0 for all interfaces)
address = "localhost"

# Disable CORS (if needed for embedding)
enableCORS = false

# Enable XSRF protection
enableXsrfProtection = true

# Max upload size (MB)
maxUploadSize = 10

# Max message size (MB)
maxMessageSize = 10

[browser]
# Don't automatically open browser on startup
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
# Custom theme (optional)
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
# Show error details
showErrorDetails = true

# Toolbar mode
toolbarMode = "minimal"

[runner]
# Faster script rerun
fastReruns = true

# Magic commands
magicEnabled = true

[logger]
# Logging level
level = "info"
```

---

### Theme Settings

**Light theme (default):**
```toml
[theme]
base = "light"
primaryColor = "#1f77b4"
```

**Dark theme:**
```toml
[theme]
base = "dark"
primaryColor = "#4dabf7"
backgroundColor = "#1e1e1e"
secondaryBackgroundColor = "#2d2d2d"
textColor = "#fafafa"
```

**Custom theme:**
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F7F7F7"
secondaryBackgroundColor = "#E8E8E8"
textColor = "#2D3748"
font = "Helvetica"
```

---

## Performance Tuning

### Caching Strategy

**Current implementation:**

1. **Data loading** (@lru_cache)
   - `load_options()`: Cached, 0.32 MB
   - `load_unit_costs()`: Cached, 0.19 MB
   - Cache size: 2 entries each
   - Persistence: Application lifetime

2. **Search indexing** (initialized once)
   - OptionsSearch builds pandas DataFrame at init
   - Reused for all searches
   - <10ms per query

3. **Cost resolution** (@lru_cache)
   - `get_component_cost()`: 1024 entry cache
   - Speeds up repeated lookups
   - Cleared on source change

**Optimization tips:**

- Keep cache sizes reasonable (current settings optimal)
- Don't cache session state (changes frequently)
- Use @st.cache_data for expensive computations
- Clear cache if data files updated

---

### Memory Usage

**Estimated memory footprint:**

- **Base Streamlit**: ~80 MB
- **Python dependencies**: ~120 MB
- **HTAP data loaded**: ~1 MB (0.32 + 0.19 MB files)
- **Search index**: ~2 MB (pandas DataFrame)
- **Session state**: ~1 MB per user
- **Total**: ~200-250 MB per user

**For multi-user deployments:**
- Budget 250 MB per concurrent user
- Example: 10 users = 2.5 GB RAM
- Add 500 MB buffer for OS

**Docker resource limits:**
```bash
docker run --memory=1g --cpus=2 htap-editor
```

---

### Optimization Tips

**1. Data Loading**
- ✅ Already cached with @lru_cache
- ✅ Files are small (0.51 MB total)
- Don't load data in loops
- Don't reload on every interaction

**2. Search Performance**
- ✅ Uses pandas for fast filtering
- ✅ Pre-built index at startup
- Target: <10ms per search
- Limit results to 100 by default

**3. UI Responsiveness**
- Use st.spinner() for operations >500ms
- Lazy load expensive visualizations
- Paginate large result sets
- Minimize widget redraws

**4. Cost Calculations**
- ✅ Component lookups cached
- Calculate on-demand (not precomputed)
- Export to CSV for large analyses
- Use pandas for aggregations

---

## Monitoring

### Health Checks

**Streamlit health endpoint:**
```bash
curl http://localhost:8501/_stcore/health
```

**Expected response:**
```json
{
  "status": "ok"
}
```

**Docker health check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1
```

---

### Logging Configuration

**Streamlit logs:**
- Location: Console output or log file
- Level: Set in `.streamlit/config.toml`
- Format: Timestamp, level, message

**Application logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('htap-editor.log'),
        logging.StreamHandler()
    ]
)
```

**Docker logging:**
```bash
# View logs
docker logs htap-editor

# Follow logs
docker logs -f htap-editor

# Last 100 lines
docker logs --tail 100 htap-editor
```

---

### Error Tracking

**Built-in error handling:**
- @handle_errors decorator on utility functions
- User-friendly error messages in UI
- Technical details in console (development mode)

**Production monitoring:**
1. Set up log aggregation (e.g., ELK, Splunk)
2. Monitor error rates
3. Set alerts for critical errors
4. Review logs regularly

**Metrics to track:**
- Application startup time
- Search query performance
- Cost calculation time
- Error frequency by type
- User session duration

---

## Security

### File Access Restrictions

**HTAP data files:**
- Should be read-only for application
- Mounted as read-only in Docker: `-v path:/htap:ro`
- No user-uploaded files (configuration only)
- No arbitrary file access

**Run file export:**
- Generated in-memory
- Downloaded via browser
- No server-side file writes
- No file execution

---

### Input Sanitization

**Built-in protections:**

1. **Pydantic validation:**
   - All models validated on creation
   - Type checking enforced
   - Invalid data rejected

2. **Path validation:**
   - Paths checked for existence
   - No directory traversal allowed
   - Whitelist allowed directories

3. **Search queries:**
   - Pandas handles escaping
   - No SQL injection risk (no database)
   - No regex injection (uses str.contains)

**Best practices:**
- Don't expose to untrusted networks without authentication
- Use HTTPS in production (Streamlit Cloud provides)
- Validate all user inputs (already implemented)
- Keep dependencies updated

---

### Data Privacy

**What data is collected:**
- Session state (in memory only)
- Selected options (not persisted)
- Generated .run files (downloaded, not stored)
- No user data sent to external services

**What data is NOT collected:**
- No user identification
- No usage tracking (set gatherUsageStats = false)
- No telemetry
- No cookies (except Streamlit session)

**Compliance notes:**
- No personal data processed
- No GDPR concerns (no data storage)
- Run files may contain sensitive project data (handle accordingly)
- Users responsible for securing downloaded files

---

## Backup & Recovery

### What to Backup

**Critical files:**
1. **.run files** (user-generated configurations)
   - Location: User downloads
   - Frequency: After each export
   - Retention: Project lifetime

2. **HTAP data files** (if modified)
   - `HTAP-options.json`
   - `HTAPUnitCosts.json`
   - Frequency: After any edits
   - Retention: Indefinite

3. **Configuration files**
   - `.streamlit/config.toml`
   - `.env` (if using environment variables)
   - `docker-compose.yml` (if using Docker)
   - Frequency: After changes
   - Retention: Version control

**Not critical (can be recreated):**
- Application code (in git)
- Python dependencies (in requirements.txt)
- Docker images (can rebuild)
- Cache files (regenerated on startup)

---

### Disaster Recovery

**Scenario 1: Application crash**

1. Check logs for error:
   ```bash
   docker logs htap-editor
   # or
   streamlit run app.py --logger.level debug
   ```

2. Restart application:
   ```bash
   docker restart htap-editor
   # or
   streamlit run app.py
   ```

3. If persistent, check data files:
   ```bash
   # Verify files not corrupted
   python -c "import json; json.load(open('C:/HTAP/HTAP-options.json'))"
   ```

**Scenario 2: Data file corruption**

1. Restore from backup:
   ```bash
   cp HTAP-options.json.backup HTAP-options.json
   ```

2. Or restore from git:
   ```bash
   git checkout HEAD -- HTAP-options.json
   ```

3. Restart application

**Scenario 3: Lost .run file**

1. Check browser downloads folder
2. Recreate using same selections in application
3. Restore from version control if committed

**Scenario 4: Docker container issues**

1. Stop and remove container:
   ```bash
   docker stop htap-editor
   docker rm htap-editor
   ```

2. Rebuild and restart:
   ```bash
   docker build -t htap-config-editor:latest .
   docker run -d -p 8501:8501 -v C:/HTAP:/htap:ro htap-config-editor
   ```

---

### Backup Scripts

**Simple backup script:**
```bash
#!/bin/bash
# backup-htap-config.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup HTAP data files
mkdir -p "$BACKUP_DIR/$DATE"
cp C:/HTAP/HTAP-options.json "$BACKUP_DIR/$DATE/"
cp C:/HTAP/HTAPUnitCosts.json "$BACKUP_DIR/$DATE/"

# Backup configuration
cp .streamlit/config.toml "$BACKUP_DIR/$DATE/"
cp .env "$BACKUP_DIR/$DATE/" 2>/dev/null

echo "Backup complete: $BACKUP_DIR/$DATE"
```

**Automated backup (cron):**
```bash
# Backup daily at 2 AM
0 2 * * * /path/to/backup-htap-config.sh
```

---

## Production Checklist

**Before deploying:**

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] HTAP data files accessible
- [ ] Paths configured (in .env or config.toml)
- [ ] Health check endpoint working
- [ ] Error handling tested
- [ ] Performance acceptable (<10ms search)
- [ ] Memory usage acceptable (<500 MB)
- [ ] Logs configured and accessible
- [ ] Backup strategy in place
- [ ] Security reviewed (no untrusted access)
- [ ] Documentation accessible to users

**After deploying:**

- [ ] Application accessible at expected URL
- [ ] Can load options database (check middle panel)
- [ ] Can load cost database (check cost tab)
- [ ] Search works (try "window")
- [ ] Can export .run file
- [ ] Downloaded .run file valid
- [ ] Logs show no errors
- [ ] Health check passes
- [ ] Performance meets requirements

---

**Version**: 1.0.0
**Last Updated**: 2025-10-09
**Application**: HTAP Configuration Editor
