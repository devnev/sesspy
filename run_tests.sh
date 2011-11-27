#!/bin/sh

if [ x"$1" = x"-c" ]
then
	coverage erase
	for testpy in tests/test_*.py
	do
		coverage run --append $testpy
	done
	coverage html --include='sesspy/*' --omit='sesspy/six.py'
	exit 0
fi

multirun=no
if [ x"$1" = x"-m" ]
then
	multirun=yes
	shift
fi

PYTHON=${PYTHON:-python}
case "`${PYTHON} --version 2>&1 | sed 's/Python //'`" in
	2.5*|2.6*) multirun=yes ;;
esac

if [ $multirun = yes ]
then
	find tests -name 'test_*.py' | xargs -n1 -I "{}" ${PYTHON} "{}" "$@"
else
	find tests -name 'test_*.py' | tr / . | sed 's/\.py$//' | xargs ${PYTHON} -m unittest "$@"
fi
