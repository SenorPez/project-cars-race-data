from glob import glob
from racedata.RaceData import RaceData
import sys
import logging

log_file = 'racedata-0.1/outputs/log.out'
logging.basicConfig(filename=log_file, level=logging.DEBUG)

#for directory in glob('assets/race111/'):
for directory in glob('assets/race*'):
    logging.debug('Processing: '+directory)

    file_name = directory.split('/')[1]
    try:
        data = RaceData(directory, descriptor_filename='racedata.json')
        name_length = max([len(x) for x in data._current_drivers.keys()])
        data.get_all_data()
        with open('racedata-0.1/outputs/'+file_name+'.txt', 'w') as fp:
            fp.write("{}.txt\n".format(file_name))
            for entry in sorted(data.classification, key=lambda x: x.race_position):
                output = "{entry.race_position:>2} {entry.driver.name:{name_length}} {entry.driver.laps_complete:>3} {entry.driver.race_time:>9.3f} {entry.driver.best_lap:>9.3f} {entry.driver.best_sector_1:>9.3f} {entry.driver.best_sector_2:>9.3f} {entry.driver.best_sector_3:>9.3f}\n".format(entry=entry, name_length=name_length)
                fp.write(output)
    except:
        logging.exception('Error')
