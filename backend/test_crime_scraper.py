import unittest
from unittest.mock import patch, mock_open, MagicMock
from io import BytesIO
import pdfplumber
import requests
from datetime import datetime

# Import functions from your scraper script
from crime_scraper import download_pdf, parse_crime_log, get_daily_crime_log_url

class TestPDFScraper(unittest.TestCase):
    @patch('requests.get')
    def test_download_pdf(self, mock_get):
        url = "https://example.com/daily_crime_log.pdf"
        output_path = "test.pdf"
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'%PDF-1.4\n...'
        mock_get.return_value = mock_response

        with patch('builtins.open', mock_open()) as mocked_file:
            download_pdf(url, output_path)
            mocked_file.assert_called_once_with(output_path, 'wb')
            mocked_file().write.assert_called_once_with(mock_response.content)

    @patch('pdfplumber.open')
    def test_parse_crime_log(self, mock_open_pdf):
        mock_pdf = MagicMock()
        mock_open_pdf.return_value = mock_pdf
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = [
            [
                ["Date Reported", "Event #", "Case #", "Offense", "Initial Incident", "Final Incident", "Date From", "Date To", "Location", "Disposition"],
                ["06/19/24 - WED\nat 19:47", "24-06-19-180489", "", "", "LA MUNICIPAL CODE -Loud\nand Raucous Noise", "LA MUNICIPAL CODE - Loud\nand Raucous Noise", "06/19/24 - WED\nat 19:47", "06/19/24 - WED\nat 19:47", "2600 Block Of MAGNOLIA AV\n- Non-reportable location", "UNABLE TO LOCATE -\nGONE ON ARRIVAL"]
            ]
        ]
        mock_pdf.pages = [mock_page]

        logs = parse_crime_log("dummy_path")
        self.assertEqual(len(logs), 1)
        self.assertIn("Offense", logs[0])
        self.assertEqual(logs[0]["Offense"], "")

    @patch('crime_scraper.datetime')
    def test_get_daily_crime_log_url(self, mock_datetime):
        mock_datetime.today.return_value = datetime(2024, 6, 14)
        mock_datetime.strftime = datetime.strftime
        url = get_daily_crime_log_url()
        expected_url = "https://dps.usc.edu/wp-content/uploads/2024/06/06142024.pdf"
        self.assertEqual(url, expected_url)
