This version is made to run on Windows, it should refresh the data by itself, everytime the website refreshes but it might not work. If you want to update teh data manually (the site will load it), run "bash polymkt_id_data_scrapper.sh us-recession-in-2025".

1 - Install requirements. Then, run : playwright install
2 - Update BASE_DIR in polymkt_id_data_scrapper.sh
3 - Run webapp.py
4 - Go to "http://0.0.0.0:8050/"

Should work from there. 

What remains to do :

- (Medium - Important) Make sure the daily report works : Update the .py script to make it do stats on data that is at maximum 24hours in the past (so that it works now, with less data).
- (Easy - Less important) More statistics ? At least more coherent ones, for example we should display the ending condition of the bet (available in the scrapped data).
- (Easy - Less important) Make the site look better, don't really care but shouldn't be that hard.
- (Hard - Not important but cool) add a slug research bar : Takes a slug in argument, loads the data and displays it.

Don't forget that it needs to work on Linux after, that will be my problem but still (don't mess with the procedure to make the site run too much, if at all :) ).
