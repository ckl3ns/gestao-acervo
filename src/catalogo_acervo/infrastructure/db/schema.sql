PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  source_type TEXT NOT NULL,
  parser_name TEXT NOT NULL,
  description TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS imports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL,
  import_mode TEXT NOT NULL,
  imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status TEXT NOT NULL,
  total_read INTEGER NOT NULL DEFAULT 0,
  total_inserted INTEGER NOT NULL DEFAULT 0,
  total_updated INTEGER NOT NULL DEFAULT 0,
  total_skipped INTEGER NOT NULL DEFAULT 0,
  total_errors INTEGER NOT NULL DEFAULT 0,
  raw_file_name TEXT,
  FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE TABLE IF NOT EXISTS catalog_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL,
  source_key TEXT NOT NULL,
  item_type TEXT NOT NULL,
  title_raw TEXT NOT NULL,
  title_norm TEXT,
  subtitle_raw TEXT,
  author_raw TEXT,
  author_norm TEXT,
  series_raw TEXT,
  series_norm TEXT,
  publisher_raw TEXT,
  publisher_norm TEXT,
  year INTEGER,
  language TEXT,
  volume TEXT,
  edition TEXT,
  path_or_location TEXT,
  resource_type TEXT,
  raw_record_json TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  current_import_id INTEGER,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(source_id, source_key),
  FOREIGN KEY (source_id) REFERENCES sources(id),
  FOREIGN KEY (current_import_id) REFERENCES imports(id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS catalog_items_fts USING fts5(
  title_norm,
  author_norm,
  series_norm,
  content='catalog_items',
  content_rowid='id'
);

CREATE TABLE IF NOT EXISTS matches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  left_item_id INTEGER NOT NULL,
  right_item_id INTEGER NOT NULL,
  match_score REAL NOT NULL,
  match_rule TEXT NOT NULL,
  status TEXT NOT NULL,
  confidence_band TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(left_item_id, right_item_id),
  FOREIGN KEY (left_item_id) REFERENCES catalog_items(id),
  FOREIGN KEY (right_item_id) REFERENCES catalog_items(id)
);

CREATE TABLE IF NOT EXISTS manual_reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  left_item_id INTEGER NOT NULL,
  right_item_id INTEGER NOT NULL,
  decision TEXT NOT NULL,
  note TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (left_item_id) REFERENCES catalog_items(id),
  FOREIGN KEY (right_item_id) REFERENCES catalog_items(id)
);

CREATE TABLE IF NOT EXISTS aliases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  alias_kind TEXT NOT NULL,
  alias_text TEXT NOT NULL,
  canonical_text TEXT NOT NULL,
  source_scope TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS themes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS item_themes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id INTEGER NOT NULL,
  theme_id INTEGER NOT NULL,
  assignment_type TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(item_id, theme_id),
  FOREIGN KEY (item_id) REFERENCES catalog_items(id),
  FOREIGN KEY (theme_id) REFERENCES themes(id)
);

CREATE TABLE IF NOT EXISTS processing_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER,
  import_id INTEGER,
  level TEXT NOT NULL,
  message TEXT NOT NULL,
  context_json TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (source_id) REFERENCES sources(id),
  FOREIGN KEY (import_id) REFERENCES imports(id)
);

CREATE TRIGGER IF NOT EXISTS catalog_items_ai AFTER INSERT ON catalog_items BEGIN
  INSERT INTO catalog_items_fts(rowid, title_norm, author_norm, series_norm)
  VALUES (new.id, new.title_norm, new.author_norm, new.series_norm);
END;

CREATE TRIGGER IF NOT EXISTS catalog_items_au AFTER UPDATE ON catalog_items BEGIN
  INSERT INTO catalog_items_fts(catalog_items_fts, rowid, title_norm, author_norm, series_norm)
  VALUES('delete', old.id, old.title_norm, old.author_norm, old.series_norm);
  INSERT INTO catalog_items_fts(rowid, title_norm, author_norm, series_norm)
  VALUES (new.id, new.title_norm, new.author_norm, new.series_norm);
END;

CREATE TRIGGER IF NOT EXISTS catalog_items_ad AFTER DELETE ON catalog_items BEGIN
  INSERT INTO catalog_items_fts(catalog_items_fts, rowid, title_norm, author_norm, series_norm)
  VALUES('delete', old.id, old.title_norm, old.author_norm, old.series_norm);
END;
