#!/bin/bash
#
# Run the Static Analysis tests for the failover bash and python scripts

echo "#####################################PYTHON#####################################"
cd ./python/ || exit 1
python_files=()
# Find all python files, and parse into array by null character
while IFS=  read -r -d $'\0'; do
    python_files+=("$REPLY")
done < <(find "." -name "*.py" -not -name "test_*" -print0)

echo "Python files being checked: "
printf '%s\n' "${python_files[@]}"
python "$(which pylint)" "${python_files[@]}"
py_exit="${?}"

echo ""
echo "######################################BASH######################################"
cd ./../bash/ || exit 1
bash_files=()
# Find all Shell files, and parse into array by null character
while IFS=  read -r -d $'\0'; do
    bash_files+=("$REPLY")
done < <(find "." -name "*.sh" -print0)

echo "Bash files being checked: "
printf '%s\n' "${bash_files[@]}"
shellcheck "${bash_files[@]}"
sh_exit="${?}"

# OR, then NOT exit codes so build fails if either check returns warnings
! (( "${py_exit}" || "${sh_exit}" ))
