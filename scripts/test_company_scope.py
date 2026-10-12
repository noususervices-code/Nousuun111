import unittest
from unittest.mock import patch

from scout_companies import creative_sector, fetch_listing_details


class CompanyScopeTests(unittest.TestCase):
    def test_named_creative_businesses(self):
        cases = {
            "Valokuvausstudio": "Valokuvaus",
            "Strateginen viestintätoimisto": "Viestintä",
            "Mainostoimisto": "Mainostoimisto",
            "Musiikkituotanto": "Musiikki",
            "AV-tuotanto": "Audiovisuaalinen tuotanto",
            "Muotoilutoimisto": "Muotoilu",
            "Pelinkehitys": "Pelit",
            "Taidegalleria": "Taide",
            "Kustannustoiminta": "Kustantaminen",
            "Mediayhtiö": "Media",
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(creative_sector({"name": name}), expected)

    def test_generic_businesses_do_not_qualify(self):
        for name in ["Verkkokauppa", "Ohjelmistoyhtiö ICT", "Huoltopalvelu", "Siivouspalvelut", "Maahantuonti", "Markkinointi", "Sosiaalinen media", "Terveyspalvelut", "Suunnittelu ja tekninen kauppa", "Pelien verkkokauppa"]:
            with self.subTest(name=name):
                self.assertIsNone(creative_sector({"name": name}))

    def test_beauty_overrides_creative_sector_everywhere(self):
        excluded = ["kauneus", "kosmetologi", "kosmetiikka", "kauneuskirurgia", "estetiikka", "esteettiset hoidot", "beauty", "cosmetics", "aesthetic clinic", "Botox", "täyteainehoito", "plastiikkakirurgia", "kampaamo"]
        for word in excluded:
            for field in ["name", "industry", "description", "url", "insight"]:
                with self.subTest(word=word, field=field):
                    item = {"name": "Valokuvausstudio", "industry": "Mainostoimisto"}
                    item[field] = word
                    self.assertIsNone(creative_sector(item))
            with self.subTest(word=word, field="detail page"):
                self.assertIsNone(creative_sector({"name": "Valokuvausstudio"}, word))

    def test_encoded_excluded_url_is_rejected(self):
        self.assertIsNone(creative_sector({"name": "Valokuvausstudio", "url": "https://example.org/%6bosmetologi"}))

    def test_broad_creative_category_does_not_qualify_generic_business(self):
        self.assertIsNone(creative_sector({"name": "Valmistaja ja tukkumyyjä", "industry": "Maahantuonti, Mainostoimisto, markkinointi, Muu valmistava teollisuus"}))
        self.assertIsNone(creative_sector({"name": "Tunnettu verkkosivusto", "industry": "ATK-ohjelmointi, Kustannustoiminta, Mainostoimisto, markkinointi, Verkkokauppa"}))

    def test_related_listings_do_not_contaminate_source_details(self):
        page = "Myynnin aihe Myydään Toimiala Valokuvaus Hintapyyntö 1000 EUR Pyydä lisätietoja kohteesta Suositukset: Kauneusklinikka"
        with patch("scout_companies.urlopen") as request:
            request.return_value.__enter__.return_value.read.return_value = page.encode("utf-8")
            details = fetch_listing_details("https://www.yrityskaupat.net/fi/myytava-yritys/studio/")
        self.assertEqual(creative_sector({"name": "Valokuvausstudio"}, details), "Valokuvaus")

    def test_generic_and_external_urls_are_not_verifiable(self):
        for url in ["https://www.yrityskaupat.net/fi/myytavat-yritykset/", "https://example.org/fi/myytava-yritys/studio/"]:
            with self.subTest(url=url), patch("scout_companies.urlopen") as request:
                with self.assertRaises(ValueError):
                    fetch_listing_details(url)
                request.assert_not_called()

    def test_unconfirmed_page_is_not_verifiable(self):
        with patch("scout_companies.urlopen") as request:
            request.return_value.__enter__.return_value.read.return_value = b"<h1>Not found</h1>"
            with self.assertRaises(ValueError):
                fetch_listing_details("https://www.yrityskaupat.net/fi/myytava-yritys/studio/")


if __name__ == "__main__":
    unittest.main()
