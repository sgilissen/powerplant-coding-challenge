"""
merit.py
Library to calculate merit plan for the powerplant coding challenge
"""
import pandas
import logging
import pprint


class MeritOrder:
    def __init__(self, payload):
        self._payload = payload
        self._results = []  # Empty array for later usage

    def check_payload(self):
        try:
            # Check if the "load" value in the dict is a positive integer
            assert int(self._payload['load']) > 0, 'No load requested or load value invalid'

            # Check if there are positive rates for fuels provided as float
            fuels = self._payload['fuels']
            assert float(fuels['gas(euro/MWh)']) >= 0.0, 'Gas fuel value is invalid'
            assert float(fuels['kerosine(euro/MWh)']) >= 0.0, 'Kerosine fuel value is invalid'
            assert float(fuels['co2(euro/ton)']) >= 0.0, 'co2 fuel value is invalid'
            assert float(fuels['wind(%)']) >= 0.0, 'Wind fuel value is invalid'

            # Check if values for power plants provided are valid
            pplants = self._payload['powerplants']
            for plant in pplants:
                assert(0.0 <= float(plant['efficiency']) <= 1.0), 'Plant efficiency is invalid'
                assert(int(plant['pmax']) >= 0.0), 'Plant pmax is invalid'
                assert(int(plant['pmin']) >= 0.0), 'Plant pmin is invalid'
                assert(len(plant['name']) > 0), 'Plant name is invalid'
                assert(len(plant['type']) > 0), 'Plant type is invalid'

            logging.info(f'Payload JSON is valid.')
            return True
        except AssertionError as e:
            logging.error(f'Invalid payload: {e}')
            return False

    def calculate(self):
        if self.check_payload:
            # Payload is valid
            logging.info(f'Payload JSON is valid.')

            # Set up fuel cost definitions
            fuel_defs = {
                'gasfired': self._payload['fuels']['gas(euro/MWh)'],
                'turbojet': self._payload['fuels']['kerosine(euro/MWh)'],
                'windturbine': 0.0   # Wind turbines do not generate fuel costs
            }

            # Set up CO2 definitions
            co2_defs = {
                'gasfired': 0.3,
                'turbojet': 0.0,
                'windturbine': 0.0
            }

            # Set up wind values. Only wind turbines are affected,
            # others are always 100% as they're not affected by wind
            wind_vals = {
                'gasfired': 100.0,
                'turbojet': 100.0,
                'windturbine': self._payload['fuels']['wind(%)']
            }

            # Set up Pandas dataframe for power plants and map values
            power_plants = pandas.DataFrame(data=self._payload['powerplants'])
            power_plants['target_load'] = self._payload['load']
            power_plants['wind_pct'] = power_plants['type'].map(wind_vals)
            power_plants['fuel_cost_mwh'] = power_plants['type'].map(fuel_defs)
            power_plants['co2_cost_mwh'] = power_plants['type'].map(co2_defs)

            # Calculations
            # Wind-powered power plants are 100% efficient. We get a value of 1.0 on these plants,
            # so we can calculate the netto efficiency by multiplying the values with the wind percentage
            power_plants['effc_netto'] = power_plants['efficiency'] * power_plants['wind_pct']
            # Calculate netto pmin/pmax per mwh.
            power_plants['pmin_netto_mwh'] = (power_plants['pmin'] * power_plants['effc_netto'])
            power_plants['pmax_netto_mwh'] = (power_plants['pmax'] * power_plants['effc_netto'])
            # Calculate netto fuel cost per mwh with efficiency in mind
            power_plants['cost_mwh_netto'] = (power_plants['fuel_cost_mwh'] /
                                              power_plants['effc_netto']) + power_plants['co2_cost_mwh']
            # Units in MW
            power_plants['max_produced'] = power_plants['pmax_netto_mwh'] / 0.1
            power_plants['min_produced'] = power_plants['pmin_netto_mwh'] / 0.1
            power_plants['target_produced'] = power_plants['target_load'] / 0.1

            # Sorting, first by cheapest netto cost per mwh, then by maximum production, then by minimum production
            power_plants.sort_values(
                by=['cost_mwh_netto', 'max_produced', 'min_produced'], inplace=True, ascending=[True, False, False]
            )

            # Calculate if plant should be committed.
            # Production target in MW
            target_produced = power_plants['target_produced'][0]
            for row in power_plants.iterrows():
                row_data = row[1]
                commission = (
                    row_data.pmax_netto_mwh if target_produced > row_data.pmax_netto_mwh
                    else max(target_produced, row_data.pmin_netto_mwh)
                ) / 100

                self._results.append({
                    'name': row[1]['name'],
                    'p': float(commission)
                })
            return self._results

        else:
            return {}

