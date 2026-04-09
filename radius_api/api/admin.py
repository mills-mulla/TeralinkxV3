from django.contrib import admin
from .models import RadCheck, RadReply, RadGroupCheck, RadGroupReply, RadUserGroup, RadAcct, RadPostAuth, Nas, NasReload


@admin.register(RadCheck)
class RadCheckAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'attribute', 'op', 'value')
    list_filter = ('attribute',)
    search_fields = ('username', 'attribute')


@admin.register(RadReply)
class RadReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'attribute', 'op', 'value')
    list_filter = ('attribute',)
    search_fields = ('username', 'attribute')


@admin.register(RadGroupCheck)
class RadGroupCheckAdmin(admin.ModelAdmin):
    list_display = ('id', 'groupname', 'attribute', 'op', 'value')
    list_filter = ('groupname', 'attribute')
    search_fields = ('groupname', 'attribute')


@admin.register(RadGroupReply)
class RadGroupReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'groupname', 'attribute', 'op', 'value')
    list_filter = ('groupname', 'attribute')
    search_fields = ('groupname', 'attribute')


@admin.register(RadUserGroup)
class RadUserGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'groupname', 'priority')
    list_filter = ('groupname',)
    search_fields = ('username', 'groupname')


@admin.register(RadAcct)
class RadAcctAdmin(admin.ModelAdmin):
    list_display = ('radacctid', 'username', 'nasipaddress', 'acctstarttime', 'acctstoptime', 'acctinputoctets', 'acctoutputoctets')
    list_filter = ('nasipaddress', 'acctstarttime', 'acctstoptime')
    search_fields = ('username', 'acctuniqueid', 'acctsessionid')
    readonly_fields = ('radacctid', 'acctsessionid', 'acctuniqueid')


@admin.register(RadPostAuth)
class RadPostAuthAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'reply', 'authdate')
    list_filter = ('reply', 'authdate')
    search_fields = ('username',)
    readonly_fields = ('authdate',)


@admin.register(Nas)
class NasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nasname', 'shortname', 'type', 'secret')
    list_filter = ('type',)
    search_fields = ('nasname', 'shortname', 'description')


@admin.register(NasReload)
class NasReloadAdmin(admin.ModelAdmin):
    list_display = ('nasipaddress', 'reloadtime')
    readonly_fields = ('reloadtime',)
