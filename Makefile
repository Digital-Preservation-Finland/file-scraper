PREFIX=/usr
ROOT=
PYROOT=${ROOT}/

all: info

info:
		@echo
		@echo "PAS contract database"
		@echo
		@echo "Usage:"
		@echo "  make clean             - Clean some temporary file"
		@echo "  make test              - Run all unit tests"
		@echo "  make install           - Install file-scraper"
		@echo

clean: clean-rpm
		rm -f INSTALLED_FILES
		rm -f INSTALLED_FILES.in

install: clean
		python setup.py build ; python ./setup.py install -O1 --prefix="${PREFIX}" --root="${PYROOT}" --record=INSTALLED_FILES.in
		cat INSTALLED_FILES.in | sed 's/^/\//g' >> INSTALLED_FILES
		echo "-- INSTALLED_FILES"
		cat INSTALLED_FILES
		echo "--"

install3: clean
		python3 setup.py build ; python3 ./setup.py install -O1 --prefix="${PREFIX}" --root="${PYROOT}" --record=INSTALLED_FILES.in
		cat INSTALLED_FILES.in | sed 's/^/\//g' >> INSTALLED_FILES
		echo "-- INSTALLED_FILES"
		cat INSTALLED_FILES
		echo "--"

clean-rpm:
	rm -rf rpmbuild

rpm: clean
	create-archive.sh
	preprocess-spec-m4-macros.sh include/rhel7
	build-rpm.sh

rpm3: clean
	create-archive.sh
	preprocess-spec-m4-macros.sh include/rhel8
	build-rpm.sh
