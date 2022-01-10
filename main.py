#!/usr/bin/python

import os
import sys
import pandas as pd
import numpy as np
import requests as rq
import json
import time


class OrbNumApi():

    def __init__(self, debug):
        self.geoname, self.iteration, self.debug = pd.DataFrame([]), 0, debug
        self.df, self.datamissed = pd.DataFrame(
            []), pd.DataFrame([], columns=['api_link'])
        self.backup = 500
        self.api_key = 'c66c5dad-395c-4ec6-afdf-7b78eb94166a'
        self.naics, self.sic = 511210, 7372
        self.company, self.country, self.revenue = 'company', 'UnitedStates', '0-1m'
        self.info, self.offset, self.round, self.zip = 0, 0, 0, 0

    def __enter__(self):
        print(f'{self.output_info()} INFO: Orb Api Automation')
        self.find_csv()
        self.cleaning(self.geoname)
        self.analysis(self.geoname)
        self.run()

    def __exit__(self):
        print(f'{self.output_info()} INFO: Stoping OrbApi Python')
        quit()

    def cleaning(self, data):
        try:
            drop = np.where(data['postal code'] == 'NY')
            drop += np.where(data['postal code'] == '501')
            drop += np.where(data['postal code'] == '544')

            i = 0
            while i < 3:
                data = data.drop(index=drop[i], axis=1)
                i += 1

            data = data.rename(columns={'postal code': 'zip',
                                        'place name': 'city', 'admin name1': 'state'})

        except print(f'{self.output_info()} ERROR: Failure of data cleaning, please do it yourself'):
            return

        self.geoname = data
        self.iteration = self.geoname['zip'].nunique()

    def output_info(self):
        if type(self.info) == int:
            self.info += 1
        elif type(self.info) == str:
            self.info = int(self.info) + 1

        if len(str(self.info)) == 1:
            self.info = f'00{self.info}'
        elif len(str(self.info)) == 2:
            self.info = f'0{self.info}'

        return self.info

    def find_csv(self):
        for dirname, _, filenames in os.walk(r'.'):
            for filename in filenames:
                print(os.path.join(dirname, filename)) if self.debug else None
                if filename.endswith('.csv'):
                    self.geoname = pd.read_csv(filename)
                    return print(
                        f'{self.output_info()} INFO: Read the csv file {filename}')

    def analysis(self, data):
        return print(f'{self.output_info()} INFO:\n',
                     pd.DataFrame(
                         {'Data Type': data.dtypes, 'Unique Count': data.apply(lambda x: x.nunique(), axis=0),
                          'Null Count': data.isnull().sum()}))

    def stored_data(self):
        if self.datamissed.empty == True:
            self.df = self.df.append(
                {'api_link': 'No links registered'}, ignore_index=True)

        data = self.df[['zip', 'address1', 'city', 'company_status', 'entity_type', 'fetch_url', 'is_standalone_company', 'api_link', 'full_profile.email',
                        'full_profile.description', 'full_profile.employees', 'full_profile.employees_range', 'full_profile.industry',
                        'full_profile.facebook_account.url', 'full_profile.linkedin_account.url', 'full_profile.twitter_account.url',
                        'full_profile.last_funding_round_amount', 'full_profile.naics_code', 'full_profile.sic_code',
                        'full_profile.names', 'full_profile.orb_num', 'full_profile.revenue', 'full_profile.revenue_range',
                        'full_profile.total_funding', 'full_profile.webdomain', 'full_profile.website',
                        'full_profile.technologies', 'full_profile.year_founded']]

        data.to_csv(rf'lib/orbnum_api_{self.round}it.csv',
                    sep=',', index=True)

        if self.round == self.iteration-1:
            print('\n---------------------------------------------------------------------------\n'
                  '|-----------------------------//DATA OUTPUT\\\-----------------------------|\n'
                  '---------------------------------------------------------------------------\n'
                  f'{data}'
                  f'\n{self.output_info()} INFO: Data saved as \'orbnum_api_{self.round}it.csv\'')

    def run(self):
        print(f'\n{self.output_info()} INFO: Starting {self.iteration} iteration\n')
        start_time = time.perf_counter()

        while self.round+1 <= self.iteration:
            self.zip = self.geoname['zip'].values[self.round]
            self.zip = f'0{self.zip}' if (len(self.zip) == 4) else self.zip

            print(
                f'{self.output_info()} INFO: Iteration {self.round+1}/{self.iteration}')
            self.offset = 0

            while self.offset < 110:
                link = f'https://api.orb-intelligence.com/3/search/?api_key={self.api_key}&offset={self.offset}'\
                    f'&entity_type={self.company}&zip={self.zip}&country={self.country}'\
                    f'&employees=1-10&employees=10-50&revenue={self.revenue}'\
                    f'&naics_codes={self.naics}&show_full_profile={True}'

                try:
                    response = rq.get(link)
                    data = response.json()
                except print(f'{self.output_info()} ERROR: api GET request ', 0):
                    time.sleep(5)
                    break

                if self.offset == 0:
                    counting = data['results_count']

                if counting == 0:
                    time.sleep(1)
                    break
                elif counting == 16695:
                    self.datamissed = self.datamissed.append(
                        {'api_link': link}, ignore_index=True)
                    self.df = self.df.append(
                        self.datamissed, verify_integrity=True, ignore_index=True)

                    print(
                        f'{self.output_info()} WARNING: Maximum numbers reached: {counting}')
                    time.sleep(1)
                    break
                elif self.offset <= 100:
                    print(json.dumps(data, sort_keys=True, indent=2)
                          ) if self.debug else None

                    dataJSON = pd.json_normalize(data['results'])

                    if self.df.empty:
                        self.df = pd.DataFrame(dataJSON)
                    else:
                        self.df = self.df.append(
                            dataJSON, verify_integrity=True, ignore_index=True)

                    counting -= 10
                    pd.io.json.build_table_schema(self.df)

                if self.offset == 100 and counting > 0:
                    self.datamissed = self.datamissed.append(
                        {'api_link': link}, ignore_index=True)
                    self.df = self.df.append(
                        self.datamissed, verify_integrity=True, ignore_index=True)
                    print(
                        f'{self.output_info()} WARNING: {counting} unlisted lines were saved in a link')

                if counting < 0:
                    time.sleep(1)
                    break

                self.offset += 10
                time.sleep(1)

            self.round += 1

            if self.round == self.backup:
                self.backup += 500
                self.stored_data()

        stop_time = time.perf_counter()
        print(
            f'{self.output_info()} INFO: Iterations made in {stop_time - start_time:0.4f} seconds')

        if self.df.empty == False:
            self.stored_data()
        else:
            print(f'{self.output_info()} ERROR: No data recorded')


if __name__ == '__main__':
    debug = False if len(sys.argv) == 1 else bool(sys.argv[2])

    with OrbNumApi(debug) as orbapi:
        orbapi