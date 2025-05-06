from models.objects import AttributeList, identity


class Return():
    REQUIRED_ATTRIBUTES: AttributeList = [("isbn", identity, bool),
                                            ("customer_id", identity, bool)]
