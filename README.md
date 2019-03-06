# JUNO: a simple weather API
Juno provides a gateway to access the weather forecast for the next three
days through a simple and elegant REST API.

**TO USE:**<br/>
For a server to run JUNO, the server must have Python 3.5 or greater
installed. JUNO was written with the intent to be backwards compatible with
Python 2.7 and earlier versions of Python 3 but it is untested.

The repo comes with JUNO ready to execute locally on port 8080. To start,
simply execute 'scripts/run.sh' from the toplevel directory and JUNO
will begin operating on http://localhost:8080
<br/>NOTE: Alternatively, JUNO can be executed with
'python main.py' also from the top level as JUNO is not an executable
package.



**TO BE VIEWABLE EXTERNALLY:**<br/>
To access JUNO from the web, update the HOST and PORT variables
in JUNO/config.py. HOST should be the server's IP address and PORT
should be the web accessible port that you want to operate on.

**TO SEE JUNOs OUTPUT:**<br/>
Viewing the page at the address and port specified in JUNO/config.py
or by making a GET request to the same page will provide the end user
with the forecast for the city in which they and the server running JUNO
reside.

**FURTHER CONSIDERATION:**<br/>
In the future should the third party weather API which JUNO calls be
updated to support location data as a parameter, JUNO would require
minimal changes to support maintaining a large collection of states'
cities' weather forecasts. Locations where changes would be made are,
for the most part, noted. Some of the design decisions were made with
this in mind.