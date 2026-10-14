"""
TV3 - Room & Match
RoomManager: Quản lý nhiều phòng song song, thread-safe.
"""
from __future__ import annotations

import threading
import uuid
from typing import Dict, List, Optional

from .errors import (
    ALREADY_IN_ROOM,
    INVALID_STATE,
    NOT_HOST,
    NOT_IN_ROOM,
    ROOM_FULL,
    ROOM_NOT_FOUND,
    SPECTATOR_FORBIDDEN,
    RoomError,
)
from .models import Role, Room, RoomStatus


class RoomManager:
    """Quản lý nhiều phòng song song; thread-safe vì server đa luồng."""

    def __init__(self) -> None:
        self._rooms: Dict[str, Room] = {}
        self._user_room: Dict[str, str] = {}   # username -> room_id
        self._lock = threading.RLock()

    # ---- helpers
    def _get(self, room_id: str) -> Room:
        room = self._rooms.get(room_id)
        if room is None:
            raise RoomError(ROOM_NOT_FOUND, f"Không có phòng {room_id}")
        return room

    # ---- tạo / vào / rời
    def create_room(self, host: str, name: str = "", time_limit: int = 30) -> Room:
        with self._lock:
            if host in self._user_room:
                raise RoomError(ALREADY_IN_ROOM)
            room = Room(
                room_id=uuid.uuid4().hex[:6].upper(),
                host=host,
                name=name or f"Phòng của {host}",
                time_limit=time_limit,
            )
            room.players[Role.PLAYER_X] = host     # chủ phòng cầm X (có thể random)
            self._rooms[room.room_id] = room
            self._user_room[host] = room.room_id
            return room

    def join_as_player(self, room_id: str, username: str) -> Role:
        with self._lock:
            room = self._get(room_id)
            if username in self._user_room:
                raise RoomError(ALREADY_IN_ROOM)
            if room.status != RoomStatus.WAITING or room.is_full():
                raise RoomError(ROOM_FULL)
            room.players[Role.PLAYER_O] = username
            room.status = RoomStatus.READY
            self._user_room[username] = room_id
            return Role.PLAYER_O

    def join_as_spectator(self, room_id: str, username: str) -> Role:
        """Vào xem giữa trận cũng được; TV5 sẽ gửi full GameState sau đó."""
        with self._lock:
            room = self._get(room_id)
            if username in self._user_room:
                raise RoomError(ALREADY_IN_ROOM)
            room.spectators.append(username)
            self._user_room[username] = room_id
            return Role.SPECTATOR

    def leave_room(self, username: str) -> dict:
        """Trả về thông tin để TV5 broadcast: role đã rời, phòng còn không."""
        with self._lock:
            room_id = self._user_room.get(username)
            if room_id is None:
                raise RoomError(NOT_IN_ROOM)
            room = self._get(room_id)
            role = room.role_of(username)
            del self._user_room[username]

            if role == Role.SPECTATOR:
                room.spectators.remove(username)       # không ảnh hưởng trận
                return {"room_id": room_id, "role": role, "match_aborted": False,
                        "room_closed": False}

            # người chơi rời
            del room.players[role]
            aborted = room.status == RoomStatus.PLAYING
            if aborted:
                # TV4/TV5 xử lý: đối thủ thắng do đối phương rời trận
                room.status = RoomStatus.FINISHED
            elif room.status == RoomStatus.READY:
                room.status = RoomStatus.WAITING

            closed = not room.players
            if closed:
                for s in room.spectators:
                    self._user_room.pop(s, None)
                room.status = RoomStatus.CLOSED
                del self._rooms[room_id]
            elif room.host == username:
                room.host = next(iter(room.players.values()))  # chuyển chủ phòng
            return {"room_id": room_id, "role": role, "match_aborted": aborted,
                    "room_closed": closed}

    # ---- vòng đời trận (TV4 gọi/được gọi qua các hàm này)
    def start_match(self, room_id: str, requester: str) -> Room:
        with self._lock:
            room = self._get(room_id)
            if requester != room.host:
                raise RoomError(NOT_HOST)
            if room.status != RoomStatus.READY:
                raise RoomError(INVALID_STATE, "Cần đủ 2 người chơi")
            room.status = RoomStatus.PLAYING
            return room

    def finish_match(self, room_id: str) -> Room:
        with self._lock:
            room = self._get(room_id)
            if room.status != RoomStatus.PLAYING:
                raise RoomError(INVALID_STATE)
            room.status = RoomStatus.FINISHED
            return room

    def rematch(self, room_id: str) -> Room:
        with self._lock:
            room = self._get(room_id)
            if room.status != RoomStatus.FINISHED or not room.is_full():
                raise RoomError(INVALID_STATE)
            # đổi quân X/O cho công bằng
            room.players[Role.PLAYER_X], room.players[Role.PLAYER_O] = (
                room.players[Role.PLAYER_O], room.players[Role.PLAYER_X])
            room.status = RoomStatus.READY
            return room

    # ---- truy vấn
    def get_room(self, room_id: str) -> Room:
        with self._lock:
            return self._get(room_id)

    def room_of(self, username: str) -> Optional[Room]:
        with self._lock:
            rid = self._user_room.get(username)
            return self._rooms.get(rid) if rid else None

    def list_rooms(self, only_playing: bool = False) -> List[dict]:
        """Room List; only_playing=True -> danh sách trận để khán giả vào xem."""
        with self._lock:
            rooms = self._rooms.values()
            if only_playing:
                rooms = [r for r in rooms if r.status == RoomStatus.PLAYING]
            return [r.to_summary() for r in rooms]

    def validate_move_permission(self, username: str, room_id: str) -> None:
        """Server gọi trước khi chuyển nước đi cho TV4 -> chặn khán giả."""
        with self._lock:
            room = self._get(room_id)
            if room.role_of(username) is None:
                raise RoomError(NOT_IN_ROOM)
            if not room.can_move(username):
                raise RoomError(SPECTATOR_FORBIDDEN)
            if room.status != RoomStatus.PLAYING:
                raise RoomError(INVALID_STATE)