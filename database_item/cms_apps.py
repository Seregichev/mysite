from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
gettext = lambda s: s

@apphook_pool.register  # register the application
class DataBaseItemApphook(CMSApp):
    app_name = 'database_item'
    name = gettext('Data Base Items')

    def get_urls(self, page=None, language=None, **kwargs):
        return ["database_item.urls"]