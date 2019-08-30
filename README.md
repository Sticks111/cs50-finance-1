## CS50 - Finance
My work for CS50's Finance assignment.
Some of the code was already provided by CS50 - lines of code that were not written by me are specified in a comment at the top of each file.

## Getting Started

Install Flask and activate environment. 
Install requirements.txt by executing the below into the console within the project folder:

```
pip install -r requirements.txt
```

Execute the following in order to query IEX's stock data (I'm providing the API key already, but you may get your own from iexcloud.io):
```
export API_KEY=pk_c815e2f1f9214bd8b74aafb65702bbee
```

Then execute the following to run:
```
export FLASK_APP=application.py
```
```
flask run
```

Go to the local host URL provided.
