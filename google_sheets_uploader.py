#Jacob Pawlak
#google_sheets_uploader.py
#june 15th, 2020
#goooo blue team!

#################### IMPORTS ####################

#target libraries for the google sheet editing
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#other helper libraries for system calls and stuff
import subprocess
import os
import time
import datetime
import csv

#################### HELPERS ####################

#this helper function is really the meat of the script - it takes in a csv file and then pulls out all of the rows that arent the header (we formated the csv so we know it has the header),
# and then appends them to our google sheet.
def append_csv_to_sheet(csv_file):

    #i learned this is just something you have to do to set up the creds for the google sheets api connection
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.file']
    
    try:
        #setting up the creds from out super secret file
        creds = ServiceAccountCredentials.from_json_keyfile_name('google_auth.json', scope)
        client = gspread.authorize(creds)

        #grabbing the sheet that we need to open (the first sheet in the workbook/workbench whatever google calls it)
        net_speed_sheet = client.open('BML_Network_Speed_Records').sheet1

        #now we are going to open the csv file that was passed in to the function, and make a csv.reader object out of it (this object is like a list of lists, but not itterable... :P )
        with open('./CSVs/{}'.format(csv_file), 'r') as net_csv_file:
            net_csv_reader = csv.reader(net_csv_file)
            #this next line lets me skip over the header which we know is going to be in each new file at the top
            header = next(net_csv_reader)
            #as long as there was a header aka not an empty file, lets go ahead and append each line to the sheet
            if header != None:
                for net_speed_snapshot in net_csv_reader:
                    #print(net_speed_snapshot)
                    #this append_row method lets us place a row in the active range in the first empty row (no needing to count or anything upfront)
                    #i had to include that value_input_option because it was entering in all of the values with a ' infront of them, like '60.0 and '6-16-2020. for some reason that kwarg fixes it?
                    net_speed_sheet.append_row(net_speed_snapshot, value_input_option='USER_ENTERED')
                print("Added {} to the Google Sheet".format(csv_file))
            
            #if there are no rows after the header then we can just close out the file and leave with a little message
            else:
                print("Ooops, it looks like that file ({}) might have been empty or something... moving on.".format(csv_file))

    #this is really  here just to guard against a downed connection, i dont really want it to do anything if the connection breaks - it can try again next time
    except Exception as err:
        print("Shit, looks like the connection to google is down and you couldnt authenticate or add to the sheet. We will try again next time, the file isnt going to be moved. Error code: {}".format(err))
        return False

    return True

#a real quick and easy function to move one file to the 'Uploaded' folder
def move_to_uploaded(csv_file):

    #using the os library here to move the file to the uploaded folder
    try:
        os.replace('./CSVs/{}'.format(csv_file), './CSVs/Uploaded/{}'.format(csv_file))
    #just to save face incase something errs out
    except FileNotFoundError as err:
        print("Oh no, looks like that file doesnt exist in the CSVs directory. Please check the error message... {}".format(err))
    except Exception as err:
        print("Wow things really hit the fan huh.. if it wasnt a file error it must have been {}".format(err))
    
    return

#################### MAIN () ####################

def main():

    #since this will be run on a cron schedule i dont really care to look at the dates, we can just list the csvs dir and grab all of the file names in there
    files_to_upload = os.listdir('./CSVs')
    #for each file in there (hopefully we only have one file at a time, but this will work if there are multiple files)
    for csv_file in files_to_upload:
        #after doing some testing, it looks like the Uploaded directory gets returned in the listdir (duh why wouldnt it) so we are just going to skip over that one
        if(csv_file != 'Uploaded'):
            #here is another conditional, here i only want to move the file if the sheet was updated.
            if(append_csv_to_sheet(csv_file)):
                move_to_uploaded(csv_file)

main()