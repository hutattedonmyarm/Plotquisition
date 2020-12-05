coverage run -m py.test
status=$?
coverage report -m
#coverage report -m | grep TOTAL | tr -s ' ' | cut -d' ' -f 4
exit $status
