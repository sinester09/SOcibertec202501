
#!/bin/bash

#variables comparar if

home='/home'
var2=$(pwd)

if test $home = $var2; then
echo "ejecutando..... en $var2"

for i in *; do

        echo "guardando archivoarchivos en $home"
        echo "$i" >> texto2.txt

done

else
echo "no"
fi
















