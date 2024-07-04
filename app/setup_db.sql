-- create database election_results;

-- GRANT pg_read_all_data TO flaskapp;

DROP TABLE ls_results;

CREATE TABLE IF NOT EXISTS ls_results (
  id SERIAL,
  year SMALLINT,
  state VARCHAR(100),
  constituency_name VARCHAR(255),
  constituency_num SMALLINT,
  constituency_type VARCHAR(32),
  candidate_name VARCHAR(255),
  candidate_pos SMALLINT,
  party VARCHAR(255),
  gender VARCHAR(8),
  votes INTEGER,
  total_votes INTEGER,
  total_voters INTEGER,
  PRIMARY KEY (id)
);


\copy ls_results(state,constituency_num,candidate_pos,candidate_name,gender,votes,total_votes,total_voters,constituency_name,constituency_type,year,party) FROM '/Users/ramya/elections/data/ls_results.csv' WITH DELIMITER ',' CSV HEADER;

