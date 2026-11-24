from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


work_orders = Table('work_orders', metadata,
    Column('code', String(64), primary_key=True),
    Column('profile', String(160), ForeignKey('profiles.code'), nullable=False),
    Column('jig', String(160), ForeignKey('jigs.code'), nullable=False),
    Column('slot', String(160), nullable=False, unique=True),
    Column('quantity', Integer, nullable=False),
    Column('state', String(160), nullable=False),
    # 首片冷却弯度与签注预测的偏差（mm），首片签回时落账；重试不重复计数
    Column('first_bend', Float, nullable=True),
    Column('first_attempts', Integer, nullable=True),
    # 用首片偏差修正后的余片预测（mm）
    Column('revised_prediction', Float, nullable=True),
    # 修正预测加曲线留出 MAE 得到的行程上界（mm）
    Column('travel_bound', Float, nullable=True),
    # 余片开工当时的行程快照与放行依据
    Column('release_throw', Float, nullable=True),
    Column('release_basis', JSON, nullable=True),
    CheckConstraint('quantity between 1 and 20'),
    CheckConstraint("first_attempts is null or first_attempts >= 0"),
    CheckConstraint("first_bend is null or first_bend >= 0"),
)
