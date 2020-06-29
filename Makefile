PREFIX=/usr
ROOT=
PYROOT=${ROOT}/
ETC=${ROOT}/etc

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

clean:
		rm -f INSTALLED_FILES
		rm -f INSTALLED_FILES.in

install: clean
		mkdir -p "${ETC}/file-scraper"
		cp file_scraper/vnu/vnu_filters.txt "${ETC}/file-scraper/"

		python setup.py build ; python ./setup.py install -O1 --prefix="${PREFIX}" --root="${PYROOT}" --record=INSTALLED_FILES.in
		cat INSTALLED_FILES.in | sed 's/^/\//g' >> INSTALLED_FILES
		echo "-- INSTALLED_FILES"
		cat INSTALLED_FILES
		echo "--"

test:
		py.test -svvv --maxfail=9999 --junitprefix=file-scraper --junitxml=junit.xml tests

