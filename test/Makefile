.PHONY: test clean

TEST_OUT=SPyFFIdata/outputs/18h00m00s+66d33m39s_smallone/1800s/sub400x400/simulated_18h00m00s+66d33m39s_sub400x400_000000.fits
test: $(TEST_OUT) light_curve_tests


###################### Virtual Environment ######################

.PHONY: install pre-install
VIRTUAL_ENV=$(CURDIR)/venv
PYTHON=$(VIRTUAL_ENV)/bin/python2.7
PIP=$(VIRTUAL_ENV)/bin/pip2.7
SITE_PACKAGES=$(VIRTUAL_ENV)/lib/python2.7/site-packages
VERSION=$(shell python -c "$(shell grep '^VERSION' $(CURDIR)/../setup.py) ; print VERSION")
INSTALL=$(SITE_PACKAGES)/SPyFFI-$(VERSION)-py2.7.egg
MATPLOTLIBRC=~/.matplotlib/matplotlibrc

$(VIRTUAL_ENV):
	virtualenv --python=python2.7 $@

$(SITE_PACKAGES)/numpy: $(VIRTUAL_ENV)
	$(PIP) install $(notdir $@)

$(SITE_PACKAGES)/pyds9.py: $(VIRTUAL_ENV)
	$(PIP) install git+https://github.com/ericmandel/pyds9.git

$(INSTALL): $(SITE_PACKAGES)/numpy $(VIRTUAL_ENV)
	make pre-install
	(cd ..; $(PYTHON) setup.py install)
	@# Hack to deal with http://stackoverflow.com/a/21789908/586893
	@if [ "$(shell uname)" == "Darwin" ]; then \
		if [ ! -f $(MATPLOTLIBRC) ] || \
		   [ -z "$(shell grep 'backend: TkAgg' $(MATPLOTLIBRC))" ]; then \
			echo 'backend: TkAgg' >> $(MATPLOTLIBRC); \
		fi ; \
	fi

$(VIRTUAL_ENV)/lib/python2.7/site-packages/%: $(SITE_PACKAGES)/numpy $(VIRTUAL_ENV)
	$(PIP) install $(notdir $@)

pre-install: $(addprefix $(SITE_PACKAGES)/, numpy matplotlib astropy astroquery scipy pyds9.py)

install: $(INSTALL)

uninstall: $(INSTALL)
	echo y | $(PIP) uninstall SPyFFI


###################### Testing ######################

light_curve_tests: light_curve_draw_rotation_test light_curve_draw_transit_test

SPyFFIdata/inputs:
	mkdir -p $(dir $@)
	wget -qO- https://www.dropbox.com/s/0e4c2uk34phv4qx/SPyFFI_coreinputs.tar.gz | tar xzv -C $(dir $@)

$(TEST_OUT): SPyFFIdata/inputs
	# PYTHONPATH: Where the Python scripts can be found (i.e. the directory containing SPyFFI/ and zachopy/)
	# SPYFFIPATH: The root directory of SPyFFI (needed for some file-finding by the code)
	# SPYFFIDATA: The directory where you want to store TESS data (inputs/intermediates/outputs)
	PYTHONPATH=$(CURDIR)/../.. SPYFFIPATH=$(CURDIR)/.. SPYFFIDATA=$(CURDIR)/SPyFFIdata/ ./smallone.py

light_curve_%_test: light_curve_%.out
	cmp --quiet $< reference/$<

light_curve_%.out: light_curve_%.py $(INSTALL)
	$(PYTHON) $< > $@

clean:
	rm -rf SPyFFIdata $(VIRTUAL_ENV)