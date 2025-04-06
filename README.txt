This is the live version of the website. 

1 - Install requirements. Then, run : playwright install
2 - Update BASE_DIR in polymkt_id_data_scrapper.sh 
3 - Run webapp.py
4 - Crontab on "bash polymkt_id_data_scrapper.sh us-recession-in-2025"

Should work from there. 

Possible improvements :

- Rely on Python more for the extraction of data by also using the api directly.
- Improve the look and functionnality of the website.
- Allow for market slug id search.
