# Cosmic Explorer Cache Directory

This directory stores temporary cache files for the Cosmic Explorer application.

## Contents

- **space_cache.json**: Cached search results and scraped data
- **nlp_cache.json**: Cached NLP processing results
- **temp/**: Temporary files during processing

## Cache Management

The cache is automatically managed by the application:
- Cache files expire after 1 hour by default
- Maximum cache size is limited to prevent excessive storage use
- Cache can be disabled in development mode

## Manual Cache Clearing

To manually clear the cache:
1. Delete all files in this directory
2. Restart the application

The application will automatically recreate cache files as needed.
