
grep ^Depends debian/control | sed 's/Depends: //' | sed 's/,//g' | sed 's/|//g'
