# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2024-12-28

### Added
- **Pagination Support**: Implemented pagination for both task lists and tasks using `@odata.nextLink`
  - Added `PaginatedTaskListResponse` and `PaginatedTaskResponse` models
  - Added `skip_token` parameter to list and task endpoints
  - Returns `nextLink` URL for fetching subsequent pages when more data is available
  - Returns `count` field showing number of items in current page

- **Comprehensive Test Suite**: Added `test_all_fixes.py` to validate all improvements
  - Tests OAUTHLIB environment variables are not forced
  - Tests API prefix normalization
  - Tests async httpx integration
  - Tests GraphAPIError status codes
  - Tests pagination models and routes

### Changed
- **Removed Forced OAUTHLIB Variables**: Removed forced setting of OAUTHLIB environment variables from `config.py`
  - `OAUTHLIB_INSECURE_TRANSPORT`
  - `OAUTHLIB_RELAX_TOKEN_SCOPE`
  - `OAUTHLIB_IGNORE_SCOPE_CHANGE`
  - These can now be set via environment variables for development, but are not required for production
  - Updated `.env.example` with documentation for these variables

- **API Prefix Normalization**: Standardized `settings.api_prefix` format
  - Automatically removes leading and trailing slashes
  - Adds a single leading slash if prefix is not empty
  - Handles spaces and multiple slashes gracefully
  - Prevents route concatenation errors

- **Async HTTP Client**: Replaced synchronous `requests` with `httpx.AsyncClient`
  - All Graph API client methods are now async
  - Prevents blocking in async FastAPI context
  - Improved performance and scalability
  - Added httpx==0.25.2 to requirements

- **Improved Error Handling**: Enhanced `GraphAPIError` exception class
  - Now includes `status_code` attribute
  - Routes use `e.status_code` instead of string matching (e.g., `"404" in str(e)`)
  - More accurate HTTP status code responses
  - Better error messages with `[status_code] message` format

### Updated
- **Documentation**: Updated README_API.md
  - Added pagination documentation with examples
  - Documented OAUTHLIB environment variables for development
  - Updated feature list to highlight new improvements
  - Added httpx to technology stack
  - Added security notes about OAUTHLIB variables

### Technical Details

#### Breaking Changes
- `GraphAPIClient.get_lists()` now returns a dictionary with `value`, `nextLink`, and `count` instead of a list
- `GraphAPIClient.get_tasks()` now returns a dictionary with `value`, `nextLink`, and `count` instead of a list
- All GraphAPIClient methods are now async and must be awaited
- Routes now return paginated responses by default

#### Migration Guide
If you're using the GraphAPIClient directly:

**Before:**
```python
lists = client.get_lists(limit=99)
for lst in lists:
    print(lst.displayName)
```

**After:**
```python
result = await client.get_lists(limit=99)
for lst in result['value']:
    print(lst.displayName)
if result['nextLink']:
    # Fetch next page if needed
    pass
```

#### API Response Format Changes

**Before:**
```json
[
  {"list_id": "...", "displayName": "..."},
  {"list_id": "...", "displayName": "..."}
]
```

**After:**
```json
{
  "value": [
    {"list_id": "...", "displayName": "..."},
    {"list_id": "...", "displayName": "..."}
  ],
  "nextLink": "https://graph.microsoft.com/...",
  "count": 2
}
```

### Security Improvements
- Removed forced insecure OAUTHLIB settings, improving production security
- Environment variables now fully controlled by deployment configuration
- Better separation between development and production configurations
