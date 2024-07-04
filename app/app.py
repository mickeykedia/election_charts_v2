# Run in flask environment

import os
import psycopg2
from flask import Flask, render_template, Response
import pandas as pd

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
            database='election_results',
            user=os.environ['DB_USERNAME'],
            password=os.environ['DB_PASSWORD'])
    return conn

def query_db(query, data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, data)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res


@app.route("/api/results/<year>/<party>/<state>")
def get_results(year,party,state=None):
    party_res = query_db("""
With PartyResults AS (
    SELECT
    constituency_num,constituency_name,candidate_name,candidate_pos,gender,votes,total_votes,total_voters
    FROM ls_results
    WHERE party = %s AND year = %s AND state = %s ORDER BY constituency_num
), StateWinners AS (
    SELECT constituency_num,constituency_name,candidate_name,party,gender,votes,total_votes,total_voters
    FROM ls_results
    WHERE candidate_pos = 1 AND year = %s AND state = %s ORDER BY constituency_num
), StateLosers AS (
    SELECT constituency_num,constituency_name,candidate_name,party,gender,votes,total_votes,total_voters
    FROM ls_results
    WHERE candidate_pos = 2 AND year = %s AND state = %s ORDER BY constituency_num
),
PartyLosers AS (
    SELECT
      sw.constituency_name,
      pr.candidate_name,
      pr.votes,
      pr.votes - sw.votes AS margin,
      'LOST' AS status
    FROM
        StateWinners AS sw
        INNER JOIN PartyResults AS pr
        USING (constituency_num)
    WHERE
      pr.candidate_pos != 1
),
PartyWinners AS (
  SELECT
      sl.constituency_name,
      pr.candidate_name,
      pr.votes,
      pr.votes - sl.votes AS margin,
      'WON' AS status
    FROM
        StateLosers AS sl
        INNER JOIN PartyResults AS pr
        USING (constituency_num)
    WHERE
      pr.candidate_pos = 1
)
SELECT * FROM PartyWinners UNION ALL (SELECT * FROM PartyLosers) ORDER BY margin desc
            """, (party, year, state, year, state, year, state))

    party_res = pd.DataFrame(party_res, 
             columns=['constituency_name','candidate_name','votes', 'margin', 'status'])
    return Response(party_res.to_json(orient='records'), mimetype='application/json')


@app.route("/")
def hello_world():
    election_years = query_db('SELECT DISTINCT year FROM ls_results order by year desc', data=None);
    state = query_db('SELECT DISTINCT state FROM ls_results order by state desc', data=None);
    return render_template("index.html", data=election_years, state=state)

