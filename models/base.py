from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.types import String

from lib.store import engine
from lib.utils import jsonify


BaseModel = declarative_base(engine)


class ModelMixin:
    def __setattr__(self, key, value):
        # 当给 String 类型字段赋值时限制字符串的长度, 如 Column(String(20)) 中最长只能有 20 个字符.
        if isinstance(value, str):
            the_attribute = getattr(self.__class__, key, None)

            if isinstance(the_attribute, InstrumentedAttribute):
                # is a column
                if isinstance(the_attribute.property.columns[0].type, String):
                    max_length = the_attribute.property.columns[0].type.length
                    value = value[:max_length]

        super().__setattr__(key, value)

    @classmethod
    def get(cls, session, object_id):
        """
        Get object by object id, if not find, return None.
        """
        ret = None
        if hasattr(cls, 'id'):
            ret = session.query(cls).filter(
                cls.id == object_id
            ).first()

        return ret


def create_all_tables():
    from models.chat import User_A
    from models.chat import User_B
    from models.chat import Message
    BaseModel.metadata.create_all(bind=engine)


__all__ = [
    'BaseModel',
    'ModelMixin',
    'create_all_tables'
]

