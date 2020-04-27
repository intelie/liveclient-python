from unittest import mock
import queue


class ChatMock:
    def __init__(self):
        self.room = {"users": {}}

    def update_room(self, event):
        for user in event.get("removedUsers", []):
            removed_user = self.room["users"].pop(user["id"], None)

        for user in event.get("addedOrUpdatedUsers", []):
            self.room["users"][user["id"]] = user

    def add_user(self, user):
        self.room["users"][user["id"]] = user


# [ECS]: "patch_with_factory" is not the best name for this function
# The intention here is to provide a simple way to return a function that when
# called will return the desired object. I'm calling such function a "factory"
# but it may be misleading for people comming from other contexts.
# While we don't come up with a better name, let's use this.
def patch_with_factory(target, obj, *args, **kwargs):
    return mock.patch(target, lambda *a, **kws: obj, *args, **kwargs)


class MPQueue(queue.Queue):
    def close(*args, **kwargs):
        pass
