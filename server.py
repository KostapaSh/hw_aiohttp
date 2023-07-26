from aiohttp import web
from models import Session, Base, engine, Advert
import json
from sqlalchemy.exc import IntegrityError


app = web.Application()


async def orm_context(app):
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print('SHUT DOWN')


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)



async def get_advert(advert_id: int, session: Session) -> Advert:
    advert = await session.get(Advert, advert_id)
    if advert is None:
        raise web.HTTPNotFound(
            text=json.dumps({'error': 'advert not found'}),
            content_type='application/json'
        )
    return advert


class AdvertView(web.View):

    @property
    def get_session(self) -> Session:
        print('session: ', self.request['session'])
        return self.request['session']

    @property
    def advert_id(self) -> int:
        print('advert_id: ', self.request.match_info['advert_id'])
        return int(self.request.match_info['advert_id'])

    async def get(self):
        advert = await get_advert(self.advert_id, self.get_session)
        return web.json_response({
            "id": advert.id,
            "title": advert.title,
            "description": advert.description,
            # "creation_date": advert.creation_date.strftime("%m.%d.%y"),
            "creation_date": int(advert.creation_date.timestamp()),
            "owner": advert.owner
        })

    async def post(self):
        json_data = await self.request.json()
        advert = Advert(**json_data)
        self.get_session.add(advert)
        try:
            await self.get_session.commit()
        except IntegrityError as er:
            raise web.HTTPConflict(
                text=json.dumps({'error': 'exists'}),
                content_type='application/json',
            )
        return web.json_response({
            'id': advert.id,
            'title': advert.title
        })

    async def delete(self):
        advert = await get_advert(self.advert_id, self.get_session)
        await self.get_session.delete(advert)
        await self.get_session.commit()
        return web.json_response({
            "status": "deleted",
            'id': advert.id,
            'title': advert.title
        })


app.add_routes([
    web.get('/adverts/{advert_id:\\d+}/', AdvertView),
    web.post('/adverts/', AdvertView),
    web.delete('/adverts/{advert_id:\\d+}/', AdvertView),
])


if __name__ == '__main__':
    web.run_app(app)
