
from bs4 import BeautifulSoup
import hashlib
import re
import sqlite3
import urllib2


def scrapeFilms(url, conn, verbose=False):
    """
    Scrapes films from the URL (should be the full film list) and adds them to
    the database indicated by conn. 
    """
    
    print "Processing films..."
    
    c = conn.cursor()
    c.execute(r"DROP TABLE IF EXISTS films")
    c.execute(r"""CREATE TABLE films 
                  (id text, title text, url text, year integer, director text, 
                   country text)""")
    c.execute(r"""CREATE UNIQUE INDEX film_index 
                  ON films (title, year, director)""")
    conn.commit()
    
    soup = BeautifulSoup(urllib2.urlopen(url))
    film_blocks = soup.find_all("div", class_="sas-all-films-group")
    
    for film_block in film_blocks:
        film_rows = film_block.find("table").find_all("tr")
        for film_row in film_rows:
            
            # title is taken from the first <td>. film_url is pulled from the
            # hyperlink. year, director, and country are pulled from attributes 
            # of the <tr>. The year is stripped off of the name of the film 
            # (the titles all end in "(yyyy)" on the website). Not all films 
            # have urls or years. film_id is hashed from title, year, and 
            # director. If more than one country name was included, they are
            # separated by commas. 
            
            title = film_row.find("td").string.strip()
            year = film_row["data-year"].strip()
            if year == "": 
                year = ""
            else: 
                if re.search(r"\(" + year + r"\)$", title):
                    title = re.sub(r"\s*\(" + year + "\)$", "", title)
            
            # some fixes needed to director: spacing, different separators, and a
            # few manual fixes
            director = film_row["data-director"].strip()
            director = re.sub("\s", " ", director)
            director = re.sub(r"\/", r", ", director)
            director = re.sub(r"&", r", ", director)
            director = re.sub(r"\s+,", r",", director)
            director = re.sub(r"  +", " ", director)
            if director == "Joel, Ethan Coen":
                director = "Joel Coen, Ethan Coen"
            elif director == "Jim Abrahams, David, Jerry Zucker":
                director = "Jim Abrahams, David Zucker, Jerry Zucker"
                
            country = film_row["data-country"].strip()
            country = re.sub(r",\s+", ", ", country)
            try:
                film_url = film_row.find("td").find("a")["href"].strip()
            except TypeError:
                film_url = None
            film_id = hashlib.md5(",".join([title, year, director]).encode("utf-8")).hexdigest()
            
            if year == "": year = None
            if director == "": director = None
            if country == "": country = None
            
            c.execute(r"INSERT INTO films VALUES (?,?,?,?,?,?)", 
                      (film_id, title, film_url, year, director, country))
            conn.commit()
            if verbose: 
                if year == None: print "%s" % title
                else: print "%s (%s)" % (title, year)
    
    print "Films processed."
    c.close()


def scrapeVoters(url, conn, scrape_ballot=False, verbose=False):
    """
    Scrapes voter info from the URL (should be the full voter list) and adds
    them to the database indicated by conn. If scrape_ballot is True, also 
    runs scrapeBallot on each voter page. 
    """
    
    print "Processing voters..."
    
    c = conn.cursor()
    c.execute(r"DROP TABLE IF EXISTS voters")
    c.execute(r"""CREATE TABLE voters 
                  (id text, name text, url text, poll text, occupation text, 
                   sex text, country text, film_id1, film_id2, film_id3, 
                   film_id4, film_id5, film_id6, film_id7, film_id8, film_id9, 
                   film_id10, film_id11, film_id12)""")
    c.execute(r"""CREATE UNIQUE INDEX voter_index 
                  ON voters (name, poll, occupation, sex, country)""")
    conn.commit()
    
    soup = BeautifulSoup(urllib2.urlopen(url))
    voter_blocks = soup.find_all("div", class_="sas-all-films-group")
    
    for voter_block in voter_blocks:
        voter_rows = voter_block.find("table").find_all("tr")
        for voter_row in voter_rows:
            
            # name is taken from the first <td>. voter_url is pulled from the 
            # hyperlink. The other variables are conveniently found as 
            # attributes of the <tr>. voter_id is hashed from name, poll, 
            # occupation, sex, and country. 
            
            name = voter_row.find("td").string.strip()
            voter_url = voter_row.find("td").find("a")["href"].strip()
            poll = voter_row["data-poll"].strip()
            occupation = voter_row["data-category"].strip()
            sex = voter_row["data-gender"].strip()
            if sex == "Male": sex = "M"
            elif sex == "Female": sex = "F"
            else: sex = ""
            country = voter_row["data-country"].strip()
            voter_id = hashlib.md5(",".join([name, poll, occupation, sex, country]).encode("utf-8")).hexdigest()
            
            if poll == "": poll = None
            if occupation == "": occupation = None
            if sex == "": sex = None
            if country == "": country = None
            
            c.execute(r"INSERT INTO voters VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (voter_id, name, voter_url, poll, occupation, sex, country, 
                       None, None, None, None, None, None, None, None, None, None, None, None))
            conn.commit()
            if verbose: print "%s (%s)" % (name, occupation)
            
            if scrape_ballot:
                scrapeBallot(voter_url, conn, voter_id=voter_id, verbose=verbose)
    
    print "Voters processed."
    c.close()


def scrapeBallot(url, conn, voter_id, verbose=False):
    """
    Scrapes ballot info from the URL (should be one of the voters' ballot 
    pages) and adds it to the database indicated by conn, in the row indicated
    by voter_id. Only film_ids are added, so this is not useful unless you've
    also added film data to the db with scrapeFilms. 
    """
    
    c = conn.cursor()
    
    soup = BeautifulSoup(urllib2.urlopen(url))
    ballot_rows = soup.find("div", class_="sas-voter-details-votes").find("table").find_all("tr")
    if len(ballot_rows) > 12:
        raise Exception("More than 12 films on ballot " + url)
    
    film_ids = []
    for ballot_row in ballot_rows:
        ballot_cells = ballot_row.find_all("td")
        title = ballot_cells[0].string.strip()
        year = ballot_cells[1].string
        if year == None: year = ""
        else: year = year.strip()
        
        # some fixes needed to director: spacing, different separators, and a
        # few manual fixes
        director = ballot_cells[2].string.strip()
        director = re.sub("\s", " ", director)
        director = re.sub(r"\/", r", ", director)
        director = re.sub(r"&", r", ", director)
        director = re.sub(r"\s+,", r",", director)
        director = re.sub(r"  +", " ", director)
        if director == "Joel, Ethan Coen":
            director = "Joel Coen, Ethan Coen"
        elif director == "Jim Abrahams, David, Jerry Zucker":
            director = "Jim Abrahams, David Zucker, Jerry Zucker"
        
        film_id = hashlib.md5(",".join([title, str(year), director]).encode("utf-8")).hexdigest()
        film_ids.append(film_id)
    
    ballot_inserts = []
    for i in range(len(ballot_rows)):
        ballot_inserts.append("film_id" + str(i + 1) + " = ?")
    c.execute(r"UPDATE voters SET " + ",".join(ballot_inserts) + r"WHERE id = ?",
              film_ids + [voter_id])
    conn.commit()
    c.close()
    