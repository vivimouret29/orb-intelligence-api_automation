#!/usr/bin/python

import sys
import pandas as pd
import numpy as np
import requests as rq
import json
import time


class OrbNumApi():

    def __init__(self, data, debug):
        self.geoname, self.iteration, self.debug = data, 0, debug
        self.df, self.datamissed = pd.DataFrame(
            []), pd.DataFrame([], columns=['api_link'])
        self.api_key = 'c66c5dad-395c-4ec6-afdf-7b78eb94166a'
        self.naics, self.sic = 511210, 7372
        self.company, self.country, self.revenue = 'company', 'UnitedStates', '0-1m'
        self.offset, self.round, self.zip = 0, 0, 0

    def __enter__(self):
        self.cleaning(self.geoname)
        self.analysis(self.geoname)
        self.run()

    def __exit__(self):
        print('\nStoping OrbApi Python')
        quit()

    def stored_data(self):
        if self.datamissed.empty == True:
            self.df = self.df.append(
                {'api_link': 'No links registered'}, ignore_index=True)

        final_data = self.df[['zip', 'address1', 'city', 'company_status', 'entity_type', 'fetch_url', 'is_standalone_company', 'api_link', 'full_profile.email',
                              'full_profile.description', 'full_profile.employees', 'full_profile.employees_range', 'full_profile.industry',
                              'full_profile.facebook_account.url', 'full_profile.linkedin_account.url', 'full_profile.twitter_account.url',
                              'full_profile.last_funding_round_amount', 'full_profile.naics_code', 'full_profile.sic_code',
                              'full_profile.names', 'full_profile.orb_num', 'full_profile.revenue', 'full_profile.revenue_range',
                              'full_profile.total_funding', 'full_profile.webdomain', 'full_profile.website',
                              'full_profile.technologies', 'full_profile.year_founded']]

        print('\n----------------------------------------------------------------------------\n'
              '|-----------------------------//FINAL OUTPUT\\\-----------------------------|\n'
              '----------------------------------------------------------------------------\n'
              f'{final_data}')

        final_data.to_csv(rf'lib/orbnum_api_{self.iteration}it.csv',
                          sep=',', index=True)
        print(f'Data saved as \'orbnum_api_{self.iteration}it.csv\'')

        self.__exit__()

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

        except print(f'Error during data cleaning'):
            return

        self.geoname = data
        self.iteration = self.geoname['zip'].nunique()
        # self.iteration = 100

    def analysis(self, data):
        return print('\n',
                     pd.DataFrame(
                         {'Data Type': data.dtypes, 'Unique Count': data.apply(lambda x: x.nunique(), axis=0),
                          'Null Count': data.isnull().sum()}))

    def run(self):
        print(f'\nStart {self.iteration} Iteration\n')
        start_time = time.perf_counter()

        while self.round+1 <= self.iteration:
            self.zip = self.geoname['zip'].values[self.round]
            self.zip = f'0{self.zip}' if (len(self.zip) == 4) else self.zip

            print(f'Iteration {self.round+1}/{self.iteration}')
            self.offset = 0

            while self.offset < 110:
                link = f'https://api.orb-intelligence.com/3/search/?api_key={self.api_key}&offset={self.offset}'\
                    f'&entity_type={self.company}&zip={self.zip}&country={self.country}'\
                    f'&employees=1-10&employees=10-50&revenue={self.revenue}'\
                    f'&naics_codes={self.naics}&show_full_profile={True}'

                try:
                    response = rq.get(link)
                    data = response.json()
                except print(f'Error GET api w {link}'):
                    self.__enter__()

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
                        f'error: result {counting} maximum possible numbers')
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
                        f'{counting} unlisted lines were saved in a link')

                if counting < 0:
                    time.sleep(1)
                    break

                self.offset += 10
                time.sleep(1)

            self.round += 1

        stop_time = time.perf_counter()
        print(f'Iterations made in {stop_time - start_time:0.4f} seconds')

        if self.df.empty == False:
            self.stored_data()
        else:
            print(f'No data recorded')


if __name__ == '__main__':
    df = pd.read_csv(r'geonames-postal-code.csv')
    debug = False if len(sys.argv) == 1 else bool(sys.argv[1])

    with OrbNumApi(df, debug) as orbapi:
        orbapi
