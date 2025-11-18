# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of HubSpot ↔ IndieStack sync service
- Bidirectional sync for Contacts, Companies, and Deals
- Configurable field mappings via YAML
- Three conflict resolution strategies (indie_wins, hubspot_wins, newest_wins)
- FastAPI REST API for programmatic control
- Typer-based CLI for manual operations
- SQLite/PostgreSQL tracking database
- Comprehensive error logging and tracking
- Dry-run mode for testing changes
- Structured logging with JSON and text formats
- HubSpot CRM v3 API integration
- IndieStack database integration (PostgreSQL)
- Field transformation support (datetime, enums, etc.)
- Sync run history and statistics
- Health check endpoints
- Rich CLI output with tables and colors

### Documentation
- Comprehensive README with quick start guide
- Architecture documentation
- Usage examples for common scenarios
- Configuration guide
- API documentation
- CLI reference

### Testing
- Unit tests for mapping engine
- Test fixtures and configuration
- pytest setup with coverage support

### Project Structure
- Modular architecture with clear separation of concerns
- Repository pattern for data access
- Protocol-based interfaces for extensibility
- Environment-based configuration
- Entry points for CLI and API

## [Unreleased]

### Planned Features
- Real-time sync via webhooks
- Conflict resolution UI
- Field-level change tracking
- Multi-tenant support
- Custom transformation scripts
- Sync scheduling UI
- Performance dashboard
- Audit trail for compliance
- Incremental sync based on timestamps
- Association sync (contact→company, deal→contact, etc.)
- API-based IndieStack integration
- Advanced filtering and field selection
- Bulk operations support
- Import/export of sync configurations
- Slack/email notifications for sync failures
- Retry logic with exponential backoff
- Rate limiting for API calls
- Custom conflict resolution strategies
- Data validation rules
- Rollback support for failed syncs

### Known Issues
- Association sync not yet implemented
- API-based IndieStack integration not available
- No webhook support for real-time sync
- Limited HubSpot API error handling
- No built-in retry logic for transient failures

### Breaking Changes
None

---

## Version History

- **1.0.0** - Initial release with core functionality
