from datetime import datetime

from sqlalchemy import Column, types, UniqueConstraint
from sqlalchemy.dialects.mssql import TINYINT

from .base import BaseModel, ModelMixin


class UserMessage(BaseModel, ModelMixin):

    """ 用户聊天表 """

    __tablename__ = 'user_message'

    TYPE_LAWER = 1  # 律师
    TYPE_PROPERTY = 2  # 物业
    TYPE_INDUSTRY = 3  # 业委会

    id = Column(types.BigInteger, primary_key=True)
    user_id = Column(types.Integer, nullable=False)
    from_type = Column(TINYINT, nullable=False, default='')
    from_name = Column(types.String(50), nullable=False, default='')
    from_token = Column(types.String(50), nullable=False, default='')

    to_type = Column(TINYINT, nullable=False, default='')
    to_user_id = Column(types.Integer, nullable=False)
    to_name = Column(types.String(50), nullable=False, default='')
    to_token = Column(types.String(50), nullable=False, default='')

    has_read = Column(types.Boolean, nullable=False, default=False)
    content = Column(types.String(100), nullable=False, default='')
    ticket = Column(types.JSON, nullable=False)
    created_at = Column(types.DateTime, nullable=False, default=datetime.now)
