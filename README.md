# ORB API v3.0


## From [Orb Api Schema](https://api.orb-intelligence.com/docs/)
Automates API queries on a dataset based on ZIP codes.  
Stores the results of API requests in a *.csv* file.  
A column with the link of the API request is provided, when the allowed offset is exceeded.  
Ability to display in **debugg mode** by placing `True` after the command call:

```bash
(env) $ python main.py True 
```

To avoid displaying **debugg mode**, do not add anything after the command, or `False`.  
We juste use data from [geonames-postal-code.csv](geonames-postal-code.csv)* for the moment.  

You can find the examples in the [lib](lib/) folder there.
  
**[source](https://data.opendatasoft.com/explore/dataset/geonames-postal-code%40public/export/?flg=fr&refine.country_code=US)*
___
## Code explanation
### Initialization
We work in a class called `OrbNumApi()`.  
First, when Python is launched, pandas reads the *.csv file*.  
Then, the **debugg** mode is set according to the `True` or `False` arguments selected.  
Finally, the `OrbNumApi()` class is executed.
```python
if __name__ == '__main__':
    df = pd.read_csv(r'geonames-postal-code.csv')
    debug = False if len(sys.argv) == 1 else bool(sys.argv[1])

    with OrbNumApi(df, debug) as orbapi:
        orbapi
```

### Constructors
The following constructors initialise the variables and the order of execution of the functions:
- `__init__`: initializes local variables
- `__enter__`: defines the order of execution of functions ; starts with `cleaning()`, followed by `analysis()` and ends with `run()`.
- `__exit__`: run at the end of the script
```python
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
```

### Data Backup
The main function of this function is to save all the data that has been recorded during the iterations.   
It's the last function called.
```python
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
```

### Cleaning
Functions specific to the *.csv* used for the demonstration.
The `cleaning()` function removes columns with outliers in the `'postal code'` column.  
The `analysis()` function returns to the terminal the results of values as :
- its type
- if it contains characters of any type
- the sum of the `Null` data
```python
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

def analysis(self, data):
        return print('\n',
                     pd.DataFrame(
                         {'Data Type': data.dtypes, 'Unique Count': data.apply(lambda x: x.nunique(), axis=0),
                          'Null Count': data.isnull().sum()}))
```

### The Execution
Main function of **`main.py`**.  
The parts are explained in the logical sequence of the function.  

- starts the function timer with `start_time` ; the main `while` loop is defined to run as many queries as there are columns containing valid zip code ; `stop_time` is created once the whole function finishes, then displayed the time taken in the terminal ; the `if` condition is created in the event that the array is empty so no saving is needed.
```python
print(f'\nStart {self.iteration} Iteration\n')
start_time = time.perf_counter()

while self.round+1 <= self.iteration:
    # more soon ...

stop_time = time.perf_counter()
print(f'Iterations made in {stop_time - start_time:0.4f} seconds')
if self.df.empty == False:
    self.stored_data()
else:
    print(f'No data recorded')
```

- defines the `self.zip` to be used on each iteration of the previous loop (if the zip code is only 4 digits long, a 0 is added at the beginning so that the search does not make an error) ; on the first iteration of the loop, `self. offset` is initialized to 0 ; the secondary loop `while` is defined to constantly send api requests with a different **offset** with conditions being defined in this loop ; once the secondary loop is finished, increment `self.round` with the value 1 (condition relative to the main loop)
```python
self.zip = self.geoname['zip'].values[self.round]
self.zip = f'0{self.zip}' if (len(self.zip) == 4) else self.zip

print(f'Iteration {self.round+1}/{self.iteration}')
self.offset = 0

while self.offset < 110:
    # more soon ...

self.round += 1
```

- `link` is a variable containing the values to be used in each request ; `try` allows the whole script to be restarted in case of an error / inside it runs the GET request to the api and stores the data in a `data` variable
```python
link = f'https://api.orb-intelligence.com/3/search/?api_key={self.api_key}&offset={self.offset}'\
    f'&entity_type={self.company}&zip={self.zip}&country={self.country}'\
    f'&employees=1-10&employees=10-50&revenue={self.revenue}'\
    f'&naics_codes={self.naics}&show_full_profile={True}'

try:
    response = rq.get(link)
    data = response.json()
except print(f'Error GET api w {link}'):
    self.__enter__()
```

- if `self.offset` is 0, the number of results is retrieved from `counting`, `counting` being an important variable
```python
if self.offset == 0:
    counting = data['results_count']
```

- if `counting` is equal to 0, no result so we exit the secondary loop ; if `counting` is equal to 16695, it is an error so the link used is recorded in a specific table ; if `self.offset` is less than or equal to 100, the *JSON* data is converted, recorded and normalized in a *pandas* array
```python
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
```

- this condition is used when the offset is fully used and there are still results, the API link is stored in a column of the table
```python
if self.offset == 100 and counting > 0:
    self.datamissed = self.datamissed.append(
        {'api_link': link}, ignore_index=True)
    self.df = self.df.append(
        self.datamissed, verify_integrity=True, ignore_index=True)
    print(
        f'{counting} unlisted lines were saved in a link')

```

- if `counting` is less than 0 - we deduce who was previously less than 10 - we exit the secondary loop 
```python
if counting < 0:
    time.sleep(1)
    break
```
