run:
	textual run --dev src/logsift/__main__.py tail -f /var/log/syslog

build:
	@echo Generating Distribution Packages
	@python -m build

clean:
	@-pip uninstall logsift
