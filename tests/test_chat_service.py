import unittest

from app.services.chat_service import ChatService
from app.services.location_service import LocationService


class ChatServiceTests(unittest.TestCase):
    def test_tourism_recommendation_uses_location_fallback(self) -> None:
        service = ChatService()
        try:
            location_context, post_context = service._build_context("서울에서 가장 유명한 관광지 추천해줘")
        finally:
            service.close()

        self.assertGreater(len(location_context), 0)
        self.assertLessEqual(len(location_context), 5)
        self.assertEqual(location_context[0]["category"], "관광지")
        self.assertIsInstance(post_context, list)

    def test_category_recommendations_use_matching_location_fallback(self) -> None:
        cases = [
            ("서울 레포츠 추천해줘", "레포츠"),
            ("서울 문화시설 알려줘", "문화시설"),
            ("서울에서 가볼만한 문화시설 추천해줘", "문화시설"),
            ("서울 쇼핑할 곳 추천해줘", "쇼핑"),
            ("서울 숙박 추천해줘", "숙박"),
            ("서울 여행코스 추천해줘", "여행코스"),
            ("서울 축제 행사 알려줘", "축제공연행사"),
        ]
        service = ChatService()
        try:
            for message, expected_category in cases:
                with self.subTest(message=message):
                    location_context, _ = service._build_context(message)

                    self.assertGreater(len(location_context), 0)
                    self.assertEqual(location_context[0]["category"], expected_category)
        finally:
            service.close()


class LocationServiceTests(unittest.TestCase):
    def test_default_data_dir_loads_seoul_json_files(self) -> None:
        response = LocationService().get_locations(category="관광지", limit=3)

        self.assertEqual(len(response.items), 3)
        self.assertGreater(response.total, 3)
        self.assertEqual(response.items[0].category, "관광지")


if __name__ == "__main__":
    unittest.main()
