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
	find tests -name '*.py' | tr / . | sed 's/\.py$//' | xargs ${PYTHON:-python} -m unittest
fi
