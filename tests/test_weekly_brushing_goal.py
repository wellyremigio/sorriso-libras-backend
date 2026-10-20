"""Exercise the real weekly-goal service and repositories without MongoDB."""
import copy
import unittest
from datetime import date
from types import SimpleNamespace

from bson import ObjectId
from fastapi import HTTPException

from app.repositories.sticker_gallery_repository import StickerGalleryRepository
from app.schemas.brushing_goal_schema import BrushingGoalCompleteResponse
from app.services.brushing_goal_services import BrushingGoalService, DAYS_OF_WEEK, VALID_SHIFTS


class MemoryCursor:
    def __init__(self, documents):
        self.documents = copy.deepcopy(documents)

    def sort(self, field, direction):
        self.documents.sort(key=lambda item: item[field], reverse=direction < 0)
        return self

    async def to_list(self, length):
        return self.documents[:length]


class MemoryCollection:
    def __init__(self):
        self.documents = []

    @staticmethod
    def matches(document, query):
        return all(document.get(key) == value for key, value in query.items())

    async def find_one(self, query):
        return next((copy.deepcopy(doc) for doc in self.documents if self.matches(doc, query)), None)

    def find(self, query):
        return MemoryCursor([doc for doc in self.documents if self.matches(doc, query)])

    async def insert_one(self, document):
        document = copy.deepcopy(document)
        document.setdefault('_id', ObjectId())
        self.documents.append(document)
        return SimpleNamespace(inserted_id=document['_id'])

    async def update_one(self, query, update):
        document = next(doc for doc in self.documents if self.matches(doc, query))
        document.update(copy.deepcopy(update['$set']))


class MemoryDatabase(dict):
    def __missing__(self, key):
        collection = self[key] = MemoryCollection()
        return collection


class WeeklyBrushingGoalTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.database = MemoryDatabase()
        self.service = BrushingGoalService(self.database)
        # Sunday allows all 21 checks; this does not change the machine clock.
        self.service._get_current_week_range = lambda: (date(2026, 10, 19), date(2026, 10, 25))
        self.service._get_current_day_index = lambda: 6
        self.child_id = 'isolated_weekly_goal_test'
        await self.database['stickers'].insert_one({
            'name': 'Adesivo semanal de teste', 'module': 'children',
            'image_url': 'https://example.test/sticker.png',
            'unlock_condition': 'weekly_brushing_goal',
            'is_active': True, 'is_special': False,
        })

    async def mark_checks(self, count):
        slots = [(day, shift) for day in DAYS_OF_WEEK for shift in VALID_SHIFTS]
        for day, shift in slots[:count]:
            await self.service.update_check(self.child_id, day, shift, True)

    async def test_all_21_checks_award_a_sticker_saved_in_gallery(self):
        await self.mark_checks(21)
        result = await self.service.complete_current_goal(self.child_id)
        BrushingGoalCompleteResponse.model_validate(result)
        self.assertTrue(result['completed'])
        self.assertEqual(result['goal']['total_completed'], 21)
        self.assertEqual(len(result['earned_stickers']), 1)
        self.assertIsNotNone(result['goal']['completed_at'])
        gallery = await StickerGalleryRepository(self.database).find_child_stickers(self.child_id)
        self.assertEqual(gallery[0]['id'], result['earned_stickers'][0]['id'])
        self.assertEqual(gallery[0]['earned_reason'], 'weekly_brushing_goal')

    async def test_incomplete_goal_returns_message_and_no_sticker(self):
        await self.mark_checks(20)
        result = await self.service.complete_current_goal(self.child_id)
        BrushingGoalCompleteResponse.model_validate(result)
        self.assertFalse(result['completed'])
        self.assertIn('não completou a meta semanal', result['message'])
        self.assertEqual(result['earned_stickers'], [])
        self.assertIsNone(result['goal']['completed_at'])
        self.assertEqual(self.database['child_stickers'].documents, [])

    async def test_repeated_completion_does_not_duplicate_sticker(self):
        await self.mark_checks(21)
        await self.service.complete_current_goal(self.child_id)
        result = await self.service.complete_current_goal(self.child_id)
        self.assertTrue(result['completed'])
        self.assertEqual(result['earned_stickers'], [])
        self.assertEqual(len(self.database['child_stickers'].documents), 1)

    async def test_future_day_cannot_be_checked(self):
        self.service._get_current_day_index = lambda: 1  # Tuesday
        with self.assertRaises(HTTPException) as caught:
            await self.service.update_check(self.child_id, 'Dom', 'night', True)
        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(self.database['weekly_brushing_goals'].documents, [])


if __name__ == '__main__':
    unittest.main()
