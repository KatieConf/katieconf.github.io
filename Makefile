# Jekyll

serve:
	bundle install
	bundle exec jekyll serve -w


# Imports (Python)

venv:
	test -d venv || virtualenv venv
	venv/bin/python -m pip install -r scripts/requirements.txt

test_import: venv
	venv/bin/python scripts/import_speakers.py

import: venv
	venv/bin/python scripts/import_speakers.py _data/speakers.yml
