with open('backend/app/models/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

models_code = """

class MonthlyRationList(Base):
    __tablename__ = "monthly_ration_lists"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, default="My Monthly Ration")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    items = relationship("MonthlyRationItem", back_populates="ration_list", cascade="all, delete-orphan", order_by="MonthlyRationItem.created_at")


class MonthlyRationItem(Base):
    __tablename__ = "monthly_ration_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    list_id = Column(String(36), ForeignKey("monthly_ration_lists.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(50), nullable=True)
    product_name_en = Column(String(150), nullable=False)
    product_name_hi = Column(String(150), nullable=True)
    unit = Column(String(50), nullable=False, default="1 kg")
    quantity = Column(Integer, nullable=False, default=1)
    notes = Column(String(255), nullable=True)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

    ration_list = relationship("MonthlyRationList", back_populates="items")
"""

if 'MonthlyRationList' not in content:
    content += models_code
    with open('backend/app/models/base.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('MonthlyRationList and MonthlyRationItem added to base.py')
else:
    print('Already present')
