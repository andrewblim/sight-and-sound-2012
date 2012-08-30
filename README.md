
sight-and-sound-2012
====================

About
-----

This is a simple scraper program to download the contents from the Sight & Sound 2012 Poll, as published in the format on the [BFI's web page](http://explore.bfi.org.uk/sightandsoundpolls/2012/), into an SQLite database. 

License: MIT, included in `license.txt`.

Requirements
------------

I used the following, but any reasonably up-to-date versions should be OK: 

- [Python](http://www.python.org/) 2.7.3
- [SQLite](http://www.sqlite.org/) 3.7.13
- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) 4.1.3 (older than 4.1.2 won't work due to usage of `class_`)

Usage
-----

`python scraper.py [db_name]`

The `--help` flag will give you command-line help and a few additional flags to use. 

The resulting SQL database contains two tables, `films` and `voters`. `films` contains an ID string, title, URL for web page on BFI website, year, director, and country. `voters` contains an ID string, name of voter, poll in which he or she participated, occupation, sex, country, and columns `film_id1` through `film_id12` indicating the IDs of the films he or she voted for. 

Not all fields are always populated; in some cases country, occupation, sex, and URL were unpopulated and so will be blank in the database. 

Multiple countries and directors are separated by a comma and a space: ", ". 

The film and voter IDs are MD5 hashes of some of the data items and do not correspond to the implied ID in the URL on the BFI's website (for example Aaron Katz's ID is `8de84a461911f527dec71544239ec7dc`, not `847`). I thought it was a little better to do it this way; in any case not all films have URLs. 

Miscellany
----------

**Why are there 12 film columns? Isn't the ballot only 10 films long?** 

As a matter of fact two lucky directors, Martin Scorsese and Quentin Tarantino, got to cast a ballot of 12. Nothing like scraping web data to find random irregularities in it. 

**There are some typos! And "Africa" isn't a "country."** 

Yes, I know - just going with whatever is on the BFI's website...

**How do I get this into a spreadsheet?** 

You can dump the data into CSV files with the SQLite commands: 

    .mode csv
    .output films.csv
    SELECT * from films;
    .output voters.csv
    SELECT * from voters;
    .output stdout  -- to switch it back, in case you forget

There are probably also a number of applications/add-ins out there that will read an SQLite database straight into your favorite spreadsheet program more cleanly. 

To-do
-----

If I'm feeling ambitious about this, at some point I may try to link the titles up with a movie data API (probably Rotten Tomatoes; I don't think IMDb offers an API) to make better analysis easier. 
