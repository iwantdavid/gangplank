import json

import falcon
from gangplank.models import Event
from graceful.authorization import authentication_required

from .schema.event import EventSchema, CreateEventSchema


class EventsResource(object):
    def on_get(self, req, resp):
        events = Event.objects

        event_schema = EventSchema(many=True)
        result = event_schema.dump(events)

        resp.body = json.dumps({'results': result.data})

    @authentication_required
    def on_post(self, req, resp):
        create_schema = CreateEventSchema()
        result, error = create_schema.load(json.load(req.bounded_stream))
        if error:
            raise falcon.HTTPBadRequest('Missing data', error)

        context_user = {
            'id': req.context['user']['id'],
            'name': req.context['user']['name'],
        }

        event = Event(
            name=result['name'],
            start_date=result['start_date'],
            description=result['description'],
            creator=context_user,
        ).save()

        event_schema = EventSchema()
        event_result = event_schema.dump(event)

        resp.body = json.dumps(event_result.data)
        resp.status = falcon.HTTP_201
