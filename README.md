# recovery code manager (rcman)
manages your recovery codes for websites that use 2 factor authentication. also
encrypts them with AES encryption and whatnot so that's cool.

note that i am only planning on having full support on linux, so if there's bugs
on other operating systems i really don't care fix it yourself it's open source

## how to use
```bash
pip install --upgrade -r requirements.txt
python main.py
```

if you wanna make this a command that can be run via bash you can do one of the
following:
1. ```bash
   mv /path/to/rcman/main.py /usr/bin/rcman
   ```
2. ```bash
   echo 'alias rcman="python /path/to/rcman/main.py"' >> ~/.bashrc
   ```
