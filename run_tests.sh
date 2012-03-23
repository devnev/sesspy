#!/bin/sh
#
# Copyright 2012 Mark Nevill
# This file is part of sesspy.
# 
# sesspy is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
# 
# sesspy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with sesspy.  If not, see <http://www.gnu.org/licenses/>.

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
