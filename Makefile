UUID = app-grid-soft@local
VERSION = 2
ZIP = $(UUID)_v$(VERSION).zip
SOURCES = metadata.json extension.js prefs.js README.md COPYING

.PHONY: all zip-file check
all: zip-file

schemas/gschemas.compiled: schemas/*.gschema.xml
	glib-compile-schemas --strict schemas

check: schemas/gschemas.compiled
	glib-compile-schemas --strict --dry-run schemas

zip-file: check
	zip -q -FS $(ZIP) $(SOURCES) schemas/*.gschema.xml schemas/gschemas.compiled
