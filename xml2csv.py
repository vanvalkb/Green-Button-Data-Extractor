# xml format testing

import glob
from bs4 import BeautifulSoup
import datetime
import csv
import os
from tqdm import tqdm

dir = os.getcwd()

def xml2csv(file):
    with open(file) as fp:
        soup = BeautifulSoup(fp,"html.parser")

    bowl = soup.find_all('entry')
    for x in bowl: 
        a = x.find('interval')
        if a == None:
            pass
        else:
            # Finds all of the interval reading data points
            b = x.find_all('intervalreading')
            # Gets title information for the meter and extracts the address for file namimg
            csv_name = x.title.string
            csv_name = csv_name.replace('Usage for Meter: ','')
            replace_idx = csv_name.index('-')
            csv_name = csv_name.replace(csv_name[replace_idx:],'')
            csv_name = csv_name.replace(' ','_')
            if csv_name[-1] == '_':
                csv_name = csv_name[:-1]

            # Finds start date information for data set
            start_time = int(a.start.text)
            data_time = int(b[0].start.text) - start_time
            day_s = 86400
            # Gets start time for file naming
            start_date = datetime.date.fromtimestamp(start_time+36000)
            mon_yr = get_date(start_date)
            dir = os.getcwd()
            des_dir = dir + '\\' + csv_name
            if not os.path.exists(des_dir):
                os.makedirs(des_dir)
            csv_name = des_dir+'\\'+csv_name +'_'+mon_yr+'.csv'
        

            with open(csv_name,'w', newline='') as csvfile:
                filewriter = csv.writer(csvfile, delimiter = ',', quotechar ='|', quoting=csv.QUOTE_MINIMAL)

                for x in range(len(b)):
                    # Gets the correct date in Unix data (Epoch/Posix) then turns it into calander date.
                    # 36000 applies correction to Eastern Time
                    unix_date = float(b[x].start.text)+36000
                    old_unix_date = float(b[x-1].start.text)+36000
                    # This will be used to compare the days of the current and the past point
                    act_date = datetime.date.fromtimestamp(unix_date)
                    old_date = datetime.date.fromtimestamp(old_unix_date)
            
                    # Gets the usage and converts from Wh to kWh
                    usage = float(b[x].value.text)/1000
                    # Adds the duration to the time.  If it goes greater than 1 day, it resets it to 0.
                    # Gets the lenth of the interval, so it should work for any interval data.
                    dur = float(b[x].duration.text)
            
                    # Finds the time of day for that point by taking the current time and dividing by secs in a day
                    # If the current date and previous date aren't the same, it resets the time to 0. This skips the first point.
                    if act_date != old_date and x!=0:
                        data_time = 0
                    time = data_time/day_s
                    # Once time is found, it adds the duration to the next point.
                    data_time += dur
                

                    # Gets data to outport then writes the next row of the .csv    
                    out_data=[act_date,time,usage]
                    filewriter.writerow(out_data)    

# Gives you the date for a given data point
def get_date(point):
    # Gets any day infomation from the point
    date_info = datetime.date.timetuple(point)
    # Makes the Month index and Day index start at 0.
    year = str(date_info[0])[2:]
    m_idx = date_info[1] - 1
    Months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    # Gets month
    month = Months[m_idx]
    date = month+year
    # Spits out month and day.
    return date


# Finds all files in the directory above that end in .xml. Then loops through them all running xml2csv() 
# and then deletes old .xml file.
files = glob.glob(dir +'/*.xml')
print('Converting {0} .xml files into .csv'.format(len(files)))
print()
print('Progress:')
for x in tqdm(files):
    xml2csv(x)
    os.remove(x)    
print()
print('Conversion complete')    
