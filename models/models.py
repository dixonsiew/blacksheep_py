from tortoise import fields, Model

class CityModel(Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=50)
    created_by = fields.IntField(null=True)
    created_date = fields.DatetimeField(auto_now_add=True)
    deleted = fields.BooleanField(default=False)
    deleted_by = fields.IntField(null=True)
    deleted_date = fields.DatetimeField(null=True)
    desc = fields.TextField(null=True)
    modified_by = fields.IntField(null=True)
    modified_date = fields.DatetimeField(auto_now=True)
    ref = fields.CharField(max_length=100, null=True)
    
    class Meta:
        table = "city"