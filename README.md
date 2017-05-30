Raspberry Pi Controller Server
===

### Installation
This project must be installed on a Raspberry Pi and requires MongoDB and Nginx to be installed.

```bash
git clone git@github.com:PeterCP/RasPiController-Python.git
cd RasPiController-Python
pip install -r requirements.txt
python manage.py runserver
```

**NOTE**: The GPIO python requirement is commented in requirements.txt to allow for testing on a
normal dev machine. Also, to actually modify pin states on the GPIO board, all commented lines
in app/handlers.py must be uncommented.
