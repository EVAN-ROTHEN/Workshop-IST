# Génère les PDF des livrables via Marp.
# Trouve automatiquement le Chrome téléchargé par puppeteer.
CHROME := $(shell find $(HOME)/.cache/puppeteer -name chrome -type f 2>/dev/null | head -1)
MARP   := CHROME_PATH="$(CHROME)" npx -y @marp-team/marp-cli@latest --allow-local-files

.PHONY: pdf slides cheatsheet clean

pdf: slides cheatsheet

slides:
	$(MARP) slides/presentation.md --pdf -o slides/presentation.pdf

cheatsheet:
	$(MARP) cheatsheet/cheatsheet.md --pdf -o cheatsheet/cheatsheet.pdf --theme-set cheatsheet/theme-a4.css

clean:
	rm -f slides/presentation.pdf cheatsheet/cheatsheet.pdf
