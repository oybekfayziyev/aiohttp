import logging
from main import web
from app.utils import jwt_encrypt, jwt_decrypt
from app.models import User, Event, Coupon
from aiohttp_pydantic import PydanticView
from app.serializers import (
    TokenObtainSerializer,
    UserCreateSerializer,
    EventCreateSerializer,
    CouponSerializer,
)

logging.basicConfig(level=logging.DEBUG)


# Account Views
class TokenObtainApiView(PydanticView):
    async def get(self):

        authorization = self.request.headers.get("Authorization", "")
        if not authorization:
            return web.json_response({"data": "Authentication is required"}, status=401)

        token_type = authorization.split(" ")[0]
        if token_type != "Bearer":
            return web.json_response(
                {"data": "Bearer authentication is allowed"}, status=400
            )

        token = authorization.split(" ")[1]
        decoded = jwt_decrypt(token)
        user = await User.get_user_by_username(decoded["user"]["username"])
        del user["timestamp"]
        return web.json_response(user)

    async def post(self, token: TokenObtainSerializer):

        username = token.username
        password = token.password
        user = await User.get_user_by_username(username)
        if not User().check_password(password, user["password"]):
            return web.json_response({"data": "Password is incorrect"}, status=400)
        del user["password"]
        del user["token"]
        del user["timestamp"]
        token = jwt_encrypt({"user": user})
        user["token"] = token
        return web.json_response(user)


class UserApiView(PydanticView):
    async def post(self, user: UserCreateSerializer):
        data = await user.save(user.dict())
        data = data[0]
        del data["timestamp"]
        return web.json_response(data)


async def get_users_events(request):
    user_events = await Coupon.get_users_coupons()
    res = {}
    for item in user_events:
        item = dict(item)
        del item["total_events"]
        res.setdefault(item["user"], []).append(item)
    return web.json_response(res)


# Event Views
class EventListApiView(PydanticView):
    async def get(self):
        events = await Event.get_events()
        return web.json_response(events)

    async def post(self, event: EventCreateSerializer):
        event = await Event().create_event(event.dict())
        return web.json_response(event)


async def retrieve_event(request):
    event_id = str(request.rel_url).split("/")[-1]
    event = await Event.get_event_by_id(int(event_id))
    return web.json_response(event)


async def get_events_list(request):
    events = await Coupon.get_events_list()
    res = {}
    for item in events:
        item = dict(item)
        item["date"] = str(item["date"])
        res.setdefault(item["title"], []).append(item)
    return web.json_response(res)


# Coupon Views
class CouponApiView(PydanticView):
    async def get(self):
        user = self.request.user
        coupons = await Coupon.get_user_coupons(user["id"])

        return web.json_response(coupons)

    async def post(self, coupon: CouponSerializer):
        coupon = await Coupon().create_coupon(coupon.user, coupon.event)
        return web.json_response(coupon)
