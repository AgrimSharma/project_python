# /bin/bash

find /path/to/files -atime +99 -type f -exec rm -f {}\;
