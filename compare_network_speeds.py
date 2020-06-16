#Jacob Pawlak
#compare_network_speeds.py
#june 13th, 2020
#goooo blue team!

#################### IMPORTS ####################

#importing selenium and bs4 for webscraping
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#other helper libraries for system calls and stuff
import subprocess
import os
import time
import datetime

#################### HELPERS ####################

#I pulled this directly from the python selenium docs because it was EXACTLY what i needed lmao
#i want to use this for the fast.com's spinner icon, since i know the upload speed wont be availble until the the spinner is done or 'succeeded'
#hell yeah over and over, thank you selenium docs <3
class element_has_css_class(object):
  """An expectation for checking that an element has a particular css class.
  locator - used to find the element
  returns the WebElement once it has the particular css class
  """
  def __init__(self, locator, css_class):
    self.locator = locator
    self.css_class = css_class

  def __call__(self, driver):
    # Finding the referenced element
    element = driver.find_element(*self.locator)
    if self.css_class in element.get_attribute("class"):
        return element
    else:
        return False

#this helper funtion webscrapes fast.com to get the download and upload speed (fast.com is pretty unbiased for a browser tool) and returns the speeds in megabytes
def grab_fast_com_speed():

    #just like we would set up any of our selenium scrapes, gotta include the path to the chromedriver
    driver = webdriver.Chrome('./Chrome/83/chromedriver')
    #and open the target site in a browser
    driver.get('https://fast.com')
    #wait for the page to load for 10 seconds (fast.com is pretty fast and light so it loads much quicker than that)
    driver.implicitly_wait(10)

    #just to wrap the scrape in a guard like usual, try except clause it out
    try:
        #setting up some speed variables here, init at -1 so i know if there is an error loading the page or connecting, or if the speed is actually 0.
        fast_adjusted_download = -1
        fast_adjusted_upload = -1
        #so the page loads really quickly, but the speedtest doesnt start right away, so the window will close if you just check for DOM loaded, instead
        # what i have to do is check for something on the website to change or load or something, so after tinkering around on the site for a little bit i 
        # noticed that there is a showmore button that pops up after the test runs (more later), so we just need to check that the button is visible before we move on
        try:
            show_more_btn = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "show-more-details-link")))
            #grab the page source and then find the elements corresponding to the download speed and units
            soup = BeautifulSoup(driver.page_source, 'html5lib')
            fast_download = float(soup.find('div', attrs={'id': 'speed-value'}).text)
            fast_d_units = soup.find('div', attrs={'id': 'speed-units'}).text
        except:
            soup = BeautifulSoup(driver.page_source, 'html5lib')
            fast_download = float(soup.find('div', attrs={'id': 'speed-value'}).text)
            fast_d_units = soup.find('div', attrs={'id': 'speed-units'}).text
        #now we gotta click the show more button to get to the upload speed test (then let the page load for a sec)
        show_more_btn = driver.find_element_by_id('show-more-details-link')
        show_more_btn.click()
        time.sleep(1)
        #now, once you click the show more button, the upload tests starts - this will take a little bit of time and its not really a predictable range. 
        # What we are looking for in this case is the little spinner icon to go from orange spinning to green success. we will watch for that using the class
        # made at the top of the HELPERS section. Edit: i really only want to do this if we have connection (a speed above 0), no need to waste time
        if(fast_download != 0):
            try:
                #same way we watched for the button to appear, we are waiting for the spinner to add the 'succeeded' class, which makes the spinner green
                spinnerbar = WebDriverWait(driver, 20).until(element_has_css_class((By.ID, 'speed-progress-indicator'), 'succeeded'))
                #once we have found the green spinner, we are going to re-scrape the page and find the upload speed
                soup = BeautifulSoup(driver.page_source, 'html5lib')
                fast_upload = float(soup.find('span', attrs={'id': 'upload-value'}).text)
                fast_u_units = soup.find('span', attrs={'id': 'upload-units'}).text
            #in the wacky case that the upload test takes too long and out wait times out, or the page breaks for some reason we are just going to try to grab 
            # whatever the test is currently clocking in at
            except:
                soup = BeautifulSoup(driver.page_source, 'html5lib')
                fast_upload = float(soup.find('span', attrs={'id': 'upload-value'}).text)
                fast_u_units = soup.find('span', attrs={'id': 'upload-units'}).text
        #after testing, found out that if there is no connection, i still need to have the fast_u_units or else i get the unbound local var error. 
        # so this is just clean up, i dont want to take up the extra space by initing it at the top like the speeds
        else:
            fast_u_units = ""

        #these next two chunks are here to normalize the speeds to Megabytes per second, or adjust the speed back to -1 if there were errors in the page scrape
        #this first one is for the download speed
        if(fast_d_units == 'Mbps'):
            fast_adjusted_download = fast_download
        elif(fast_d_units == 'Kbps'):
            fast_adjusted_download = fast_download * .001
        elif(fast_d_units == 'Gbps'):
            fast_adjusted_download = fast_download * 1000
        elif(fast_d_units == 'Bytes'):
            fast_adjusted_download = fast_download * .000001
        else:
            fast_adjusted_download = -1
        #and this is for the upload speed
        if(fast_u_units == 'Mbps'):
            fast_adjusted_upload = fast_upload
        elif(fast_u_units == 'Kbps'):
            fast_adjusted_upload = fast_upload * .001
        elif(fast_u_units == 'Gbps'):
            fast_adjusted_upload = fast_upload * 1000
        elif(fast_u_units == 'Bytes'):
            fast_adjusted_upload = fast_upload * .000001
        else:
            fast_adjusted_upload = -1

    #there are a few errors that could be thrown during this but the most likely would be a timeout error on the wait statements
    except Exception as err:
       print("Oh no! we ran into a little timeout error {}".format(err))

    #at the end we need to close the driver so it doesnt take up the memory. it is chrome afterall. 
    finally:
        driver.quit()

    return (fast_adjusted_download, fast_adjusted_upload)


#this helper function is using the speedtest cli tool to grab the network speed. it returns the download and upload speed in megabytes
def grab_sys_speed():

    #setting the variables here like i did in the fast.com helper
    sys_adjusted_download = -1
    sys_adjusted_upload = -1
    #same kinda thing, we are going to wrap the test in a try/except clause 
    try:
        #for this test, we are going to issue a command to the system to run the cli speedtest tool, and then record the results
        #i found the outline for subprocess.check_output on some stackoverflow, and have modified it to fit my needs 
        result = str(subprocess.check_output("speedtest", shell=True))
        #so speetest cli returns some output that looks like you would expect - a few lines of preamble, some loading ... and then the numbers 
        # which are burried in there a few lines down. after plaing around with the cli i know which lines are in there - i can think of 
        # a few other ways to do this but this is honestly the simplest way imo
        res_list = result.split('\\n')
        #each of the two lines looks like: 'Up/Download: 100.0 Mbit/s'
        sys_download = res_list[6].split()[1]
        sys_d_units = res_list[6].split()[2]
        sys_upload = res_list[8].split()[1]
        sys_u_units = res_list[8].split()[2]

        #noramlizing here again to the Megabytes unit since that is pretty standard for speeds
        if(sys_d_units == 'Mbit/s'):
            sys_adjusted_download = sys_download
        elif(sys_d_units == 'Kbit/s'):
            sys_adjusted_download = sys_download * .001
        elif(sys_d_units == 'Gbit/s'):
            sys_adjusted_download = sys_download * 1000
        elif(sys_d_units == 'Bit/s'):
            sys_adjusted_download = sys_download * .000001
        else:
            sys_adjusted_download = -1
        #same here for upload speed
        if(sys_u_units == 'Mbit/s'):
            sys_adjusted_upload = sys_upload
        elif(sys_u_units == 'Kbit/s'):
            sys_adjusted_upload = sys_upload * .001
        elif(sys_u_units == 'Gbit/s'):
            sys_adjusted_upload = sys_upload * 1000
        elif(sys_u_units == 'Bit/s'):
            sys_adjusted_upload = sys_upload * .000001
        else:
            sys_adjusted_upload = -1

    #same error handling (or lack there of - we either get the numbers, or an error means no connection so its nbd)
    except Exception as err:
        print("Oh no! we ran into a little error {}".format(err))

    return (sys_adjusted_download, sys_adjusted_upload)


#pretty simple little function to write out the data to our csv file, or create the file if it is not there. this should run once every time this file is run
def write_out_to_csv(date, data_list):

    #first, gotta check to see if the csv is there or not, and if not then we need to create the csv
    if(not os.path.exists('CSVs/{}.csv'.format(date))):
        with open('CSVs/{}.csv'.format(date), 'w') as outfile:
            #if we dont see that file in our directory we are going to make one and add the header at the top
            outfile.write('start_time,fast_download,fast_upload,sys_download,sys_upload,run_time,download_diff_percent,upload_diff_percent,outage_detected\n')
            outfile.write(','.join(map(str, data_list)) + '\n')
    #if we do find the file then we know it okay to just append the next row
    else:
        with open('CSVs/{}.csv'.format(date), 'a') as outfile:
            outfile.write(','.join(map(str, data_list)) + '\n')

    return

#################### MAIN () ####################

def main():

    #i want to track the total runtime of the program just as another datapoint, so im setting up a datetime timer
    start_time = datetime.datetime.now()

    #now it's time to call the fast.com speed helper function, and pull out the down and up speeds
    fast_adjusted_speeds = grab_fast_com_speed()
    #since we wrote the function, we know that the returned value is a tuple of (down, up)
    fast_download = float(fast_adjusted_speeds[0])
    fast_upload = float(fast_adjusted_speeds[1])

    #now we want to grab the speed from the system call helper function - it has the same return structure as the fast.com one
    sys_adjusted_speeds = grab_sys_speed()
    sys_download = float(sys_adjusted_speeds[0])
    sys_upload = float(sys_adjusted_speeds[1])

    #this is calculating the total time ran in seconds
    run_time = float((datetime.datetime.now() - start_time).seconds)

    #now to set that start to a human-readible format
    date_file_name = start_time.strftime("%m-%d-%Y")
    start_time = start_time.strftime("%m-%d-%Y %H:%M:%S")

    #now just for funsies i am going to calulate the difference in the two different up and down stats
    #if one of the speeds fails or doesnt exist, then we dont want to take the difference in values
    if( not (fast_download == -1 or sys_download == -1) ):
        #the easy formula im using is just ( |n1 - n2| / (.5 * (n1 + n2)) ) * 100
        download_diff_percent = round((abs(fast_download - sys_download) / ((fast_download + sys_download)/2)) * 100, 4)
        upload_diff_percent = round((abs(fast_upload - sys_upload) / ((fast_upload + sys_upload)/2)) * 100, 4)
    else:
        #we can just set these to -1 like the others
        download_diff_percent = -1
        upload_diff_percent = -1

    #setting up a little flag here to check for outages (defined as both speeds are -1)
    outage_detected = False
    if( fast_download == -1 and fast_upload == -1 and sys_download == -1 and sys_upload == -1 ):
        outage_detected = True

    #the last thing to do is to write the data to our csv file and to the standard output in the terminal
    write_out_to_csv(date_file_name, [start_time, fast_download, fast_upload, sys_download, sys_upload, run_time, download_diff_percent, upload_diff_percent, outage_detected])
    print(start_time, fast_download, fast_upload, sys_download, sys_upload, run_time, download_diff_percent, upload_diff_percent, outage_detected)

main()