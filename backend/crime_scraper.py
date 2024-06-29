import re
import requests
import pdfplumber
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime

def download_pdf(url, output_path):
    response = requests.get(url)
    with open(output_path, 'wb') as file:
        file.write(response.content)
    print("----------------------------------------------------------------------")
    print(f"Downloaded PDF from {url} to {output_path}")
    print("----------------------------------------------------------------------")

def parse_crime_log(pdf_path):
    crime_logs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                headers = table[0]
                for row in table[1:]:
                    log_entry = dict(zip(headers, row))
                    crime_logs.append(log_entry)
    return crime_logs

def get_60_day_crime_log_url():
    url = "https://dps.usc.edu/alerts/log/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    link = soup.find('a', string='60 Day Crime & Fire Log')
    if link:
        pdf_url = link['href']
        return pdf_url
    return None

def clean_crime_logs(crime_logs):
    cleaned_logs = []
    for log in crime_logs:
        cleaned_log = {}
        for key, value in log.items():
            value = value.replace('\n', ' ')
            value = re.sub(' +', ' ', value).strip()
            if key in ['Date Reported', 'Date From', 'Date To']:
                value = re.sub(r'(\d{2})/(\d{2})/(\d{2})', r'\1/\2/20\3', value)
            cleaned_log[key] = value
        if cleaned_log['Offense'] == '':
            cleaned_log['Offense'] = 'N/A'
        if cleaned_log['Case #'] == '':
            cleaned_log['Case #'] = 'N/A'
        cleaned_logs.append(cleaned_log)
    return cleaned_logs

def normalize_street_name(location):
    location = location.upper()
    location = re.sub(r'\bST\b', 'Street', location)
    location = re.sub(r'\bAV\b', 'Avenue', location)
    location = re.sub(r'\bBLVD\b', 'Boulevard', location)
    location = re.sub(r'\bDR\b', 'Drive', location)
    location = re.sub(r'\bRD\b', 'Road', location)
    location = re.sub(r'\bPL\b', 'Place', location)
    location = re.sub(r'\bLN\b', 'Lane', location)
    location = re.sub(r'[^a-zA-Z0-9 ,]', '', location)  # Remove special characters except hyphen and comma
    return location.strip()

def split_and_normalize_location(location):
    if '-' in location or ',' in location:
        streets = re.split(r'[-,]', location)
        normalized_streets = [normalize_street_name(street.strip()) for street in streets]
        return normalized_streets
    else:
        return [normalize_street_name(location)]

def categorize_crime(offense):
    offense_capitalized = offense
    offense = offense.lower()
    
    if any(keyword in offense for keyword in ['theft', 'burglary', 'robbery', 'motor vehicle theft']):
        return 'Theft'
    if any(keyword in offense for keyword in ['burglary', 'invasion']):
        return 'Burglary'
    if any(keyword in offense for keyword in ['vandalism', 'damage', 'arson']):
        return 'Property Damage'
    if any(keyword in offense for keyword in ['assault', 'battery', 'homicide']):
        return 'Physical Violence'
    if any(keyword in offense for keyword in ['murder', 'homicide']):
        return 'Murder'
    if any(keyword in offense for keyword in ['disorderly conduct', 'noise']):
        return 'Disorderly Conduct'
    if 'trespass' in offense:
        return 'Property Trespass'
    if 'criminal threats' in offense:
        return 'Criminal Threats'
    if 'fraud' in offense:
        return 'Fraud'
    if 'drug' in offense:
        return 'Drug-Related'
    if 'traffic' in offense:
        return 'Traffic Incidents'
    if 'fire' in offense:
        return 'Fire Incidents'
    if 'hazard' in offense:
        return 'Environmental Hazards'
    if any(keyword in offense for keyword in ['sexual', 'indecent', 'lewd']):
        return 'Sexual Offenses'
    if 'domestic' in offense:
        return 'Domestic Issues'
    if any(keyword in offense for keyword in ['property', 'recovered', 'lost', 'missing']):
        return 'Property Issues'
    if 'administrative' in offense or 'warrant' in offense or 'incident report' in offense:
        return 'Administrative'
    if any(keyword in offense for keyword in ['harassment', 'stalking', 'hate', 'obscene']):
        return 'Harassment'
    
    return offense_capitalized

def organize_data(crime_logs):
    organized_data = defaultdict(lambda: defaultdict(int))
    for log in crime_logs:
        if 'NON-REPORTABLE LOCATION' not in log['Location']:
            locations = split_and_normalize_location(log['Location'])
            crime_category = categorize_crime(log['Offense'])
            if crime_category != 'N/A':
                for street in locations:
                    organized_data[street][crime_category] += 1
    return organized_data

def main():
    crime_log_url = get_60_day_crime_log_url()
    if crime_log_url:
        output_path = "60_day_crime_log.pdf"
        download_pdf(crime_log_url, output_path)
        try:
            crime_logs = parse_crime_log(output_path)
            cleaned_logs = clean_crime_logs(crime_logs)
            organized_data = organize_data(cleaned_logs)

            print("Organized Crime Data:")
            for street in sorted(organized_data.keys()):
                crimes = organized_data[street]
                print(f"{street}: {dict(crimes)}")
            print("----------------------------------------------------------------------")
        except pdfplumber.pdfminer.PDFSyntaxError:
            print("Failed to parse the PDF. No valid PDF available.") 
    else:
        print("No valid URL found for the 60 Day Crime & Fire Log.")

main()