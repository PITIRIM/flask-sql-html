from   flask import Flask, render_template
import pandas as pd
import requests
import json
import urllib
from   pandas.io.json import json_normalize
import sqlite3

app = Flask(__name__)
@app.route("/")
def home():
    #1. INPUT - get data from source
    params = {"verbose" : "true"}
    url = "https://api.usaspending.gov/api/v1/awards/?limit=15"
    r = requests.post(url, data=params)
    print(r.status_code, r.reason)
    r.raise_for_status()
    r.headers
    r.request.headers
    data = r.json() 
    meta = data['page_metadata'
    data = data['results']
    df_API_data = pd.io.json.json_normalize(data)

    #2. PROCESSING - format into a list
    awardsList = []
    for index, row in df_API_data.iterrows():
        record = (row["awarding_agency.id"], row["awarding_agency.office_agency"], \
                  row["awarding_agency.subtier_agency.abbreviation"], \
                  row["awarding_agency.subtier_agency.name"], \
                  row["recipient.recipient_name"], \
                  row["recipient.location.state_name"], \
                  row["total_obligation"], \
                  row["description"]
                         )
        awardsList.append(record)

    #2.1 PROCESSING - write to sql. kill and fill.
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    #c.execute('''CREATE TABLE awards (awarding_agency_id text, awarding_agency_office_agency text, awarding_agency_subtier_agency_abbreviation text, awarding_agency_subtier_agency_name text)''')
    c.execute("DELETE  FROM awards")
    c.executemany('INSERT INTO awards VALUES (?,?,?,?,?,?,?,?)', awardsList)
    conn.commit()
    conn.close()

    #3. OUTPUT - create output html file and build the html via the
    #write html header
    outfile = open("C:\\Users\\pitir\\AppData\\Local\\Programs\\Python\\Python37\\templates\\awards.html", "w")
    outfile.write("""<html>
    <head>
     <title>USA Spending - Awards</title>
    </head>
    <body>
    <table border="1">""")
    outfile.write('\n' + "<tr><th>Agendy ID</th><th>Office</th><th>Subtier Abbreviation</th><th>Subtier Name</th> \
                              <th>Recipient</th><th>Location State</th><th>Total Obligation</th><th>Description</th> \
                          </tr>")

    #3.1 read sql table and build html table
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM awards'):
            outfile.write('\n' + "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
    conn.close()

    #3.2 write html trailer
    outfile.write('\n' + """</table></body></html>""")
    outfile.close()

    #3.3 render the new awards.html to browser
    return render_template("awards.html")
          
if __name__ == "__main__":
    app.run(debug=True)
