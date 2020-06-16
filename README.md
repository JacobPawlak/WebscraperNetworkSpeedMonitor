# WebscraperNetworkSpeedMonitor
A cheeky little way to check the difference between network speed given by fast.com and the system, then chart it over in google sheets or something


what ill be doing here is comparing the stated network speed from fast.com (attained via webscraper) with the network speed given to me by the system. I really want to keep this monitored over time, so ideally i will send this to like a google sheet and track it in a csv file as well (if you cant tell, i like redundancy at the expense of storage. storage is cheap, backups are priceless!)

Okay so today (the 15th) i started and finished the data collection part, and i decided to make a seperate script to send stuff from csv to google drive. i want to keep the first script as lean as possible so it takes less than a minute (i want the cron scheduler to run min). I feel like i should also add I am doing this as a pro-bono project for my apt complex, using this script to test the network connection over the 'ISP recommended router'.