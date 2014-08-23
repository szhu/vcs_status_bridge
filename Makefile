GEM_NAME = vcs_status_bridge

all:
	gem build $(GEM_NAME).gemspec

install: all
	gem install $(GEM_NAME)

uninstall:
	gem uninstall $(GEM_NAME)

clean:
	rm $(GEM_NAME)-*.gem

.PHONY: all install clean
