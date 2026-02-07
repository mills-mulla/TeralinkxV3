from django.db import models


class Voucher(models.Model):
    """Voucher tracking for time-based access"""
    username = models.CharField(max_length=255, unique=True, db_index=True)
    profile = models.CharField(max_length=255)
    duration_seconds = models.IntegerField(help_text="Voucher validity in seconds")
    activated_at = models.DateTimeField(null=True, blank=True, help_text="First login time")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Expiry time")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'vouchers'
    
    def __str__(self):
        return f"{self.username} - {self.profile}"
    
    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def remaining_seconds(self):
        if not self.expires_at:
            return self.duration_seconds
        from django.utils import timezone
        remaining = (self.expires_at - timezone.now()).total_seconds()
        return max(0, int(remaining))


class RadCheck(models.Model):
    """User credentials table"""
    id = models.AutoField(primary_key=True)
    username = models.TextField(default='')
    attribute = models.TextField(default='')
    op = models.CharField(max_length=2, default='==')
    value = models.TextField(default='')

    class Meta:
        db_table = 'radcheck'
        managed = False


class RadReply(models.Model):
    """User-specific reply attributes"""
    id = models.AutoField(primary_key=True)
    username = models.TextField(default='')
    attribute = models.TextField(default='')
    op = models.CharField(max_length=2, default='=')
    value = models.TextField(default='')

    class Meta:
        db_table = 'radreply'
        managed = False


class RadGroupCheck(models.Model):
    """Group check attributes (profile requirements)"""
    id = models.AutoField(primary_key=True)
    groupname = models.TextField(default='')
    attribute = models.TextField(default='')
    op = models.CharField(max_length=2, default='==')
    value = models.TextField(default='')

    class Meta:
        db_table = 'radgroupcheck'
        managed = False


class RadGroupReply(models.Model):
    """Group reply attributes (profile settings)"""
    id = models.AutoField(primary_key=True)
    groupname = models.TextField(default='')
    attribute = models.TextField(default='')
    op = models.CharField(max_length=2, default='=')
    value = models.TextField(default='')

    class Meta:
        db_table = 'radgroupreply'
        managed = False


class RadUserGroup(models.Model):
    """User to group assignment"""
    id = models.AutoField(primary_key=True)
    username = models.TextField(default='')
    groupname = models.TextField(default='')
    priority = models.IntegerField(default=0)

    class Meta:
        db_table = 'radusergroup'
        managed = False


class RadAcct(models.Model):
    """Accounting/session tracking table"""
    radacctid = models.BigAutoField(primary_key=True)
    acctsessionid = models.TextField()
    acctuniqueid = models.TextField(unique=True)
    username = models.TextField(null=True, blank=True)
    realm = models.TextField(null=True, blank=True)
    nasipaddress = models.GenericIPAddressField()
    nasportid = models.TextField(null=True, blank=True)
    nasporttype = models.TextField(null=True, blank=True)
    acctstarttime = models.DateTimeField(null=True, blank=True)
    acctupdatetime = models.DateTimeField(null=True, blank=True)
    acctstoptime = models.DateTimeField(null=True, blank=True)
    acctinterval = models.BigIntegerField(null=True, blank=True)
    acctsessiontime = models.BigIntegerField(null=True, blank=True)
    acctauthentic = models.TextField(null=True, blank=True)
    connectinfo_start = models.TextField(null=True, blank=True)
    connectinfo_stop = models.TextField(null=True, blank=True)
    acctinputoctets = models.BigIntegerField(null=True, blank=True)
    acctoutputoctets = models.BigIntegerField(null=True, blank=True)
    calledstationid = models.TextField(null=True, blank=True)
    callingstationid = models.TextField(null=True, blank=True)
    acctterminatecause = models.TextField(null=True, blank=True)
    servicetype = models.TextField(null=True, blank=True)
    framedprotocol = models.TextField(null=True, blank=True)
    framedipaddress = models.GenericIPAddressField(null=True, blank=True)
    framedipv6address = models.GenericIPAddressField(null=True, blank=True)
    framedipv6prefix = models.GenericIPAddressField(null=True, blank=True)
    framedinterfaceid = models.TextField(null=True, blank=True)
    delegatedipv6prefix = models.GenericIPAddressField(null=True, blank=True)
    class_field = models.TextField(null=True, blank=True, db_column='class')

    class Meta:
        db_table = 'radacct'
        managed = False


class RadPostAuth(models.Model):
    """Post-authentication logging table"""
    id = models.BigAutoField(primary_key=True)
    username = models.TextField()
    pass_field = models.TextField(null=True, blank=True, db_column='pass')
    reply = models.TextField(null=True, blank=True)
    calledstationid = models.TextField(null=True, blank=True)
    callingstationid = models.TextField(null=True, blank=True)
    authdate = models.DateTimeField(auto_now_add=True)
    class_field = models.TextField(null=True, blank=True, db_column='class')

    class Meta:
        db_table = 'radpostauth'
        managed = False


class Nas(models.Model):
    """NAS (Network Access Server) table - MikroTik routers"""
    id = models.AutoField(primary_key=True)
    nasname = models.TextField()
    shortname = models.TextField()
    type = models.TextField(default='other')
    ports = models.IntegerField(null=True, blank=True)
    secret = models.TextField()
    server = models.TextField(null=True, blank=True)
    community = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'nas'
        managed = False


class NasReload(models.Model):
    """NAS reload tracking table"""
    nasipaddress = models.GenericIPAddressField(primary_key=True)
    reloadtime = models.DateTimeField()

    class Meta:
        db_table = 'nasreload'
        managed = False
