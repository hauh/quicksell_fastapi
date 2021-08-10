"""Shop related database models."""

import enum

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import BigInteger, Enum, String, Text

from .base import ColumnUUID, LocationMixin, Model, foreign_key


class Shop(Model, LocationMixin):
	"""Shop model."""

	uuid = ColumnUUID()
	company_id = foreign_key('Company')

	name = Column(String, unique=True, nullable=False)
	description = Column(Text)
	phone = Column(String, nullable=False)
	photo = Column(String)

	company = relationship('Company', back_populates='shops', lazy=False)


class Company(Model):
	"""Company model."""

	class Form(enum.Enum):
		"""Company legal form."""

		SP = 0  # 'Sole Pro­pri­etorship'
		LLC = 1  # 'Lim­it­ed Lia­bil­i­ty Company'
		JSC = 2  # 'Joint-Stock Company'

	uuid = ColumnUUID()
	owner_id = foreign_key('User')

	name = Column(String, unique=True, nullable=False)
	form = Column(Enum(Form), nullable=False)
	tin = Column(BigInteger, unique=True, nullable=False)

	address = Column(String, nullable=False)
	phone = Column(String)
	email = Column(String)
	logo = Column(String)

	owner = relationship('User', back_populates='company')
	shops = relationship('Shop', back_populates='company', lazy=False)
