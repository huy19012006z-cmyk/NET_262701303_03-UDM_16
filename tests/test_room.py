"""
TV3 - Room & Match
Unit Test cho module Room & Match (Giai đoạn 2).
"""
import unittest

from server.room import (
    ALREADY_IN_ROOM,
    NOT_HOST,
    ROOM_FULL,
    ROOM_NOT_FOUND,
    SPECTATOR_FORBIDDEN,
    Role,
    RoomError,
    RoomManager,
    RoomStatus,
)


class TestRoom(unittest.TestCase):
    def setUp(self):
        self.m = RoomManager()
        self.r = self.m.create_room("an")

    def test_create_assigns_x_to_host(self):
        self.assertEqual(self.r.players[Role.PLAYER_X], "an")
        self.assertEqual(self.r.status, RoomStatus.WAITING)

    def test_join_makes_ready(self):
        self.assertEqual(self.m.join_as_player(self.r.room_id, "binh"), Role.PLAYER_O)
        self.assertEqual(self.r.status, RoomStatus.READY)

    def test_room_full(self):
        self.m.join_as_player(self.r.room_id, "binh")
        with self.assertRaises(RoomError) as c:
            self.m.join_as_player(self.r.room_id, "chi")
        self.assertEqual(c.exception.code, ROOM_FULL)

    def test_cannot_join_twice(self):
        with self.assertRaises(RoomError) as c:
            self.m.join_as_spectator(self.r.room_id, "an")
        self.assertEqual(c.exception.code, ALREADY_IN_ROOM)

    def test_unknown_room(self):
        with self.assertRaises(RoomError) as c:
            self.m.join_as_player("XXXXXX", "binh")
        self.assertEqual(c.exception.code, ROOM_NOT_FOUND)

    def test_only_host_starts(self):
        self.m.join_as_player(self.r.room_id, "binh")
        with self.assertRaises(RoomError) as c:
            self.m.start_match(self.r.room_id, "binh")
        self.assertEqual(c.exception.code, NOT_HOST)

    def test_spectator_cannot_move(self):
        self.m.join_as_player(self.r.room_id, "binh")
        self.m.join_as_spectator(self.r.room_id, "chi")
        self.m.start_match(self.r.room_id, "an")
        with self.assertRaises(RoomError) as c:
            self.m.validate_move_permission("chi", self.r.room_id)
        self.assertEqual(c.exception.code, SPECTATOR_FORBIDDEN)

    def test_spectator_leave_does_not_affect_match(self):
        self.m.join_as_player(self.r.room_id, "binh")
        self.m.join_as_spectator(self.r.room_id, "chi")
        self.m.start_match(self.r.room_id, "an")
        info = self.m.leave_room("chi")
        self.assertFalse(info["match_aborted"])
        self.assertEqual(self.r.status, RoomStatus.PLAYING)

    def test_player_leave_aborts_match(self):
        self.m.join_as_player(self.r.room_id, "binh")
        self.m.start_match(self.r.room_id, "an")
        info = self.m.leave_room("binh")
        self.assertTrue(info["match_aborted"])

    def test_multiple_rooms_independent(self):
        r2 = self.m.create_room("dung")
        self.assertEqual(len(self.m.list_rooms()), 2)
        self.assertNotEqual(self.r.room_id, r2.room_id)

    def test_list_only_playing(self):
        self.m.join_as_player(self.r.room_id, "binh")
        self.m.start_match(self.r.room_id, "an")
        self.m.create_room("dung")
        self.assertEqual(len(self.m.list_rooms(only_playing=True)), 1)


if __name__ == "__main__":
    unittest.main()