from app.views import (
    EventListApiView,
    UserApiView,
    TokenObtainApiView,
    retrieve_event,
    CouponApiView,
    get_users_events,
    get_events_list,
)


def path(app):
    # Account urls
    app.router.add_view("/api/v1/account/create", UserApiView)
    app.router.add_view("/api/v1/account/me", TokenObtainApiView)
    app.router.add_get("/api/v1/users/events", get_users_events)

    # Event
    app.router.add_view("/api/v1/events", EventListApiView)
    app.router.add_get(r"/api/v1/events/{event_id:\d+}", retrieve_event)
    app.router.add_get("/api/v1/events/list", get_events_list)

    # Coupon
    app.router.add_view("/api/v1/coupons", CouponApiView)
