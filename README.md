# eCommerce-Restock-Scraper

Originally made for my girlfriend to check when item restocked, as the sites own notification service did not work.

website_parser() function will scrape the website and check if it is sold out or not.
new_estimated_date() function can be used for websites that show a restock date. Can be used to check that and let you know beforehand the date it will restock.

Contains 2 txt files and 1 web scraping script.
1. Replace the url in function execute_scrape() with desired url for product you want to check.
2. Use inspect element on product page to find element you want to check and write it in.
3. Edit in your own email and password.


## Setup
Clone the repo, fill in url, html tag you need to scrape and email and password to email yourself when it is restocked.
I used crontab to automate it to check at 12pm, 4pm and 8pm.

For Macs:
Go to terminal and enter: crontab -e
Depending on which editor is your default, (you may need to configure it), enter the time that you want the program to run and the command to execute your code.
Below is a guide on how to set the time.

### Crontab Guide

Follows the format: * * * * *  command_to_execute

First asterix is minute (0 - 59).

Second asterix is hour (0 - 23).

Third asterix is day of month (1 - 31).

Fourth asterix is month (1 - 12).

Fifth asterix is day of week (0 - 6) (Sunday to Saturday; 7 is also Sunday on some systems)

For example in your editor after typing crontab -e:
0 12,16,20 * * * /usr/local/bin/python3 ~/Desktop/scrape.py
runs the program at 12:00, 16:00 and 20:00 everyday of every month every day of the week.

Can also view this great [crontab guide youtube tutorial](https://www.youtube.com/watch?v=QZJ1drMQz1A)!

That's all you need! The program will only email you if the stock is available, but not if it is still unavailable. That way you won't be spammed everyday!
