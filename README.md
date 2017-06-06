# Test on fake API https://jsonplaceholder.typicode.com

## Before first run
Create and activate virtualenv and install prerequisites
```
virtualenv .virenv
. .virenv/bin/activate
pip install -r requirements
```

## Run tests
Specify server to run tests against
```
export JSON_SERVER_URL=http://localhost:3000
```
Run
```
nosetests
```
