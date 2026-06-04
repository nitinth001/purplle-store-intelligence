from shapely.geometry import Point, Polygon

QUEUE_ZONE = Polygon([
    (650, 120),
    (980, 120),
    (980, 760),
    (650, 760)
])

BILLING_ZONE = Polygon([
    (250, 180),
    (650, 180),
    (650, 760),
    (250, 760)
])

def in_queue(x, y):
    return QUEUE_ZONE.contains(Point(x, y))

def in_billing(x, y):
    return BILLING_ZONE.contains(Point(x, y))