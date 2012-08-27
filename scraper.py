
from sightandsound import *
import argparse
import sqlite3

if __name__ == "__main__":
    
    default_film_url = r"http://explore.bfi.org.uk/sightandsoundpolls/2012/film"
    default_voter_url = r"http://explore.bfi.org.uk/sightandsoundpolls/2012/voter"
    
    parser = argparse.ArgumentParser(description = "Scrape the 2012 Sight & Sound vote into an SQLite DB.")
    parser.add_argument("db_name", metavar="db_name", type=str, help="name of the database to create")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("--films-url", metavar="URL", type=str, default=default_film_url,
                        help="override the all-films page with a different URL")
    parser.add_argument("--voters-url", metavar="URL", type=str, default=default_voter_url,
                        help="override the all-voters page with a different URL")
    args = vars(parser.parse_args())
    
    conn = sqlite3.connect(args["db_name"])
    scrapeFilms(args["films_url"], conn, verbose=args["verbose"])
    scrapeVoters(args["voters_url"], conn, scrape_ballot=True, verbose=args["verbose"])
    conn.close()