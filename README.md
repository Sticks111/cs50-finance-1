# CS50 - Finance
My work for HarvardX CS50's Finance assignment.

A mock stock-trading website where a user can register, login, change passwords, buy and sell stocks, and see their transaction history.

All of the code I wrote in Python is in **application.py**. Some of the code in that file was provided by CS50 - lines of code that were not written by me are specified in a comment at the top of the file.
Additionally, I wrote all the HTML files inside of templates/ except the files mentioned below.

The following files were provided by CS50 - I did not write any of the code in the below files:
* helpers.py
* templates/login.html
* templates/layout.html
* templates/apology.html
* static/styles.css
* requirements.txt

# Getting Started

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
