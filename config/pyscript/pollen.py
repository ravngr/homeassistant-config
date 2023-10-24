from datetime import datetime

from bs4 import BeautifulSoup
import aiohttp


_POLLEN_URL = 'https://www.melbournepollen.com.au/'


@service
def update_pollen_forecast():
    """yaml
name: Update pollen forecast
description: Scrape melbournepollen.com.au and update pollen and thunderstorm asthema sensors.
"""
    async with aiohttp.ClientSession() as session:
        async with session.get(_POLLEN_URL) as resp:
            pollen_dom = BeautifulSoup(resp.text(), 'html.parser')

    # Extract forecast date
    date_node = pollen_dom.find('div', {'id': 'pdate'})
    forecast_date = datetime.strptime(date_node.text, '%A, %B %d, %Y').date()

    log.debug(f"Forecast date: {forecast_date}")

    # Extract forecast cells by looking for forecast values (shared between pollen and TA)
    for value_node in pollen_dom.find_all('div', {'class': 'forecast-value'}):
        # Get region by looking for the parent row, then drilling down to the 'day' node
        row_node = value_node.find_parent('div', {'class': 'ta-forecast-cell'})
        region_node = row_node.find('div', {'class': 'forecast-day'})
        region_entity_name = region_node.text.lower().replace(' ', '_')

        # TA cells begin with a common prefix
        if any([name.startswith('tae-level-') for name in value_node['class']]):
            log.debug(f"TA Forecast: {region_node.text} = {value_node.text}")

            state.set(
                f"sensor.thunderstorm_asthma_level_{region_entity_name}",
                value_node.text,
                {
                    'date': forecast_date,
                    'friendly_name': f"{region_node.text} Thunderstorm Asthma Forecast",
                    'icon': 'mdi:flower-pollen-outline',
                    'region': region_node.text
                }
            )
        else:
            log.debug(f"Pollen Forecast: {region_node.text} = {value_node.text}")

            state.set(
                f"sensor.pollen_level_{region_entity_name}",
                value_node.text,
                {
                    'date': forecast_date,
                    'friendly_name': f"{region_node.text} Pollen Forecast",
                    'icon': 'mdi:flower-pollen',
                    'region': region_node.text
                }
            )
