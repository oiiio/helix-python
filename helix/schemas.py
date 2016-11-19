import marshmallow
from marshmallow import fields


class EventSchema(marshmallow.Schema):
    event_type = fields.Str(load_from="eventType", required=True, allow_none=False)
    pacid = fields.Str(load_from="pacId", required=True, allow_none=False)
    sequence_num = fields.Int(load_from="sequenceNum", required=True, allow_none=False)
    timestamp = fields.DateTime(required=True, allow_none=False)


class CustomerInfoSchema(marshmallow.Schema):
    support_id = fields.Str(load_from="supportId", required=True, allow_none=False)
    first_name = fields.Str(load_from="firstName", required=True, allow_none=False)
    last_name = fields.Str(load_from="lastName", required=True, allow_none=False)
    email = fields.Email(required=True, allow_none=False)


class SampleStatusSchema(marshmallow.Schema):
    timestamp = fields.DateTime(required=True, allow_none=False)
    status = fields.Str(required=True, allow_none=False)


class CallSchema(marshmallow.Schema):
    callSetId = fields.Str()
    callSetName = fields.Str()
    genotype = fields.List(fields.Int())
    phaseset = fields.Str()
    genotypeLikelihood = fields.List(fields.Float)
    info = fields.Dict()


class VariantSchema(marshmallow.Schema):
    id = fields.Str()
    referenceName = fields.Str()
    start = fields.Int()
    end = fields.Int()
    referenceBases = fields.Str()
    alternateBases = fields.List(fields.Str())
    quality = fields.Number()
    variantSetId = fields.Str()

    filter = fields.List(fields.Str())
    calls = fields.Nested(CallSchema, many=True)
