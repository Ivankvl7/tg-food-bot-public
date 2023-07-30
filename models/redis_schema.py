from marshmallow import fields, Schema


class PriceRepresentationSchema(Schema):
    value = fields.Float()
    unit = fields.Str()


class CartItemSchema(Schema):
    product_name = fields.Str()
    category_name = fields.Str()
    description = fields.Str()
    price = fields.Nested(PriceRepresentationSchema)
    quantity = fields.Int()
    product_uuid = fields.Str()
    article = fields.Int()

