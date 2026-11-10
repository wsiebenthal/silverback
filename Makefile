# Common commands for the Silver Back monorepo.
# The desktop package imports from ./desktop when this Python is the one
# that ran `pip install -e "./desktop[dev]"`.

PY ?= python3

.PHONY: install test test-desktop test-extension check-syntax demo

install:
	$(PY) -m pip install -e "./desktop[dev]"

test-desktop:
	cd desktop && $(PY) -m pytest

test-extension:
	node --test extension/tests/*.test.js

check-syntax:
	node --check extension/src/background.js
	node --check extension/src/popup.js
	node --check extension/src/options.js
	node --check extension/src/tab_policy.js

test: test-desktop test-extension check-syntax

# Opens a titled X11 window and minimizes it with the simulated trigger.
# Requires xmessage and a window title of "SilverBack Demo" (the example config).
demo:
	xmessage -title "SilverBack Demo" -buttons close -timeout 25 "Silver Back demo. This window should minimize." &
	sleep 0.8
	$(PY) -m silverback trigger --config desktop/silverback.config.example.json
