# Makefile
SHELL := /bin/bash
.PHONY: all clean

all clean:
	@total=$$(find . -mindepth 2 -name "Makefile" | wc -l); \
	current=0; \
	width=40; \
	echo "Build started at $$(date)" > build.log; \
	tput civis; \
	find . -mindepth 2 -name "Makefile" -print0 | while IFS= read -r -d '' mkfile; do \
		dir=$$(dirname "$$mkfile"); \
		current=$$((current + 1)); \
		percent=$$((current * 100 / total)); \
		filled=$$((percent * width / 100)); \
		empty=$$((width - filled)); \
		bar_filled=$$(printf "%$${filled}s" | tr " " "#"); \
		bar_empty=$$(printf "%$${empty}s" | tr " " " "); \
		printf "\r%3d%%|%s%s| %d/%d [%s]\033[K" "$$percent" "$$bar_filled" "$$bar_empty" "$$current" "$$total" "$$dir"; \
		if ! $(MAKE) -s -C "$$dir" $@; then \
			printf "\nError processing %s. See build.log\n" "$$dir"; \
		fi; \
	done; \
	echo ""; \
	tput cnorm; \
	echo "Done."
