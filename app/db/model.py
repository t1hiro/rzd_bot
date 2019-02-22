from datetime import datetime

from sqlalchemy import Column, Integer, String, create_engine, DateTime, Binary
from sqlalchemy.ext.declarative import declarative_base
from app.settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


class Subscribes(Base):
    __tablename__ = 'subscribes'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    route_from = Column(String, nullable=False)
    route_to = Column(String, nullable=False)
    route_date = Column(DateTime, nullable=False)
    seat_type = Column(String, nullable=True)
    created_dt = Column(DateTime, nullable=False, default=datetime.now())
    update_dt = Column(DateTime, nullable=False, default=datetime.now())
    notify = Column(Binary, nullable=False, default=0)

    def __repr__(self):
        return '<Subscribes {} {} {} {}>'.format(self.id, self.route_from, self.route_to, self.route_date)

    def save(self):
        session = Session()
        subscribe_exists = session.query(Subscribes).filter_by(chat_id=self.chat_id, route_from=self.route_from,
                                                               route_to=self.route_to,
                                                               route_date=self.route_date).first()
        if not subscribe_exists:
            self.created_dt = datetime.now()
            self.update_dt = datetime.now()
            session.add(self)
            session.commit()

    def update(self):
        session = Session()
        subscribe_exists = session.query(Subscribes).filter_by(chat_id=self.chat_id, route_from=self.route_from,
                                                               route_to=self.route_to,
                                                               route_date=self.route_date).first()
        if subscribe_exists:
            self.route_to = 'test'
            session.commit()
