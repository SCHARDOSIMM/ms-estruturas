"""Audit that installation tests do not change the real user's preferences."""
import hashlib
import json
from PyQt5.QtCore import QSettings

c=QSettings('Ecoplan','Estrutural');c.sync()
data=json.dumps({key:c.value(key) for key in sorted(c.allKeys())},ensure_ascii=False,sort_keys=True,default=str)
print(hashlib.sha256(data.encode('utf-8')).hexdigest())
