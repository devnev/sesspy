#!/bin/sh

if [ x"$1" = x"-c" ]
then
	coverage erase
	for testpy in tests/test_*.py
	do
		coverage run --append $testpy
	done
	coverage html --include='sesspy/*'
else
	PYTHON=${PYTHON:-python}
	case "`${PYTHON} --version 2>&1 | sed 's/Python //'`" in
		2.5*|2.6*) find tests -name 'test_*.py' | xargs -n1 -I "{}" ${PYTHON} "{}" "$@" ;;
		2.7*|3.*) find tests -name 'test_*.py' | tr / . | sed 's/\.py$//' | xargs ${PYTHON} -m unittest "$@" ;;
		*) echo Unsupported python version && exit 1 ;;
	esac
fi
