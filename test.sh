python -m coverage run -m py.test
status=$?
#output=$(coverage report -m)
#coverage_percent=$(echo "${output}" | grep TOTAL | tr -s ' ' | cut -d' ' -f 4)
#if [ $coverage_percent == '100%' ]
#then
#  echo 'Full coverage';
#else
#  echo "Coverage '${coverage_percent}'";
#fi
python -m coverage report -m
exit $status
