#!"C:\Users\Sunlight Traders\PycharmProjects\Insta\venv\Scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'jet==1.0','console_scripts','jet'
__requires__ = 'jet==1.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('jet==1.0', 'console_scripts', 'jet')()
    )
